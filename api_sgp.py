from flask import Flask, request, jsonify
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def process_sgp_request():
    """
    Processa a requisição do SGP, independentemente da URL
    """
    try:
        data = {}
        
        if request.method == 'POST':
            # Receber dados via POST (JSON ou form data)
            if request.is_json:
                data = request.get_json()
            else:
                # Se for form data, converte para dict
                data = request.form.to_dict()
        else:
            # Receber dados via GET (query parameters)
            data = request.args.to_dict()

        # Mapear parâmetros do SGP para formato esperado
        mapped_data = {}
        if 'to' in data and 'number' not in data:
            mapped_data['number'] = data['to']
        if 'msg' in data and 'text' not in data:
            mapped_data['text'] = data['msg']
            
        # Mescla os dados mapeados com os originais
        # Dados originais têm prioridade, exceto para 'to'/'number' e 'msg'/'text'
        final_data = data.copy()
        final_data.update(mapped_data)
        
        data = final_data

        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        # Log para depuração
        app.logger.info(f"Dados recebidos do SGP ({request.method}): {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Verificar campo 'number' obrigatório
        if 'number' not in data:
            return jsonify({"error": "Campo 'number' (ou 'to') é obrigatório"}), 400

        # Obter URL da UAZAPI e token dinamicamente
        uazapi_url = data.get('uazapi_url') or data.get('uazapi_base_url') or "https://niochat.uazapi.com"
        instance_token = data.get('instance_token') or data.get('token')
        
        # Remover campos de configuração dos dados antes de enviar
        data.pop('uazapi_url', None)
        data.pop('uazapi_base_url', None)
        data.pop('instance_token', None)
        data.pop('token', None)

        # Determinar se é mensagem interativa
        # Critério: se tiver pelo menos uma das variáveis específicas do template
        is_interactive = any(key in data for key in ['cliente', 'valor', 'linhadigitavel', 'link_pix', 'provedor'])

        if is_interactive:
            response = send_interactive_message(data, uazapi_url, instance_token)
        else:
            # Se não for interativa, envia como texto simples
            # Verifica se 'text' ou 'msg' existem
            if 'text' not in data and 'msg' in data:
                data['text'] = data['msg']
            elif 'text' not in data and 'message' in data:
                 data['text'] = data['message']
            elif 'text' not in data:
                 data['text'] = "Mensagem recebida."

            response = send_text_message(data, uazapi_url, instance_token)
            
        return jsonify({
            "status": "success",
            "message": "Mensagem processada com sucesso",
            "uazapi_response": response
        }), 200
        
    except Exception as e:
        app.logger.error(f"Erro ao processar requisição: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def send_text_message(data, uazapi_url, instance_token):
    """
    Envia mensagem de texto para a UAZAPI
    """
    if not instance_token:
        return {"error": "Token da instância não fornecido"}

    # Verificar se existe a variável 'teste' para adicionar texto adicional
    texto_adicional = data.get('teste', '')
    texto_principal = data['text']
    
    # Se houver texto adicional, concatenar com o texto principal
    if texto_adicional:
        full_text = f"{texto_principal}\n\n{texto_adicional}"
    else:
        full_text = texto_principal

    payload = {
        "number": format_number(data['number']),
        "text": full_text
    }
    
    # Campos opcionais
    optional_fields = [
        'linkPreview', 'linkPreviewTitle', 'linkPreviewDescription', 
        'linkPreviewImage', 'linkPreviewLarge', 'replyid', 'mentions', 
        'readchat', 'readmessages', 'delay', 'forward'
    ]
    
    for field in optional_fields:
        if field in data:
            payload[field] = data[field]
    
    # Enviar para UAZAPI
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'token': instance_token
    }
    
    try:
        response = requests.post(
            f"{uazapi_url.rstrip('/')}/send/text",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # Log da resposta da UAZAPI
        app.logger.info(f"Resposta UAZAPI - Status: {response.status_code}, Body: {response.text}")
        
        if response.status_code == 401:
            return {"error": f"Não autorizado - verifique o token da instância"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Erro ao enviar para UAZAPI: {str(e)}")
        return {"error": str(e)}

def send_interactive_message(data, uazapi_url, instance_token):
    """
    Envia mensagem interativa com botões para a UAZAPI usando variáveis do SGP
    """
    if not instance_token:
        return {"error": "Token da instância não fornecido"}

    try:
        # Montar o texto da mensagem com os dados do SGP
        cliente = data.get('cliente', 'Cliente')
        valor = data.get('valor', '0,00')
        linhadigitavel = data.get('linhadigitavel', 'Não informado')
        link_pix = data.get('link_pix', 'Não informado')
        provedor = data.get('provedor', 'Não informado')
        texto_adicional = data.get('teste', '')  # Variável de texto adicional

        # Construir a mensagem principal
        message_lines = [
            f"Prezado(a) {cliente},",
            "",
            "Identificamos um título em aberto em seu nome. Seguem os dados para regularização:",
            "",
            f"Valor: R$ {valor}",
            f"Linha Digitável: {linhadigitavel}",
            f"Código PIX: {link_pix}",
            f"Beneficiário: {provedor}"
        ]
        
        # Adicionar texto adicional se existir
        if texto_adicional:
            message_lines.extend(["", texto_adicional])
        
        # Adicionar rodapé
        message_lines.extend([
            "",
            "Agradecemos pela pronta atenção e permanecemos à disposição para qualquer esclarecimento.",
            "",
            f"Atenciosamente,",
            f"Equipe {provedor}"
        ])
        
        message_text = "\n".join(message_lines)

        # Criar os botões
        choices = []
        if data.get('linhadigitavel') and data['linhadigitavel'] != 'Não informado':
            button_text = f"Copiar Linha Digitável"
            choices.append(f"{button_text}|copy:{data['linhadigitavel']}")
        if data.get('link_pix') and data['link_pix'] != 'Não informado':
            button_text = f"Copiar PIX"
            choices.append(f"{button_text}|copy:{data['link_pix']}")

        # Verifica se há pelo menos uma opção
        if not choices:
            # Se não houver dados para botões, envia como texto simples
            app.logger.warning("Nenhum dado para botões interativos encontrado. Enviando como mensagem de texto.")
            temp_data = data.copy()
            temp_data['text'] = message_text
            return send_text_message(temp_data, uazapi_url, instance_token)

        # Montar o payload
        payload = {
            "number": format_number(data['number']),
            "type": "button",
            "text": message_text,
            "choices": choices,
            "footerText": "Escolha uma das opções abaixo"
        }

        # Enviar para UAZAPI
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'token': instance_token
        }

        response = requests.post(
            f"{uazapi_url.rstrip('/')}/send/menu",
            json=payload,
            headers=headers,
            timeout=30
        )

        app.logger.info(f"Resposta UAZAPI - Status: {response.status_code}, Body: {response.text}")

        if response.status_code == 401:
            return {"error": f"Não autorizado - verifique o token da instância"}

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Erro ao enviar para UAZAPI: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
         app.logger.error(f"Erro ao montar mensagem interativa: {str(e)}")
         # Em caso de erro na montagem, envia como texto simples
         temp_data = data.copy()
         temp_data['text'] = message_text if 'message_text' in locals() else "Erro ao montar mensagem."
         return send_text_message(temp_data, uazapi_url, instance_token)


def format_number(number):
    """
    Formata o número para o padrão internacional (5511999999999)
    Remove duplicações de '55' no início e adiciona apenas um se necessário.
    """
    # Remove caracteres não numéricos
    cleaned = ''.join(filter(str.isdigit, str(number)))
    
    # Remove todos os '55' iniciais antes de adicionar um só
    while cleaned.startswith('55') and len(cleaned) > 2:
        cleaned = cleaned[2:]  # Remove os dois primeiros dígitos '55'
    
    # Adiciona '55' se não estiver no início
    if not cleaned.startswith('55'):
        cleaned = '55' + cleaned
    
    return cleaned

# --- ROTAS ---
@app.route('/webhook/sgp', methods=['POST', 'GET'])
def receive_from_sgp():
    """
    Endpoint para receber dados do SGP via POST ou GET
    """
    return process_sgp_request()

@app.route('/webhooks/evolution-uazapi/', methods=['POST', 'GET'])
def webhook_evolution_uazapi():
    """
    Endpoint alternativo para receber dados do SGP
    """
    return process_sgp_request()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({"status": "healthy", "message": "API SGP-UAZAPI está funcionando"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)