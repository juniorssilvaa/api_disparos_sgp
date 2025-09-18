# API Disparos SGP

API para integração entre o SGP (Sistema de Gestão de Provedores) e a UAZAPI para envio de mensagens via WhatsApp.

## Funcionalidades

- Recebe requisições do SGP via webhook
- Processa dados e envia mensagens via UAZAPI
- Suporta mensagens de texto simples e mensagens interativas com botões
- Formata números de telefone automaticamente

## Requisitos

- Python 3.7+
- Flask
- Requests

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/juniorssilvaa/api_disparos_sgp.git
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```
   python api_sgp.py
   ```

## Uso

A API expõe os seguintes endpoints:

- `POST /webhook/sgp` - Recebe dados do SGP
- `GET /webhook/sgp` - Recebe dados do SGP via query parameters
- `GET /health` - Verifica se a API está funcionando

## Configuração

A API aceita os seguintes parâmetros:

- `number` ou `to`: Número de telefone do destinatário (obrigatório)
- `text` ou `msg`: Texto da mensagem (obrigatório para mensagens simples)
- `uazapi_url` ou `uazapi_base_url`: URL da instância UAZAPI (opcional, padrão: https://niochat.uazapi.com)
- `instance_token` ou `token`: Token da instância UAZAPI (obrigatório)
- `cliente`, `valor`, `linhadigitavel`, `link_pix`, `provedor`: Parâmetros para mensagens interativas

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request