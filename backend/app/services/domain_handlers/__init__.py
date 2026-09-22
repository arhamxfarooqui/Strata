from app.services.domain_handlers.base import BaseDomainHandler
from app.services.domain_handlers.competitive_programming import CPHandler
from app.services.domain_handlers.web_dev import WebDevHandler
from app.services.domain_handlers.machine_learning import MLHandler
from app.services.domain_handlers.dsa import DSAHandler
from app.services.domain_handlers.systems import SystemsHandler
from app.services.domain_handlers.infosec import InfoSecHandler

DOMAIN_HANDLERS: dict[str, BaseDomainHandler] = {
    "CP": CPHandler(),
    "WebDev": WebDevHandler(),
    "Web": WebDevHandler(),
    "Dev": WebDevHandler(),
    "ML": MLHandler(),
    "DSA": DSAHandler(),
    "Systems": SystemsHandler(),
    "InfoSec": InfoSecHandler(),
}


def get_handler(domain: str) -> BaseDomainHandler:
    """Get the domain handler for a given domain key."""
    return DOMAIN_HANDLERS.get(domain, CPHandler())


__all__ = ["DOMAIN_HANDLERS", "get_handler", "BaseDomainHandler"]
