"""
AI Orchestrator — decomposes complex user queries into atomic sub-tasks
and routes each to a domain-specific handler.

Uses DeepSeek-Reasoner for the planning/decomposition step, then
MultiCall for each sub-task execution.
"""

import json
import logging
import re

from pydantic import BaseModel

from app.config import get_settings
from app.services.ai_client import call_openai_compatible

logger = logging.getLogger(__name__)
settings = get_settings()

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

ORCHESTRATOR_SYSTEM_PROMPT = """You are the Strata Routing Orchestrator — an internal AI planner, NOT a user-facing chatbot.

Your only job is to analyze the user's request and break it into 1-3 atomic sub-tasks that domain-specific sub-agents will execute.

STRICT RULES:
1. You MUST return ONLY raw JSON. No markdown, no backticks, no explanations outside JSON.
2. The JSON must exactly match this schema:
   {"sub_tasks":[{"description":"...","target_wing":"...","action_type":"..."}],"summary":"..."}
3. Valid target_wing values: "CP", "WebDev", "ML", "DSA", "Systems", "InfoSec"
4. Valid action_type values: "code_review", "concept_nudge", "routing", "analysis"
5. NEVER include full code solutions in sub-task descriptions.
6. For CP, DSA, or InfoSec: action_type must be "concept_nudge" — sub-agents will provide hints only.
7. Keep each sub-task description concise (1-2 sentences max).
8. summary must be one sentence describing the user's overall intent."""


class SubTask(BaseModel):
    description: str
    target_wing: str
    action_type: str


class OrchestratorPlan(BaseModel):
    sub_tasks: list[SubTask]
    summary: str


def _extract_json(raw: str) -> str:
    """Strip markdown wrappers and extract the JSON object from LLM output."""
    text = raw.strip()
    text = text.removeprefix("```json").removeprefix("```")
    text = text.removesuffix("```")
    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No valid JSON object found in response: {text[:200]}")
    return text[start : end + 1]


async def decompose_task(user_prompt: str, weak_concepts: str = "") -> OrchestratorPlan:
    """
    Use DeepSeek to decompose a user request into atomic sub-tasks.

    Args:
        user_prompt: The user's raw question
        weak_concepts: Pre-formatted Shadow Memory context string

    Returns:
        OrchestratorPlan with sub_tasks and summary
    """
    if weak_concepts:
        user_message = f"SHADOW MEMORY CONTEXT:\n{weak_concepts}\n\nUSER REQUEST:\n{user_prompt}"
    else:
        user_message = f"USER REQUEST:\n{user_prompt}"

    # Try DeepSeek first, fall back to Groq
    api_key = settings.DEEPSEEK_API_KEY
    url = DEEPSEEK_URL
    model = "deepseek-reasoner"

    if not api_key:
        api_key = settings.GROQ_API_KEY
        url = GROQ_URL
        model = "llama-3.3-70b-versatile"

    if not api_key:
        raise ValueError("No AI provider API keys configured for orchestrator")

    try:
        raw_text = await call_openai_compatible(
            url, api_key, model, ORCHESTRATOR_SYSTEM_PROMPT, user_message
        )
    except Exception as e:
        # Fallback to Groq if DeepSeek fails
        if url == DEEPSEEK_URL and settings.GROQ_API_KEY:
            logger.warning("Orchestrator: DeepSeek failed (%s), falling back to Groq", e)
            raw_text = await call_openai_compatible(
                GROQ_URL, settings.GROQ_API_KEY, "llama-3.3-70b-versatile",
                ORCHESTRATOR_SYSTEM_PROMPT, user_message,
            )
        else:
            raise

    # Sanitize response — strip <think> blocks from DeepSeek
    raw_text = re.sub(r"(?s)<think>.*?</think>\n*", "", raw_text).strip()

    json_str = _extract_json(raw_text)
    data = json.loads(json_str)

    plan = OrchestratorPlan(**data)
    if not plan.sub_tasks:
        raise ValueError("Orchestrator returned an empty sub_tasks array")

    return plan
