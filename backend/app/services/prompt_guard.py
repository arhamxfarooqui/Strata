"""
Prompt Guard — anti-cheat heuristic that flags "give me the answer" style prompts.
Logs flagged prompts and detects solution leakage in AI responses.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Regex patterns that indicate the user wants a direct answer
_DIRECT_ANSWER_PATTERNS = [
    re.compile(r"\bgive\s+me\s+(the\s+)?(code|solution|answer|implementation)\b", re.I),
    re.compile(r"\bsolve\s+(this|it)\s+(for\s+me|problem)\b", re.I),
    re.compile(r"\b(full|complete|entire)\s+(solution|code|implementation|program)\b", re.I),
    re.compile(r"\bwrite\s+(the\s+)?(code|solution|program|answer)\b", re.I),
    re.compile(r"\bjust\s+(give|show|tell)\s+me\b", re.I),
    re.compile(r"\bcopy[\s-]?paste\s+solution\b", re.I),
    re.compile(r"\bdo\s+(my|this)\s+(homework|assignment)\b", re.I),
    re.compile(r"\bwhat\s+is\s+the\s+(exact\s+)?(answer|output|result)\b", re.I),
]

# Pattern: prompt is just a URL with minimal context (likely pasting a problem)
_URL_ONLY_PATTERN = re.compile(
    r"^\s*(https?://\S+)\s*$", re.I
)

# Pattern: very short prompt with a problem link
_LAZY_PROMPT_PATTERN = re.compile(
    r"^(solve|help|do)\s+(https?://\S+)\s*$", re.I
)


def check_prompt(prompt: str) -> tuple[bool, str]:
    """
    Check if a prompt looks like a "give me the answer" request.

    Returns:
        (is_flagged, reason) — reason is empty string if not flagged.
    """
    # Check direct-answer patterns
    for pattern in _DIRECT_ANSWER_PATTERNS:
        if pattern.search(prompt):
            reason = f"Matched direct-answer pattern: {pattern.pattern}"
            logger.info("Prompt flagged: %s", reason)
            return True, reason

    # Check URL-only (just pasting a problem link)
    if _URL_ONLY_PATTERN.match(prompt):
        return True, "Prompt is just a URL with no question"

    # Check lazy prompt (one word + URL)
    if _LAZY_PROMPT_PATTERN.match(prompt):
        return True, "Prompt is a lazy command + URL"

    return False, ""


def check_response_for_solution_leak(response: str) -> bool:
    """
    Post-hoc check: does the AI response contain what looks like a complete code solution?
    Heuristic: a fenced code block with ≥ 8 lines of code.
    """
    # Find all fenced code blocks
    code_blocks = re.findall(r"```[\w]*\n(.*?)```", response, re.DOTALL)
    for block in code_blocks:
        lines = [line for line in block.strip().split("\n") if line.strip()]
        if len(lines) >= 8:
            return True
    return False


# Stricter system prompt injected when a prompt is flagged but still processed
FLAGGED_SYSTEM_SUFFIX = (
    "\n\nCRITICAL: The user appears to be asking for a direct solution. "
    "You MUST NOT provide any complete code or direct answers. "
    "Instead, ask guiding questions, identify the core concept, and give "
    "a conceptual nudge that helps them figure it out themselves."
)
