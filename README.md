# Analise-Conta-de-Luz
Encontra adulterações nas contas de luz 

# Piloto — Agente de Análise de Conta de Luz via Dify

## Objetivo

Este piloto valida a chamada de um agente Dify usando GPT-5.5 para analisar uma imagem de conta de luz hospedada em um link S3/presigned URL.

## Fluxo

1. O script lê as variáveis do `.env`
2. Envia o prompt para o app Dify
3. Anexa a imagem via `remote_url`
4. Recebe a resposta do agente
5. Imprime a análise no terminal

## Variáveis de ambiente

Criar um arquivo `.env` com base no `.env.example`:

```env
DIFY_API_KEY=
DIFY_BASE_URL=
S3_IMAGE_URL=
DIFY_USER_ID=
