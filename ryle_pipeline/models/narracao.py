"""Modelo: DevocionalNarracao — texto puro pronto para TTS/narração."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class DevocionalNarracao(BaseModel):
    """Versão do devocional limpa de formatação, pronta para narração."""
    id: Optional[str] = None
    plano_id: str
    devocional_final_id: str
    titulo: str
    texto_puro: str                      # sem markdown, pronto para TTS
    palavras: int
    indicacoes_leitura: str = ""         # pausas, ênfases, tom
    status: str = "pending"              # pending | gerado | revisado | pronto
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_db_dict(self) -> dict:
        return {
            "plano_id": self.plano_id,
            "devocional_final_id": self.devocional_final_id,
            "titulo": self.titulo,
            "texto_puro": self.texto_puro,
            "palavras": self.palavras,
            "indicacoes_leitura": self.indicacoes_leitura,
            "status": self.status,
        }
