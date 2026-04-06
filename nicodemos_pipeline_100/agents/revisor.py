"""
Agente Revisor — Avalia devocionais no estilo Augustus Nicodemus.
"""
import re
from ..models.revisao import Revisao
from ..models.escritor import EscritorTrabalho
from .base import BaseAgent


class AgenteRevisor(BaseAgent):
    """Avalia devocionais contra rubrica do estilo Augustus Nicodemus."""

    def __init__(self):
        super().__init__("revisor_system.md")

    def avaliar(self, trabalho: EscritorTrabalho, plano: dict, ciclo: int) -> Revisao:
        """
        Avalia um rascunho de devocional.

        Args:
            trabalho: Rascunho do escritor
            plano: Dados do plano (ref + versículo)
            ciclo: Número do ciclo de revisão (1-2)

        Returns:
            Revisao com scores e decisão
        """
        user_msg = (
            f"DIA: {plano['dia']}\n"
            f"VERSÍCULO: {plano['ref']} — {plano['versiculo']}\n"
            f"DEVOCIONAL GERADA:\n{trabalho.conteudo_md}\n\n"
            f"---\n"
            f"Este é o ciclo {ciclo} de revisão. "
            f"Avalie conforme sua rubrica e responda em JSON válido com os campos:\n"
            f"- conformidade_estrutural (0-100)\n"
            f"- estilo_nicodemos (0-100)\n"
            f"- conformidade_teologica (0-100)\n"
            f"- qualidade_literaria (0-100)\n"
            f"- extensao_adequada (0-100)\n"
            f"- aprovado (true/false)\n"
            f"- pontos_fortes (string)\n"
            f"- problemas_encontrados (string)\n"
            f"- sugestoes_reescrita (string)\n"
            f"- texto_corrigido (string — texto final com correções inline, se aplicável)"
        )

        try:
            data = self.call_llm_json(user_msg)
        except Exception as e:
            import logging
            logging.getLogger("nicodemos_pipeline").warning(
                f"Revisor JSON parse falhou (ciclo {ciclo}): {e}"
            )
            data = {
                "conformidade_estrutural": 50,
                "estilo_nicodemos": 50,
                "conformidade_teologica": 50,
                "qualidade_literaria": 50,
                "extensao_adequada": 50,
                "aprovado": False,
                "pontos_fortes": "Erro de parse — avaliação automática indisponível.",
                "problemas_encontrados": f"Erro de parse do LLM: {str(e)[:200]}",
                "sugestoes_reescrita": "Reenviar para revisão no próximo ciclo.",
                "texto_corrigido": "",
            }

        revisao = Revisao(
            plano_id=trabalho.plano_id,
            escritor_trabalho_id=trabalho.id or "",
            ciclo=ciclo,
            conformidade_estrutural=int(data.get("conformidade_estrutural", 0)),
            estilo_nicodemos=int(data.get("estilo_nicodemos", 0)),
            conformidade_teologica=int(data.get("conformidade_teologica", 0)),
            qualidade_literaria=int(data.get("qualidade_literaria", 0)),
            extensao_adequada=int(data.get("extensao_adequada", 0)),
            aprovado=data.get("aprovado", False),
            pontos_fortes=str(data.get("pontos_fortes", "")),
            problemas_encontrados=str(data.get("problemas_encontrados", "")),
            sugestoes_reescrita=str(data.get("sugestoes_reescrita", "")),
            texto_corrigido=str(data.get("texto_corrigido", "")),
            modelo_llm=self.model,
        )
        revisao.calcular_score()

        # Forçar aprovação pelo score calculado
        from .. import config as cfg
        aprovacao_padrao = revisao.score_total >= 90.0
        aprovacao_excecao = revisao.score_total >= cfg.SCORE_MINIMO_APROVACAO and ciclo >= cfg.MAX_CICLOS_REVISAO
        revisao.aprovado = aprovacao_padrao or aprovacao_excecao

        return revisao

    def extrair_texto_final(self, revisao: Revisao, devocional_original: str) -> str:
        """Retorna o melhor texto disponível: corrigido pelo revisor ou original."""
        if revisao.texto_corrigido and len(revisao.texto_corrigido) > 100:
            return revisao.texto_corrigido
        return devocional_original
