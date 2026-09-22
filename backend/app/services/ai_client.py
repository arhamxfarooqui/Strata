"""
Generic async HTTP client for OpenAI-compatible LLM APIs (Groq, DeepSeek, HuggingFace).
Replaces the Go CallOpenAICompatible function.
"""

import logging

import httpx

logger = logging.getLogger(__name__)


async def call_openai_compatible(
    url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    """
    Call any OpenAI-compatible chat completions endpoint.

    Args:
        url: Provider endpoint (e.g., https://api.groq.com/openai/v1/chat/completions)
        api_key: Bearer token
        model: Model identifier
        system_prompt: System message
        user_prompt: User message
        max_tokens: Max response tokens
        temperature: Sampling temperature

    Returns:
        The content string of the first choice.

    Raises:
        httpx.HTTPStatusError: On non-200 response
        ValueError: On empty/invalid response
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            logger.error(
                "AI Provider Error (%d): %s", response.status_code, response.text[:500]
            )
            raise httpx.HTTPStatusError(
                f"AI Provider Error ({response.status_code}): {response.text[:500]}",
                request=response.request,
                response=response,
            )

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("No response from AI provider")

        return choices[0]["message"]["content"]
