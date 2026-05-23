"""
Agente Formatador de Hino — Estrutura letras em estrofes e coro.
"""
from .base import BaseAgent


class AgenteFormatadorHino(BaseAgent):
    """Organiza a letra de um hino com marcações claras de estrofes e refrão."""

    def __init__(self):
        super().__init__("hymn_formatter_system.md")

    def formatar(self, titulo: str, letra: str) -> str:
        """
        Formata a letra do hino estruturando-a em estrofes e refrão.

        Args:
            titulo: Título do hino (ex: "32 - O Deus fiel")
            letra: Letra crua e contínua do hino

        Returns:
            Letra organizada e formatada com marcadores
        """
        user_msg = f"HINO: {titulo}\nLETRA CRUA:\n{letra}"
        conteudo = self.call_llm(user_msg)
        return conteudo.strip()
