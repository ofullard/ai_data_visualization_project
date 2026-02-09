from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import certifi
import httpx
from dotenv import load_dotenv
from openai import OpenAI


@dataclass
class AiResponse:
    message: str
    created_at: str


def generate_ai_response(prompt: str) -> AiResponse:
    """Generate a ChatGPT response using OpenAI.

    Expects the API key in the OPENAI_API_KEY environment variable.
    """
    load_dotenv(Path(__file__).resolve().parent / ".env")
    timestamp = datetime.now().strftime("%H:%M:%S")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return AiResponse(
            message="OpenAI API key is missing. Set OPENAI_API_KEY to continue.",
            created_at=timestamp,
        )

    disable_ssl = os.getenv("OPENAI_DISABLE_SSL_VERIFY", "").lower() in {"1", "true", "yes"}
    ca_bundle = (
        os.getenv("OPENAI_CA_BUNDLE")
        or os.getenv("REQUESTS_CA_BUNDLE")
        or os.getenv("SSL_CERT_FILE")
    )
    if disable_ssl:
        verify_setting = False
    else:
        verify_setting = ca_bundle or certifi.where()

    client = OpenAI(
        api_key=api_key,
        http_client=httpx.Client(verify=verify_setting, timeout=30.0),
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for data insights.",
            },
            {"role": "user", "content": prompt.strip()},
        ],
        temperature=0.4,
        max_tokens=200,
    )

    content = response.choices[0].message.content or ""
    return AiResponse(message=content.strip(), created_at=timestamp)
