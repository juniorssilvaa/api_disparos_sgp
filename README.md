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

A API pode ser configurada através de variáveis de ambiente ou parâmetros na requisição.

### Variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

- `UAZAPI_BASE_URL`: URL da instância UAZAPI (opcional, padrão: https://niochat.uazapi.com)
- `INSTANCE_TOKEN`: Token da instância UAZAPI (obrigatório para envio de mensagens)
- `PORT`: Porta da aplicação (opcional, padrão: 5000)
- `HOST`: Host da aplicação (opcional, padrão: 0.0.0.0)

### Parâmetros da API

A API aceita os seguintes parâmetros nas requisições:

- `number` ou `to`: Número de telefone do destinatário (obrigatório)
- `text` ou `msg`: Texto da mensagem (obrigatório para mensagens simples)
- `uazapi_url` ou `uazapi_base_url`: URL da instância UAZAPI (opcional, sobrescreve variável de ambiente)
- `instance_token` ou `token`: Token da instância UAZAPI (obrigatório, sobrescreve variável de ambiente)
- `cliente`, `valor`, `linhadigitavel`, `link_pix`, `provedor`: Parâmetros para mensagens interativas

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request