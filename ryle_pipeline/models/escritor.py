"""Modelo: EscritorTrabalho — rascunho produzido pelo Agente Escritor."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class EscritorTrabalho(BaseModel):
    """Um rascunho de devocional produzido pelo Agente Escritor."""
    id: Optional[str] = None
    plano_id: str
    exegese_id: str
    versao: int = 1                      # 1-4 (original + até 3 reescritas)
    titulo: str = ""
    conteudo_md: str = ""                # markdown completo
    palavras: int = 0
    status: str = "rascunho"             # rascunho | enviado_revisao | reprovado | aprovado
    feedback_revisor: str = ""
    modelo_llm: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def contar_palavras(self) -> int:
        """Conta palavras no conteúdo markdown (ignora frontmatter)."""
        texto = self.conteudo_md
        # Remove frontmatter YAML se existir
        if texto.startswith("---"):
            parts = texto.split("---", 2)
            if len(parts) >= 3:
                texto = parts[2]
        return len(texto.split())

    def to_db_dict(self) -> dict:
        return {
            "plano_id": self.plano_id,
            "exegese_id": self.exegese_id,
            "versao": self.versao,
            "titulo": self.titulo,
            "conteudo_md": self.conteudo_md,
            "palavras": self.palavras,
            "status": self.status,
            "feedback_revisor": self.feedback_revisor,
            "modelo_llm": self.modelo_llm,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
        }
