"""
Agente Narrador — Converte markdown para texto puro de narração.
"""
from ..models.narracao import DevocionalNarracao
from .base import BaseAgent


class AgenteNarrador(BaseAgent):
    """Converte devocional markdown em texto puro para narração/TTS."""

    def __init__(self):
        super().__init__("narrador_system.md")

    def converter(self, devocional_final: dict) -> DevocionalNarracao:
        """
        Converte devocional final em texto puro para narração.

        Args:
            devocional_final: Dados da tabela devocionais_final

        Returns:
            DevocionalNarracao pronto para TTS
        """
        prompt = (
            f"## Devocional para Converter\n"
            f"Título: {devocional_final['titulo']}\n"
            f"Texto bíblico: {devocional_final['texto_biblico']}\n\n"
            f"```markdown\n{devocional_final['conteudo_md']}\n```\n\n"
            f"Converta para texto puro de narração conforme suas instruções. "
            f"Responda em JSON válido."
        )

        try:
            data = self.call_llm_json(prompt)
        except Exception as e:
            import logging, re
            logging.getLogger("ryle_pipeline").warning(f"Narrador JSON parse falhou: {e}")
            # Fallback: limpar markdown manualmente
            raw = devocional_final.get("conteudo_md", "")
            texto_limpo = re.sub(r'[#*_`>\[\]()]', '', raw).strip()
            word_count = len(texto_limpo.split())
            data = {
                "texto_puro": texto_limpo,
                "palavras": word_count,
                "indicacoes_leitura": "",
            }

        return DevocionalNarracao(
            plano_id=devocional_final["plano_id"],
            devocional_final_id=devocional_final["id"],
            titulo=devocional_final["titulo"],
            texto_puro=data.get("texto_puro", ""),
            palavras=data.get("palavras", 0),
            indicacoes_leitura=data.get("indicacoes_leitura", ""),
            status="gerado",
        )
