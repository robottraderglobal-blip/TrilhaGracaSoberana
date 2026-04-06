"""Modelo: Revisao — crítica produzida pelo Agente Revisor Nicodemos."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Revisao(BaseModel):
    """Uma avaliação de um rascunho de devocional no estilo Augustus Nicodemos."""
    id: Optional[str] = None
    plano_id: str
    escritor_trabalho_id: str
    ciclo: int = Field(..., ge=1, le=3)

    # Scores individuais (0-100) — rubrica para estilo Nicodemos
    conformidade_estrutural: int = 0    # 20% — 6-8 parágrafos, versículo, pergunta
    estilo_nicodemos: int = 0           # 25% — tom pastoral, "você", ARA, cristocêntrico
    conformidade_teologica: int = 0     # 25% — fiel ao versículo, graça, sem prosperidade
    qualidade_literaria: int = 0        # 15% — variedade frasal, transições, incisividade
    extensao_adequada: int = 0          # 15% — 700-1000 palavras

    score_total: float = 0.0
    aprovado: bool = False

    # Feedback
    pontos_fortes: str = ""
    problemas_encontrados: str = ""
    sugestoes_reescrita: str = ""
    texto_corrigido: str = ""           # Texto com correções inline do revisor

    modelo_llm: str = ""
    created_at: Optional[datetime] = None

    def calcular_score(self) -> float:
        """Calcula score ponderado (0-100)."""
        self.score_total = (
            self.conformidade_estrutural * 0.20
            + self.estilo_nicodemos * 0.25
            + self.conformidade_teologica * 0.25
            + self.qualidade_literaria * 0.15
            + self.extensao_adequada * 0.15
        )
        return self.score_total

    def to_db_dict(self) -> dict:
        return {
            "rascunho_id": self.escritor_trabalho_id,
            "ciclo": self.ciclo,
            "conformidade_estrutural": self.conformidade_estrutural,
            "estilo_nicodemos": self.estilo_nicodemos,
            "conformidade_teologica": self.conformidade_teologica,
            "qualidade_literaria": self.qualidade_literaria,
            "extensao_adequada": self.extensao_adequada,
            "score_total": self.score_total,
            "aprovado": self.aprovado,
            "problemas_encontrados": self.problemas_encontrados,
            "sugestoes_reescrita": self.sugestoes_reescrita,
            "texto_corrigido_md": self.texto_corrigido,
            "modelo_llm": self.modelo_llm,
        }
