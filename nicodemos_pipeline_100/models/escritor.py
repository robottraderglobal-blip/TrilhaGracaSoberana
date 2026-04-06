"""Modelo: EscritorTrabalho — rascunho produzido pelo Agente Escritor Nicodemos."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class EscritorTrabalho(BaseModel):
    """Um rascunho de devocional produzido pelo Agente Escritor."""
    id: Optional[str] = None
    plano_id: str
    versao: int = 1                      # 1-3 (original + até 2 reescritas)
    conteudo_md: str = ""                # markdown completo
    palavras: int = 0
    status: str = "rascunho"             # rascunho | aprovado | reprovado
    feedback_revisor: str = ""
    modelo_llm: str = ""
    created_at: Optional[datetime] = None

    def contar_palavras(self) -> int:
        """Conta palavras no conteúdo markdown."""
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
            "versao": self.versao,
            "conteudo_md": self.conteudo_md,
            "palavras": self.palavras,
            "status": self.status,
            "modelo_llm": self.modelo_llm,
        }
