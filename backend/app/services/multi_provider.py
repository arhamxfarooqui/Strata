"""
Multi-provider AI routing — routes requests to the optimal provider based on domain.
Includes automatic fallback logic between providers.
"""

import logging
import re

from app.config import get_settings
from app.services.ai_client import call_openai_compatible

logger = logging.getLogger(__name__)
settings = get_settings()

# Provider endpoints
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Routing table: domain → (provider, model, persona)
ROUTING_TABLE = {
    "cp": ("deepseek", "deepseek-reasoner", "Logic Engine (CodeSensei)"),
    "dev": ("groq", "qwen/qwen3-32b", "Architect (Dev Wing)"),
    "web": ("groq", "qwen/qwen3-32b", "Architect (Dev Wing)"),
    "ml": ("groq", "meta-llama/llama-4-scout-17b-16e-instruct", "Concept Lab (Scout)"),
    "dsa": ("deepseek", "deepseek-reasoner", "Structure Sensei"),
    "systems": ("groq", "qwen/qwen3-32b", "Systems Architect"),
    "infosec": ("groq", "llama-3.3-70b-versatile", "Red Team Analyst"),
}

DEFAULT_ROUTE = ("deepseek", "deepseek-reasoner", "Strata Core (DeepSeek)")


def _get_provider_config(domain: str) -> tuple[str, str, str]:
    """Get (provider, model, persona) for a domain."""
    return ROUTING_TABLE.get(domain.lower(), DEFAULT_ROUTE)


def _get_api_key(provider: str) -> str:
    """Get the API key for a provider."""
    if provider == "groq":
        return settings.GROQ_API_KEY
    elif provider == "deepseek":
        return settings.DEEPSEEK_API_KEY
    return ""


def _get_url(provider: str) -> str:
    """Get the API URL for a provider."""
    if provider == "groq":
        return GROQ_URL
    elif provider == "deepseek":
        return DEEPSEEK_URL
    return GROQ_URL


def sanitize_response(text: str) -> str:
    """Strip <think>...</think> blocks from DeepSeek responses."""
    return re.sub(r"(?s)<think>.*?</think>\n*", "", text).strip()


async def multi_call(
    domain: str, prompt: str, system_prompt: str
) -> tuple[str, str]:
    """
    Route an AI request to the appropriate provider based on domain.
    Returns (response_text, persona_name).

    Fallback logic:
      1. Try primary provider for the domain
      2. If key is missing, try whichever key exists
      3. If primary fails, try the other provider
      4. Append "(Fallback)" to persona if fallback was used
    """
    provider, model, persona = _get_provider_config(domain)
    api_key = _get_api_key(provider)

    # If primary key is missing, try fallback key
    if not api_key:
        if settings.GROQ_API_KEY:
            provider, model = "groq", "llama-3.3-70b-versatile"
            api_key = settings.GROQ_API_KEY
        elif settings.DEEPSEEK_API_KEY:
            provider, model = "deepseek", "deepseek-reasoner"
            api_key = settings.DEEPSEEK_API_KEY
        else:
            raise ValueError("No AI provider API keys configured")

    url = _get_url(provider)

    try:
        response = await call_openai_compatible(url, api_key, model, system_prompt, prompt)
        return sanitize_response(response), persona
    except Exception as primary_err:
        logger.warning("Provider %s failed (%s). Attempting fallback...", provider, primary_err)

        # Fallback to the other provider
        if provider == "deepseek" and settings.GROQ_API_KEY:
            try:
                response = await call_openai_compatible(
                    GROQ_URL, settings.GROQ_API_KEY, "llama-3.3-70b-versatile",
                    system_prompt, prompt,
                )
                return sanitize_response(response), f"{persona} (Groq Fallback)"
            except Exception:
                pass
        elif provider == "groq" and settings.DEEPSEEK_API_KEY:
            try:
                response = await call_openai_compatible(
                    DEEPSEEK_URL, settings.DEEPSEEK_API_KEY, "deepseek-reasoner",
                    system_prompt, prompt,
                )
                return sanitize_response(response), f"{persona} (DeepSeek Fallback)"
            except Exception:
                pass

        raise primary_err
