"""Modelo: Revisao — crítica produzida pelo Agente Revisor."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Revisao(BaseModel):
    """Uma avaliação de um rascunho de devocional."""
    id: Optional[str] = None
    plano_id: str
    escritor_trabalho_id: str
    ciclo: int = Field(..., ge=1, le=3)

    # Scores individuais (0-100)
    fidelidade_exegetica: int = 0       # 30% — base na exegese
    extensao_adequada: int = 0          # 15% — 800-1200 palavras
    estrutura_ryle: int = 0             # 15% — 3 pontos, abertura, etc.
    densidade_doutrinaria: int = 0      # 20% — usa insights das fontes
    clareza_pastoral: int = 0           # 10% — linguagem acessível
    ausencia_antipadroes: int = 0       # 10% — sem listas de adjetivos

    score_total: float = 0.0
    aprovado: bool = False

    # Feedback
    pontos_fortes: str = ""
    problemas_encontrados: str = ""
    sugestoes_reescrita: str = ""

    modelo_llm: str = ""
    created_at: Optional[datetime] = None

    def calcular_score(self) -> float:
        """Calcula score ponderado (0-100)."""
        self.score_total = (
            self.fidelidade_exegetica * 0.30
            + self.extensao_adequada * 0.15
            + self.estrutura_ryle * 0.15
            + self.densidade_doutrinaria * 0.20
            + self.clareza_pastoral * 0.10
            + self.ausencia_antipadroes * 0.10
        )
        return self.score_total

    def to_db_dict(self) -> dict:
        return {
            "plano_id": self.plano_id,
            "escritor_trabalho_id": self.escritor_trabalho_id,
            "ciclo": self.ciclo,
            "fidelidade_exegetica": self.fidelidade_exegetica,
            "extensao_adequada": self.extensao_adequada,
            "estrutura_ryle": self.estrutura_ryle,
            "densidade_doutrinaria": self.densidade_doutrinaria,
            "clareza_pastoral": self.clareza_pastoral,
            "ausencia_antipadroes": self.ausencia_antipadroes,
            "score_total": self.score_total,
            "aprovado": self.aprovado,
            "pontos_fortes": self.pontos_fortes,
            "problemas_encontrados": self.problemas_encontrados,
            "sugestoes_reescrita": self.sugestoes_reescrita,
            "modelo_llm": self.modelo_llm,
        }
