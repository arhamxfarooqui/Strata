"""
Roadmap generation service — 12-week personalized technical roadmap via AI.
"""

import logging
import re

from app.config import get_settings
from app.services.ai_client import call_openai_compatible

logger = logging.getLogger(__name__)
settings = get_settings()

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

ROADMAP_SYSTEM_PROMPT = (
    "You are the Strata Roadmap Generator. Analyze the user's current stats and "
    "Shadow Memory to output a strictly valid JSON roadmap. "
    "Output strictly valid JSON only. No markdown formatting, no explanatory text."
)


async def generate_roadmap(
    cf_rating: int,
    total_solved: int,
    wings: list[str],
    top_languages: list[str],
) -> str:
    """Generate a 12-week roadmap. Returns raw JSON string."""
    user_prompt = f"""
Generate a rigorous **12-week Technical Roadmap** for a student with these stats:
- Codeforces Rating: {cf_rating} (Total Solved: {total_solved})
- Interested Wings: {wings}
- Top Languages: {', '.join(top_languages) if top_languages else 'C++, Python'}

The roadmap must be divided into 3 Phases (4 weeks each).

REQUIRED JSON STRUCTURE:
{{
  "current_level": "Beginner/Intermediate/Advanced",
  "summary": "Brief analysis of their technical profile.",
  "phases": [
    {{
      "phase_name": "Phase 1: [Name] (Weeks 1-4)",
      "goal": "Specific goal",
      "weeks": [
        {{
          "week": 1,
          "theme": "Graph Theory / Frontend / ML Basics",
          "goals": ["Goal 1", "Goal 2"],
          "resources": [
             {{"title": "Resource Title", "url": "https://..."}}
          ],
          "tips": "Context-specific advice."
        }}
      ]
    }}
  ]
}}
"""

    # Try DeepSeek first
    api_key = settings.DEEPSEEK_API_KEY
    url = DEEPSEEK_URL
    model = "deepseek-reasoner"

    if not api_key and settings.GROQ_API_KEY:
        api_key = settings.GROQ_API_KEY
        url = GROQ_URL
        model = "llama-3.3-70b-versatile"

    try:
        response = await call_openai_compatible(
            url, api_key, model, ROADMAP_SYSTEM_PROMPT, user_prompt
        )
    except Exception as e:
        if url == DEEPSEEK_URL and settings.GROQ_API_KEY:
            logger.warning("Roadmap: DeepSeek failed (%s), falling back to Groq", e)
            response = await call_openai_compatible(
                GROQ_URL, settings.GROQ_API_KEY, "llama-3.3-70b-versatile",
                ROADMAP_SYSTEM_PROMPT, user_prompt,
            )
        else:
            raise

    # Strip <think> blocks and extract JSON
    response = re.sub(r"(?s)<think>.*?</think>\n*", "", response).strip()
    start = response.find("{")
    end = response.rfind("}")
    if start != -1 and end != -1 and end > start:
        response = response[start : end + 1]

    return response
