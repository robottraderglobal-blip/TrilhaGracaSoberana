"""Modelo: DevocionalFinal — devocional aprovada para publicação no culto doméstico."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class DevocionalFinal(BaseModel):
    """Devocional aprovada e pronta para publicação."""
    id: Optional[str] = None
    plano_id: str
    ref: str                             # Referência bíblica (ex: "Salmos 100.4")
    versiculo: str                       # Texto completo do versículo (ARA)
    conteudo_md: str                     # Markdown completo da devocional
    pergunta_reflexao: str = ""          # Pergunta para o culto doméstico
    palavras: int = 0
    semana: int = 0
    dia: int = 0
    escritor_trabalho_id: Optional[str] = None
    revisao_final_id: Optional[str] = None
    versao_aprovada: int = 1
    score_final: float = 0.0
    status: str = "aprovado"             # aprovado | publicado
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def to_db_dict(self) -> dict:
        return {
            "plano_id": self.plano_id,
            "ref": self.ref,
            "versiculo": self.versiculo,
            "conteudo_md": self.conteudo_md,
            "pergunta_reflexao": self.pergunta_reflexao,
            "palavras": self.palavras,
            "semana": self.semana,
            "dia": self.dia,
            "escritor_trabalho_id": self.escritor_trabalho_id,
            "revisao_final_id": self.revisao_final_id,
            "versao_aprovada": self.versao_aprovada,
            "score_final": self.score_final,
        }
