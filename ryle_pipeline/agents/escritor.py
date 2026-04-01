"""
Agente Escritor — Produz devocionais no estilo J.C. Ryle.
"""
from ..models.exegese import Exegese
from ..models.escritor import EscritorTrabalho
from .base import BaseAgent


from ..models.pesquisa import PesquisaFonte

class AgenteEscritor(BaseAgent):
    """Produz devocionais no estilo de J.C. Ryle a partir da exegese."""

    def __init__(self):
        super().__init__("escritor_system.md")

    def escrever(
        self,
        plano: dict,
        exegese: Exegese,
        pesquisas: list[PesquisaFonte] | None = None,
    ) -> EscritorTrabalho:
        """
        Escreve o devocional a partir do plano, exegese e pesquisa.

        Args:
            plano: Dados do plano_devocional (dict do Supabase)
            exegese: Exegese completa do Agente Exegeta
            pesquisas: Lista de resultados do Agente Pesquisador (opcional)

        Returns:
            EscritorTrabalho com o rascunho do devocional
        """
        # Montar o prompt com todos os materiais
        prompt_parts = [
            f"## Texto Bíblico\n{plano['texto_biblico']}",
            f"\n## Tema Central\n{plano['tema_central']}",
            f"\n## Tema da Semana\n{plano.get('tema_semana', '')}",
            f"\n## Título Sugerido pelo Exegeta\n{exegese.titulo_sugerido}",
            f"\n## Síntese Exegética\n{exegese.sintese}",
        ]

        # Doutrinas extraídas
        prompt_parts.append("\n## Doutrinas Extraídas pelo Exegeta")
        for i, d in enumerate(exegese.doutrinas, 1):
            prompt_parts.append(
                f"\n### Doutrina {i}: {d.nome}\n"
                f"- Base textual: {d.base_textual}\n"
                f"- Versículos de suporte: {', '.join(d.versiculos_suporte)}\n"
                f"- Refutação: {d.refutacao}"
            )

        # Demonstração
        prompt_parts.append("\n## Desdobramento Argumentativo")
        for dem in exegese.demonstracao:
            prompt_parts.append(
                f"\n### {dem.doutrina_ref}\n"
                f"{dem.desdobramento}\n"
                f"Linha argumentativa: {dem.linha_argumentativa}"
            )

        # Aplicação
        prompt_parts.append(
            f"\n## Aplicação Prática\n"
            f"- Instrução: {exegese.aplicacao.instrucao}\n"
            f"- Correção: {exegese.aplicacao.correcao}\n"
            f"- Exortação: {exegese.aplicacao.exortacao}\n"
            f"- Consolação: {exegese.aplicacao.consolacao}\n"
            f"- Perguntas de autoexame: {'; '.join(exegese.aplicacao.autoexame)}"
        )

        # Pesquisa das fontes (se disponível)
        if pesquisas:
            prompt_parts.append("\n## Insights das Fontes Teológicas")
            for p in pesquisas:
                if p.resultado:
                    fonte_label = {
                        "sproul": "R.C. Sproul",
                        "nicodemus": "Augustus Nicodemus",
                        "spurgeon": "C.H. Spurgeon",
                        "lloyd_jones": "Martyn Lloyd-Jones",
                    }.get(p.fonte, p.fonte)
                    prompt_parts.append(
                        f"\n### {fonte_label} sobre '{p.doutrina_nome}':\n"
                        f"{p.resultado}"
                    )

        prompt_parts.append(
            "\n---\n"
            "Com base em TODO o material acima, escreva o devocional completo "
            "no estilo de J.C. Ryle (800-1200 palavras, 3 pontos romanos, ARA). "
            "ATENÇÃO: NÃO escreva o texto bíblico no topo! Ele já será inserido automaticamente pelo sistema. "
            "Comece a sua resposta diretamente com a meditação/reflexão (Ex: 'Leitor, leia as palavras acima...'). "
            "Retorne APENAS o texto do devocional em markdown."
        )

        prompt = "\n".join(prompt_parts)
        conteudo = self.call_llm(prompt)
        
        # Limpar se o LLM ignorar e tentar colocar o texto bíblico
        if conteudo.startswith("“") or conteudo.startswith("*“"):
            # A heurística pode ser imperfeita, mas a string forced abaixo corrige o problema crônico
            pass

        referencia = plano["texto_biblico"]
        texto_completo = plano.get("versiculo_completo")
        
        if texto_completo:
            texto_limpo = texto_completo.strip()
            # Remove a referência do final do texto se o usuário tiver colado junto no banco de dados
            if referencia in texto_limpo:
                texto_limpo = texto_limpo.replace(f" — {referencia} (ARA)", "").replace(f" {referencia} (ARA)", "").replace(f" {referencia}", "").strip()
                if texto_limpo.endswith(" (ARA)"):
                    texto_limpo = texto_limpo[:-6].strip()
            
            cabecalho = f"*{texto_limpo}* — {referencia} (ARA)\n\n"
        else:
            cabecalho = f"*{referencia}* (ARA)\n\n"
            
        texto_final = f"{cabecalho}{conteudo.strip()}"

        trabalho = EscritorTrabalho(
            plano_id=plano["id"],
            exegese_id=exegese.id or exegese.plano_id,
            versao=1,
            titulo=exegese.titulo_sugerido,
            conteudo_md=texto_final,
            status="rascunho",
            modelo_llm=self.model,
        )
        trabalho.palavras = trabalho.contar_palavras()
        return trabalho

    def reescrever(
        self,
        trabalho_anterior: EscritorTrabalho,
        feedback: str,
        plano: dict,
        exegese: Exegese,
    ) -> EscritorTrabalho:
        """
        Reescreve o devocional incorporando o feedback do revisor.

        Args:
            trabalho_anterior: Rascunho reprovado
            feedback: Feedback detalhado do revisor
            plano: Dados do plano
            exegese: Exegese original

        Returns:
            Novo EscritorTrabalho com versão incrementada
        """
        prompt = (
            f"## Texto Bíblico\n{plano['texto_biblico']}\n\n"
            f"## Rascunho Anterior (REPROVADO)\n"
            f"```\n{trabalho_anterior.conteudo_md}\n```\n\n"
            f"## Feedback do Revisor\n{feedback}\n\n"
            f"## Síntese Exegética (referência)\n{exegese.sintese}\n\n"
            f"---\n"
            f"Reescreva o devocional corrigindo TODOS os problemas apontados. "
            f"Mantenha o que estava bom. "
            f"ATENÇÃO: NÃO escreva o texto bíblico no topo! Ele já será inserido automaticamente pelo sistema. "
            f"Comece a sua resposta diretamente com a meditação/reflexão (Ex: 'Leitor, leia as palavras acima...'). "
            f"Retorne APENAS o texto do devocional em markdown."
        )

        conteudo = self.call_llm(prompt)

        referencia = plano["texto_biblico"]
        texto_completo = plano.get("versiculo_completo")
        
        if texto_completo:
            texto_limpo = texto_completo.strip()
            # Remove a referência do final do texto se o usuário tiver colado junto no banco de dados
            if referencia in texto_limpo:
                texto_limpo = texto_limpo.replace(f" — {referencia} (ARA)", "").replace(f" {referencia} (ARA)", "").replace(f" {referencia}", "").strip()
                if texto_limpo.endswith(" (ARA)"):
                    texto_limpo = texto_limpo[:-6].strip()
            
            cabecalho = f"*{texto_limpo}* — {referencia} (ARA)\n\n"
        else:
            cabecalho = f"*{referencia}* (ARA)\n\n"
            
        texto_final = f"{cabecalho}{conteudo.strip()}"

        novo = EscritorTrabalho(
            plano_id=trabalho_anterior.plano_id,
            exegese_id=trabalho_anterior.exegese_id,
            versao=trabalho_anterior.versao + 1,
            titulo=trabalho_anterior.titulo,
            conteudo_md=texto_final,
            status="rascunho",
            modelo_llm=self.model,
        )
        novo.palavras = novo.contar_palavras()
        return novo
