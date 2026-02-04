from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

from openai import OpenAI


@dataclass
class AiResponse:
    message: str
    created_at: str


def generate_ai_response(prompt: str) -> AiResponse:
    """Generate a ChatGPT response using OpenAI.

    Expects the API key in the OPENAI_API_KEY environment variable.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return AiResponse(
            message="OpenAI API key is missing. Set OPENAI_API_KEY to continue.",
            created_at=timestamp,
        )

    client = OpenAI(api_key=api_key)
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
