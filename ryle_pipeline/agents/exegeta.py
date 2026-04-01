"""
Agente Exegeta — Análise bíblica em 5 passos puritanos.
"""
from ..models.exegese import Exegese, Doutrina, Demonstracao, Aplicacao
from .base import BaseAgent


class AgenteExegeta(BaseAgent):
    """Produz exegese em 5 passos a partir de um texto bíblico."""

    def __init__(self):
        super().__init__("exegeta_system.md")

    def analisar(self, texto_biblico: str, tema_central: str, plano_id: str) -> Exegese:
        """
        Executa a exegese puritana em 5 passos.

        Args:
            texto_biblico: Referência bíblica (ex: "Isaías 6.1-7")
            tema_central: Ângulo temático do dia
            plano_id: ID do registro no plano_devocional

        Returns:
            Exegese completa com todos os 5 passos preenchidos
        """
        prompt = (
            f"## Texto Bíblico\n{texto_biblico}\n\n"
            f"## Ângulo Temático\n{tema_central}\n\n"
            f"Produza a exegese completa em 5 passos conforme suas instruções. "
            f"Responda em JSON válido."
        )

        data = self.call_llm_json(prompt)

        # Montar objeto Exegese a partir do JSON
        doutrinas = [
            Doutrina(**d) for d in data.get("doutrinas", [])
        ]
        demonstracao = [
            Demonstracao(**d) for d in data.get("demonstracao", [])
        ]
        aplicacao = Aplicacao(
            instrucao=data.get("aplicacao_instrucao", ""),
            correcao=data.get("aplicacao_correcao", ""),
            exortacao=data.get("aplicacao_exortacao", ""),
            consolacao=data.get("aplicacao_consolacao", ""),
            autoexame=data.get("aplicacao_autoexame", []),
        )

        return Exegese(
            plano_id=plano_id,
            status="concluido",
            contexto_autor=data.get("contexto_autor", ""),
            contexto_data=data.get("contexto_data", ""),
            contexto_destinatarios=data.get("contexto_destinatarios", ""),
            contexto_situacao=data.get("contexto_situacao", ""),
            contexto_posicao=data.get("contexto_posicao", ""),
            contexto_genero=data.get("contexto_genero", ""),
            doutrinas=doutrinas,
            demonstracao=demonstracao,
            aplicacao=aplicacao,
            sintese=data.get("sintese", ""),
            titulo_sugerido=data.get("titulo_sugerido", ""),
            modelo_llm=self.model,
        )
