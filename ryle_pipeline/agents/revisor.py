"""
Agente Revisor — Avalia devocionais com rubrica de qualidade.
"""
from ..models.revisao import Revisao
from ..models.exegese import Exegese
from ..models.escritor import EscritorTrabalho
from .base import BaseAgent


class AgenteRevisor(BaseAgent):
    """Avalia devocionais contra rubrica e decide aprovação."""

    def __init__(self):
        super().__init__("revisor_system.md")

    def avaliar(
        self,
        trabalho: EscritorTrabalho,
        exegese: Exegese,
        ciclo: int,
    ) -> Revisao:
        """
        Avalia um rascunho de devocional.

        Args:
            trabalho: Rascunho do escritor
            exegese: Exegese que fundamenta o devocional
            ciclo: Número do ciclo de revisão (1-3)

        Returns:
            Revisao com scores e decisão
        """
        # Montar exegese resumida para o revisor
        doutrinas_resumo = "\n".join(
            f"- {d.nome}: {d.base_textual}" for d in exegese.doutrinas
        )

        prompt = (
            f"## Rascunho do Devocional (versão {trabalho.versao})\n"
            f"```\n{trabalho.conteudo_md}\n```\n\n"
            f"## Contagem: {trabalho.palavras} palavras\n\n"
            f"## Exegese de Referência\n"
            f"### Síntese\n{exegese.sintese}\n\n"
            f"### Doutrinas Extraídas\n{doutrinas_resumo}\n\n"
            f"### Aplicação\n"
            f"- Instrução: {exegese.aplicacao.instrucao}\n"
            f"- Correção: {exegese.aplicacao.correcao}\n\n"
            f"---\n"
            f"Avalie o rascunho conforme sua rubrica. "
            f"Este é o ciclo {ciclo} de revisão. "
            f"Responda em JSON válido."
        )

        try:
            data = self.call_llm_json(prompt)
        except Exception as e:
            import logging
            logging.getLogger("ryle_pipeline").warning(f"Revisor JSON parse falhou (ciclo {ciclo}): {e}")
            data = {
                "fidelidade_exegetica": 50,
                "extensao_adequada": 50,
                "estrutura_ryle": 50,
                "densidade_doutrinaria": 50,
                "clareza_pastoral": 50,
                "ausencia_antipadroes": 50,
                "aprovado": False,
                "pontos_fortes": "Erro de parse — avaliação automática indisponível.",
                "problemas_encontrados": f"Erro de parse do LLM: {str(e)[:200]}",
                "sugestoes_reescrita": "Reenviar para revisão no próximo ciclo.",
            }

        revisao = Revisao(
            plano_id=trabalho.plano_id,
            escritor_trabalho_id=trabalho.id or "",
            ciclo=ciclo,
            fidelidade_exegetica=data.get("fidelidade_exegetica", 0),
            extensao_adequada=data.get("extensao_adequada", 0),
            estrutura_ryle=data.get("estrutura_ryle", 0),
            densidade_doutrinaria=data.get("densidade_doutrinaria", 0),
            clareza_pastoral=data.get("clareza_pastoral", 0),
            ausencia_antipadroes=data.get("ausencia_antipadroes", 0),
            aprovado=data.get("aprovado", False),
            pontos_fortes=data.get("pontos_fortes", ""),
            problemas_encontrados=data.get("problemas_encontrados", ""),
            sugestoes_reescrita=data.get("sugestoes_reescrita", ""),
            modelo_llm=self.model,
        )
        revisao.calcular_score()
        # Forçar aprovação pelo score calculado (não confiar apenas no LLM)
        from .. import config as cfg
        aprovacao_padrao = revisao.score_total >= 90.0
        aprovacao_excecao = revisao.score_total >= 80.0 and ciclo >= 3
        revisao.aprovado = aprovacao_padrao or aprovacao_excecao

        return revisao
