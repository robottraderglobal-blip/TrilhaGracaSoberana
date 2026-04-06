"""Modelo: PesquisaFonte — resultado de uma consulta ao NotebookLM."""
import hashlib
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, computed_field


# Tipo de origem da resposta — rastreia se veio ao vivo, do cache ou de fallback
FonteResposta = Literal["live", "cache", "fallback"]


class PesquisaFonte(BaseModel):
    """Uma consulta a uma fonte teológica via NotebookLM."""
    id: Optional[str] = None
    plano_id: str
    exegese_id: str
    fonte: str                          # sproul | nicodemus | spurgeon | lloyd_jones
    doutrina_nome: str
    query_enviada: str = ""
    resultado: str = ""
    key_insights: list[str] = []        # NOVO: insights extraídos pelo agente pesquisador
    relevance_score: int = 0            # NOVO: score 1-5 do agente pesquisador
    status: str = "pending"             # pending | em_andamento | concluido | erro | empty_response
    notebook_id: str = ""
    conversation_id: str = ""
    fonte_resposta: FonteResposta = "live"   # NOVO: live | cache | fallback
    tentativas: int = 0                      # NOVO: quantas tentativas foram necessárias
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @computed_field
    @property
    def cache_key(self) -> str:
        """Chave determinística para o cache: notebook + query normalizada."""
        raw = f"{self.notebook_id}:{self.query_enviada.strip().lower()}"
        return hashlib.md5(raw.encode()).hexdigest()

    @property
    def util_para_escritor(self) -> bool:
        """Indica se esta pesquisa tem conteúdo aproveitável pelo agente escritor."""
        return self.relevance_score >= 2 and bool(self.resultado.strip())

    def to_db_dict(self) -> dict:
        return {
            "plano_id": self.plano_id,
            "exegese_id": self.exegese_id,
            "fonte": self.fonte,
            "doutrina_nome": self.doutrina_nome,
            "query_enviada": self.query_enviada,
            "resultado": self.resultado,
            "key_insights": self.key_insights,
            "relevance_score": self.relevance_score,
            "status": self.status,
            "notebook_id": self.notebook_id,
            "conversation_id": self.conversation_id,
            "fonte_resposta": self.fonte_resposta,
            "tentativas": self.tentativas,
        }
