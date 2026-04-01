"""Modelo: PesquisaFonte — resultado de uma consulta ao NotebookLM."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PesquisaFonte(BaseModel):
    """Uma consulta a uma fonte teológica via NotebookLM."""
    id: Optional[str] = None
    plano_id: str
    exegese_id: str
    fonte: str                          # sproul | nicodemus | spurgeon | lloyd_jones
    doutrina_nome: str
    query_enviada: str = ""
    resultado: str = ""
    status: str = "pending"             # pending | em_andamento | concluido | erro
    notebook_id: str = ""
    conversation_id: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_db_dict(self) -> dict:
        return {
            "plano_id": self.plano_id,
            "exegese_id": self.exegese_id,
            "fonte": self.fonte,
            "doutrina_nome": self.doutrina_nome,
            "query_enviada": self.query_enviada,
            "resultado": self.resultado,
            "status": self.status,
            "notebook_id": self.notebook_id,
            "conversation_id": self.conversation_id,
        }
