from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class AiResponse:
    message: str
    created_at: str


def generate_ai_response(prompt: str) -> AiResponse:
    """Return a lightweight AI-style response.

    Replace this with a real LLM integration when ready.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    summary = (
        "Here is a quick AI insight based on your message: "
        f"{prompt.strip()}"
    )
    return AiResponse(message=summary, created_at=timestamp)
