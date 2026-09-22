"""Tests for domain routing logic."""

import pytest
from app.services.domain_handlers import get_handler, DOMAIN_HANDLERS
from app.services.multi_provider import _get_provider_config, ROUTING_TABLE


class TestDomainRouting:
    """Tests that queries route to the correct domain handler."""

    def test_all_six_domains_registered(self):
        """Verify all 6 required domains have handlers."""
        required = {"CP", "WebDev", "ML", "DSA", "Systems", "InfoSec"}
        registered = set(DOMAIN_HANDLERS.keys())
        assert required.issubset(registered), f"Missing: {required - registered}"

    def test_cp_routes_to_deepseek(self):
        provider, model, persona = _get_provider_config("cp")
        assert provider == "deepseek"
        assert "CodeSensei" in persona

    def test_dev_routes_to_groq(self):
        provider, model, persona = _get_provider_config("dev")
        assert provider == "groq"
        assert "Architect" in persona

    def test_ml_routes_to_groq_scout(self):
        provider, model, persona = _get_provider_config("ml")
        assert provider == "groq"
        assert "Scout" in persona

    def test_dsa_routes_to_deepseek(self):
        provider, model, persona = _get_provider_config("dsa")
        assert provider == "deepseek"
        assert "Structure Sensei" in persona

    def test_systems_routes_to_groq(self):
        provider, model, persona = _get_provider_config("systems")
        assert provider == "groq"
        assert "Systems" in persona

    def test_infosec_routes_to_groq(self):
        provider, model, persona = _get_provider_config("infosec")
        assert provider == "groq"
        assert "Red Team" in persona

    def test_unknown_domain_falls_back(self):
        provider, model, persona = _get_provider_config("unknown_domain")
        assert provider in ("deepseek", "groq")  # Falls back to default

    def test_handler_has_system_prompt(self):
        """Every handler must have a non-empty system prompt."""
        for key, handler in DOMAIN_HANDLERS.items():
            assert handler.system_prompt, f"Handler {key} has empty system_prompt"
            assert len(handler.system_prompt) > 50, f"Handler {key} system_prompt too short"

    def test_handler_has_persona(self):
        """Every handler must have a persona name."""
        for key, handler in DOMAIN_HANDLERS.items():
            assert handler.persona, f"Handler {key} has empty persona"

    def test_cp_handler_refuses_noncp(self):
        """CP handler system prompt should mention refusing off-topic."""
        handler = get_handler("CP")
        assert "decline" in handler.system_prompt.lower() or "refuse" in handler.system_prompt.lower()

    def test_dev_handler_refuses_nondev(self):
        """Dev handler system prompt should mention refusing off-topic."""
        handler = get_handler("Dev")
        assert "refuse" in handler.system_prompt.lower() or "redirect" in handler.system_prompt.lower()
