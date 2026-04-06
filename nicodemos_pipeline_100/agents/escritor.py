"""
Agente Escritor — Produz devocionais no estilo Augustus Nicodemus.
"""
import re
from ..models.escritor import EscritorTrabalho
from .base import BaseAgent


class AgenteEscritor(BaseAgent):
    """Produz devocionais no estilo de Augustus Nicodemus para culto doméstico."""

    def __init__(self):
        super().__init__("escritor_system.md")

    def escrever(self, plano: dict) -> EscritorTrabalho:
        """
        Escreve a devocional a partir do plano.

        Args:
            plano: Dados do nico_plano (dict do Supabase)

        Returns:
            EscritorTrabalho com o rascunho da devocional
        """
        user_msg = f"DIA: {plano['dia']}\nVERSÍCULO: {plano['ref']} — {plano['versiculo']}"

        conteudo = self.call_llm(user_msg)

        # Limpar marcador de contagem (o SKILL pede isso mas não queremos no output final)
        conteudo = re.sub(r'\[Contagem:\s*\d+\s*palavras?\]', '', conteudo).strip()

        trabalho = EscritorTrabalho(
            plano_id=plano["id"],
            versao=1,
            conteudo_md=conteudo,
            status="rascunho",
            modelo_llm=self.model,
        )
        trabalho.palavras = trabalho.contar_palavras()
        return trabalho

    def reescrever(self, trabalho_anterior: EscritorTrabalho, feedback: str, plano: dict) -> EscritorTrabalho:
        """
        Reescreve a devocional incorporando o feedback do revisor.

        Args:
            trabalho_anterior: Rascunho reprovado
            feedback: Feedback detalhado do revisor
            plano: Dados do plano

        Returns:
            Novo EscritorTrabalho com versão incrementada
        """
        user_msg = (
            f"DIA: {plano['dia']}\n"
            f"VERSÍCULO: {plano['ref']} — {plano['versiculo']}\n\n"
            f"## Rascunho Anterior (REPROVADO)\n"
            f"```\n{trabalho_anterior.conteudo_md}\n```\n\n"
            f"## Feedback do Revisor\n{feedback}\n\n"
            f"---\n"
            f"Reescreva a devocional corrigindo TODOS os problemas apontados. "
            f"Mantenha o que estava bom. Retorne APENAS a devocional completa."
        )

        conteudo = self.call_llm(user_msg)
        conteudo = re.sub(r'\[Contagem:\s*\d+\s*palavras?\]', '', conteudo).strip()

        novo = EscritorTrabalho(
            plano_id=trabalho_anterior.plano_id,
            versao=trabalho_anterior.versao + 1,
            conteudo_md=conteudo,
            status="rascunho",
            modelo_llm=self.model,
        )
        novo.palavras = novo.contar_palavras()
        return novo
