"""Modelo: DevocionalFinal — devocional aprovado para publicação."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class DevocionalFinal(BaseModel):
    """Devocional aprovado e pronto para publicação."""
    id: Optional[str] = None
    plano_id: str
    titulo: str
    texto_biblico: str
    subtema: str = ""
    tema_semana: str = ""
    tema_mes: str = ""
    conteudo_md: str
    palavras: int
    exegese_id: Optional[str] = None
    escritor_trabalho_id: Optional[str] = None
    revisao_final_id: Optional[str] = None
    versao_aprovada: int = 1
    score_final: float = 0.0
    status: str = "aprovado"             # aprovado | publicado
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_db_dict(self) -> dict:
        return {
            "plano_id": self.plano_id,
            "titulo": self.titulo,
            "texto_biblico": self.texto_biblico,
            "subtema": self.subtema,
            "tema_semana": self.tema_semana,
            "tema_mes": self.tema_mes,
            "conteudo_md": self.conteudo_md,
            "palavras": self.palavras,
            "exegese_id": self.exegese_id,
            "escritor_trabalho_id": self.escritor_trabalho_id,
            "revisao_final_id": self.revisao_final_id,
            "versao_aprovada": self.versao_aprovada,
            "score_final": self.score_final,
            "status": self.status,
        }
