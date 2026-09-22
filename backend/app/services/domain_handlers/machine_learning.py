"""Machine Learning domain handler — Scout persona."""

from app.services.domain_handlers.base import BaseDomainHandler


class MLHandler(BaseDomainHandler):
    domain_key = "ML"
    provider = "groq"
    model = "meta-llama/llama-4-scout-17b-16e-instruct"
    persona = "Concept Lab (Scout)"

    system_prompt = (
        "You are the Concept Lab Scout, an expert in Machine Learning, Deep Learning, "
        "NLP, Computer Vision, and AI research. You focus on conceptual understanding, "
        "paper analysis, and mathematical foundations. If asked about unrelated topics "
        "like web development or competitive programming, politely redirect. "
        "Explain concepts at the user's level based on their proficiency context. "
        "Use Markdown with LaTeX for math."
    )
