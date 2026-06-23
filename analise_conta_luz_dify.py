import json
from urllib.parse import urlparse
import os
import requests

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")
DIFY_API_KEY = os.getenv("DIFY_API_KEY")

PROMPT = "Analise essa conta de luz de acordo com a metodologia explicitada"

def validate_image_url(image_url: str) -> None:
    parsed = urlparse(image_url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("A URL da imagem precisa começar com http:// ou https://.")

    if not parsed.netloc:
        raise ValueError("URL inválida: domínio ausente.")

    # Presigned URLs do S3 geralmente têm query params e nem sempre terminam com .png.
    # Por isso, não valido pela extensão do arquivo.

def call_dify_agent_with_s3_png(
    image_url: str,
    user_id: str = "analise-conta-luz-user",
    conversation_id: str = "",
) -> str:
    if not DIFY_API_KEY:
        raise RuntimeError(
            "Defina a variável de ambiente DIFY_API_KEY antes de rodar o script."
        )

    validate_image_url(image_url)

    url = f"{DIFY_BASE_URL.rstrip('/')}/chat-messages"

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": {},
        "query": PROMPT,
        "response_mode": "streaming",
        "conversation_id": conversation_id,
        "user": user_id,
        "files": [
            {
                "type": "image",
                "transfer_method": "remote_url",
                "url": image_url,
            }
        ],
        "auto_generate_name": True,
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        stream=True,
        timeout=(10, 300),
    )

    print(f"HTTP {response.status_code}")

    if response.status_code >= 400:
        print(response.text)
        response.raise_for_status()

    full_answer = []
    returned_conversation_id = None

    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue

        # Dify em streaming retorna Server-Sent Events no formato:
        # data: {"event": "...", "answer": "..."}
        if not line.startswith("data:"):
            continue

        raw_data = line.removeprefix("data:").strip()

        if raw_data == "[DONE]":
            break

        try:
            event = json.loads(raw_data)
        except json.JSONDecodeError:
            continue

        event_type = event.get("event")

        if event.get("conversation_id"):
            returned_conversation_id = event["conversation_id"]

        if event_type in ("message", "agent_message"):
            answer_piece = event.get("answer", "")
            if answer_piece:
                print(answer_piece, end="", flush=True)
                full_answer.append(answer_piece)

        elif event_type == "message_end":
            print("\n\n---")
            print("Mensagem finalizada.")

        elif event_type == "error":
            raise RuntimeError(f"Erro retornado pelo Dify: {event}")

    if returned_conversation_id:
        print(f"\nconversation_id: {returned_conversation_id}")

    return "".join(full_answer)


load_dotenv()

if __name__ == "__main__":
    s3_image_url = os.getenv("S3_IMAGE_URL")

    if not s3_image_url:
        raise RuntimeError(
            "S3_IMAGE_URL não encontrada no arquivo .env"
        )

    call_dify_agent_with_s3_png(
        image_url=s3_image_url,
        user_id="integrador-123",
        conversation_id="",
    )
    
