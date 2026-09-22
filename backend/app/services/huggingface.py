"""
HuggingFace Inference API client — preserved from Go huggingface.go.
"""

import logging

from app.config import get_settings
from app.services.ai_client import call_openai_compatible

logger = logging.getLogger(__name__)
settings = get_settings()

HF_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"


async def chat_with_coach_hf(system_context: str, user_query: str) -> str:
    """Chat via HuggingFace Inference API."""
    if not settings.HF_TOKEN:
        raise ValueError("HF_TOKEN is not set")
    return await call_openai_compatible(
        HF_API_URL, settings.HF_TOKEN, HF_MODEL, system_context, user_query,
        max_tokens=1024, temperature=0.7,
    )


async def sub_agent_call_hf(system_prompt: str, task_description: str) -> str:
    """Execute a sub-agent task via HuggingFace."""
    if not settings.HF_TOKEN:
        raise ValueError("HF_TOKEN is not set")
    return await call_openai_compatible(
        HF_API_URL, settings.HF_TOKEN, HF_MODEL, system_prompt, task_description,
        max_tokens=512, temperature=0.4,
    )
