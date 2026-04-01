"""Modelo: Exegese — resultado do Agente Exegeta (5 passos puritanos)."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Doutrina(BaseModel):
    """Uma doutrina extraída do texto bíblico."""
    nome: str                                   # ex: "A Suficiência Divina"
    base_textual: str                           # trecho do versículo
    palavras_chave: list[str] = Field(default_factory=list)
    versiculos_suporte: list[str] = Field(default_factory=list)
    refutacao: str = ""                          # refutação de interpretações errôneas


class Demonstracao(BaseModel):
    """Desdobramento argumentativo de uma doutrina."""
    doutrina_ref: str                            # referência ao nome da doutrina
    desdobramento: str
    linha_argumentativa: str = ""


class Aplicacao(BaseModel):
    """Aplicação prática da exegese."""
    instrucao: str = ""
    correcao: str = ""
    exortacao: str = ""
    consolacao: str = ""
    autoexame: list[str] = Field(default_factory=list)


class Exegese(BaseModel):
    """Exegese completa em 5 passos puritanos."""
    id: Optional[str] = None
    plano_id: str
    status: str = "pending"

    # Passo 1: Contexto
    contexto_autor: str = ""
    contexto_data: str = ""
    contexto_destinatarios: str = ""
    contexto_situacao: str = ""
    contexto_posicao: str = ""
    contexto_genero: str = ""                    # poesia, epístola, narrativa, profecia

    # Passo 2: Doutrina
    doutrinas: list[Doutrina] = Field(default_factory=list)

    # Passo 3: Demonstração
    demonstracao: list[Demonstracao] = Field(default_factory=list)

    # Passo 4: Aplicação
    aplicacao: Aplicacao = Field(default_factory=Aplicacao)

    # Passo 5: Síntese
    sintese: str = ""
    titulo_sugerido: str = ""

    # Metadados
    modelo_llm: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_db_dict(self) -> dict:
        """Converte para formato compatível com Supabase insert."""
        return {
            "plano_id": self.plano_id,
            "status": self.status,
            "contexto_autor": self.contexto_autor,
            "contexto_data": self.contexto_data,
            "contexto_destinatarios": self.contexto_destinatarios,
            "contexto_situacao": self.contexto_situacao,
            "contexto_posicao": self.contexto_posicao,
            "contexto_genero": self.contexto_genero,
            "doutrinas": [d.model_dump() for d in self.doutrinas],
            "demonstracao": [d.model_dump() for d in self.demonstracao],
            "aplicacao_instrucao": self.aplicacao.instrucao,
            "aplicacao_correcao": self.aplicacao.correcao,
            "aplicacao_exortacao": self.aplicacao.exortacao,
            "aplicacao_consolacao": self.aplicacao.consolacao,
            "aplicacao_autoexame": self.aplicacao.autoexame,
            "sintese": self.sintese,
            "titulo_sugerido": self.titulo_sugerido,
            "modelo_llm": self.modelo_llm,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
        }
