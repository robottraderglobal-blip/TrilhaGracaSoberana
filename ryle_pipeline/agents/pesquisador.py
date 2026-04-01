"""
Ryle Pipeline — Agente Pesquisador (v2)
Consulta o NotebookLM via MCP com queries em linguagem natural.

Mudanças v2:
- Queries em linguagem natural (não doutrinária)
- 2 tentativas por caderno (query principal + retry reformulado)
- Referência bíblica explícita sempre presente
- Mapeamento autor ↔ nome real para contexto
"""
import asyncio
from rich.console import Console
from .base import BaseAgent
from .. import config
from ..models.exegese import Exegese
from ..models.pesquisa import PesquisaFonte

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

console = Console()

# Mapeamento fonte → nome real do teólogo (para queries mais naturais)
NOMES_AUTORES = {
    "sproul": "R.C. Sproul",
    "augustus": "Augustus Nicodemus",
    "spurgeon": "C.H. Spurgeon",
    "lloyd_jones": "D.M. Lloyd-Jones",
}


class AgentePesquisador(BaseAgent):
    def __init__(self):
        super().__init__("pesquisador_system.md")
    
    def pesquisar_todas(self, exegese: Exegese, texto_biblico: str, tema_central: str) -> list[PesquisaFonte]:
        """
        Consulta sequencialmente todos os notebooks configurados.
        Embrulha a chamada assíncrona para o pipeline síncrono.
        """
        return asyncio.run(self._pesquisar_todas_async(exegese, texto_biblico, tema_central))

    async def _pesquisar_todas_async(self, exegese: Exegese, texto_biblico: str, tema_central: str) -> list[PesquisaFonte]:
        resultados = []
        for nome_fonte, notebook_id in config.FONTES_NOTEBOOKS.items():
            if not notebook_id or not notebook_id.strip():
                console.print(f"   [yellow]⚠ Notebook ID para '{nome_fonte}' inválido/vazio. Pulando.[/yellow]")
                continue
                
            try:
                pesquisa = await self._pesquisar_fonte(nome_fonte, notebook_id, exegese, texto_biblico, tema_central)
                resultados.append(pesquisa)
            except Exception as e:
                console.print(f"   [red]❌ Erro ao consultar {nome_fonte}: {str(e)}[/red]")
                
        return resultados

    def _gerar_queries(self, nome_fonte: str, texto_biblico: str, tema_central: str, exegese: Exegese) -> list[str]:
        """
        Gera uma lista de queries em linguagem natural para maximizar
        a chance de obter respostas relevantes do NotebookLM.
        """
        autor_nome = NOMES_AUTORES.get(nome_fonte, nome_fonte)
        
        # Extrair palavras-chave das doutrinas (mais simples e diretas)
        palavras_chave = []
        for d in exegese.doutrinas[:3]:  # max 3 doutrinas
            palavras_chave.extend(d.palavras_chave[:2])  # max 2 keywords cada
        
        kw_str = ", ".join(palavras_chave[:5]) if palavras_chave else tema_central
        
        # Query principal: referência bíblica direta + tema em linguagem simples
        query_principal = (
            f"O que {autor_nome} ensina ou prega sobre {texto_biblico}? "
            f"Busco comentários, sermões ou reflexões sobre o tema '{tema_central}'. "
            f"Inclua citações diretas, ilustrações e aplicações práticas se disponíveis."
        )
        
        # Query de retry: ângulo diferente, foco em palavras-chave e tema
        query_retry = (
            f"Quais sermões, estudos ou textos de {autor_nome} tratam sobre "
            f"{kw_str}? Apresente os principais argumentos e aplicações do autor."
        )
        
        return [query_principal, query_retry]

    async def _pesquisar_fonte(self, nome_fonte: str, notebook_id: str, exegese: Exegese, texto_biblico: str, tema_central: str) -> PesquisaFonte:
        """Consulta o MCP com retry inteligente e depois resume via LLM."""
        autor_nome = NOMES_AUTORES.get(nome_fonte, nome_fonte)
        console.print(f"   [dim]Consultando {nome_fonte} via NotebookLM MCP...[/dim]")
        
        doutrinas = ", ".join(d.nome for d in exegese.doutrinas)
        queries = self._gerar_queries(nome_fonte, texto_biblico, tema_central, exegese)
        
        resposta_bruta = ""
        query_usada = ""
        
        server_params = StdioServerParameters(
            command="notebooklm-mcp",
            args=[],
        )
        
        for i, query in enumerate(queries):
            try:
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        
                        resultado_mcp = await session.call_tool(
                            "notebook_query", 
                            {"notebook_id": notebook_id, "query": query}
                        )
                        
                        textos = [c.text for c in resultado_mcp.content if c.type == "text"]
                        if textos:
                            candidato = "\n".join(textos)
                            # Verificar se a resposta é substancial (> 80 chars)
                            if len(candidato.strip()) > 80:
                                resposta_bruta = candidato
                                query_usada = query
                                break
                            elif i == 0:
                                # Primeira tentativa fraca, tentar retry
                                console.print(f"   [yellow]↻ Resposta curta de {nome_fonte}, tentando reformulação...[/yellow]")
                                continue
                            else:
                                # Último retry, aceitar o que tem
                                resposta_bruta = candidato
                                query_usada = query
            except Exception as e:
                if i == 0:
                    console.print(f"   [yellow]↻ Erro MCP ({nome_fonte}), tentando retry...[/yellow]")
                    continue
                else:
                    console.print(f"   [red]Erro de MCP IO para {nome_fonte}: {e}[/red]")
                    resposta_bruta = f"Erro no servidor local MCP: {e}"
                    query_usada = query

        if not query_usada:
            query_usada = queries[0]

        if not resposta_bruta.strip():
            resposta_bruta = "Não foi possível obter resposta desta fonte."

        # Resumir via LLM local (Agente Base)
        prompt_llm = f"""
        **Texto Bíblico:** {texto_biblico}
        **Tema Central:** {tema_central}
        **Doutrinas Observadas:** {doutrinas}
        **Autor Consultado:** {autor_nome}
        
        **Resposta Bruta do NotebookLM (Fonte: {nome_fonte}):**
        {resposta_bruta}
        """
        
        try:
            json_resume = self.call_llm_json(prompt_llm)
        except Exception as e:
            console.print(f"   [yellow]⚠ Erro ao parsear JSON da IA. ({e}) Fallback ativado.[/yellow]")
            json_resume = {
                "resultado": "Erro de parse do LLM.", 
                "key_insights": [], 
                "relevance_score": 1
            }
            
        return PesquisaFonte(
            plano_id=str(exegese.plano_id),
            exegese_id=str(exegese.id),
            fonte=nome_fonte,
            doutrina_nome=doutrinas,
            query_enviada=query_usada,
            resultado=json_resume.get("resultado", "Erro"),
            status="concluido" if json_resume.get("relevance_score", 1) >= 2 else "empty_response",
            notebook_id=notebook_id
        )
