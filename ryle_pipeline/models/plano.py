"""Modelo: PlanoDevocional — representa um dia no plano de 52 semanas."""
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DiaNome(str, Enum):
    SAB = "Sáb"
    DOM = "Dom"
    SEG = "Seg"
    TER = "Ter"
    QUA = "Qua"
    QUI = "Qui"
    SEX = "Sex"


class StatusPlano(str, Enum):
    PENDING = "pending"
    EXEGESE_EM_ANDAMENTO = "exegese_em_andamento"
    EXEGESE_CONCLUIDA = "exegese_concluida"
    PESQUISA_EM_ANDAMENTO = "pesquisa_em_andamento"
    PESQUISA_CONCLUIDA = "pesquisa_concluida"
    ESCRITA_EM_ANDAMENTO = "escrita_em_andamento"
    ESCRITA_CONCLUIDA = "escrita_concluida"
    REVISAO_EM_ANDAMENTO = "revisao_em_andamento"
    APROVADO = "aprovado"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class PlanoDevocional(BaseModel):
    """Um dia do plano devocional anual."""
    id: Optional[str] = None
    semana: int = Field(..., ge=1, le=52)
    dia_semana: int = Field(..., ge=1, le=7)   # 1=Sáb ... 7=Sex
    dia_nome: DiaNome
    mes: int = Field(..., ge=1, le=13)
    tema_mes: str
    tema_semana: str
    texto_biblico: str                          # ex: "Isaías 6.1-7"
    tema_central: str                           # tema daquele dia
    status: StatusPlano = StatusPlano.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True
