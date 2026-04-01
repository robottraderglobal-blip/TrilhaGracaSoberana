"""Ryle Pipeline — Agentes."""
from .base import BaseAgent
from .exegeta import AgenteExegeta
from .escritor import AgenteEscritor
from .revisor import AgenteRevisor
from .narrador import AgenteNarrador

__all__ = [
    "BaseAgent",
    "AgenteExegeta",
    "AgenteEscritor",
    "AgenteRevisor",
    "AgenteNarrador",
]
