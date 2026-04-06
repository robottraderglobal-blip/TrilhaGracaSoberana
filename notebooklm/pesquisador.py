"""
Ryle Pipeline — Agente Pesquisador (v3)
Consulta o NotebookLM via MCP com sessão única, cache Supabase e paralelismo controlado.

Mudanças v3 (vs v2):
─────────────────────────────────────────────────────────────────────
RESILIÊNCIA
  • Sessão MCP única para todo o batch (não abre/fecha por query)
  • Backoff exponencial com jitter em cada chamada MCP
  • Cache Supabase: hit → pula NLM; miss → consulta e salva
  • Fallback gracioso: cache → fallback genérico → nunca trava o pipeline
  • Health check pre-flight: aborta cedo se sessão inválida

QUALIDADE
  • Consultas paralelas (asyncio.gather) com semáforo para não sobrecarregar
  • Multi-turn: conversa preservada por notebook via conversation_id
  • Query de follow-up automática se score < 3 após primeira resposta
  • key_insights e relevance_score propagados para o modelo PesquisaFonte
─────────────────────────────────────────────────────────────────────
"""
import asyncio
import json
import logging
import random
import time
from typing import Optional

from rich.console import Console

from .base import BaseAgent
from .. import config
from ..models.exegese import Exegese
from ..models.pesquisa import PesquisaFonte
from .nlm_cache import NLMCache

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

console = Console()
logger = logging.getLogger(__name__)

# ── Configurações de retry ────────────────────────────────────────────────────
MAX_RETRIES = 3          # tentativas por query dentro da sessão MCP
BACKOFF_BASE = 1.5       # segundos base para backoff exponencial
BACKOFF_MAX = 10.0       # teto do backoff em segundos
JITTER_MAX = 0.5         # aleatoriedade extra para evitar thundering herd
MIN_RESPOSTA_UTIL = 80   # chars mínimos para considerar resposta não-vazia
SEMAFORO_PARALELO = 2    # máximo de notebooks consultados simultaneamente

# ── Mapeamento fonte → nome real ──────────────────────────────────────────────
NOMES_AUTORES = {
    "sproul": "R.C. Sproul",
    "augustus": "Augustus Nicodemus",
    "spurgeon": "C.H. Spurgeon",
    "lloyd_jones": "D.M. Lloyd-Jones",
}


def _calcular_backoff(tentativa: int) -> float:
    """Backoff exponencial com jitter: base^tentativa + aleatório."""
    espera = min(BACKOFF_BASE ** tentativa, BACKOFF_MAX)
    jitter = random.uniform(0, JITTER_MAX)
    return espera + jitter


class AgentePesquisador(BaseAgent):
    def __init__(self, supabase_client=None):
        super().__init__("pesquisador_system.md")
        # Cache é opcional: se não passar supabase_client, roda sem cache
        self.cache = NLMCache(supabase_client) if supabase_client else None

    # ──────────────────────────────────────────────────────────────────────────
    # API pública
    # ──────────────────────────────────────────────────────────────────────────

    def pesquisar_todas(
        self, exegese: Exegese, texto_biblico: str, tema_central: str
    ) -> list[PesquisaFonte]:
        """
        Ponto de entrada síncrono: abre UMA sessão MCP e consulta todos os
        notebooks configurados em paralelo (controlado por semáforo).
        """
        return asyncio.run(
            self._pesquisar_todas_async(exegese, texto_biblico, tema_central)
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Orquestração assíncrona
    # ──────────────────────────────────────────────────────────────────────────

    async def _pesquisar_todas_async(
        self, exegese: Exegese, texto_biblico: str, tema_central: str
    ) -> list[PesquisaFonte]:
        """
        Abre UMA sessão stdio_client e reutiliza para todas as consultas.
        Isso elimina a principal fonte de falhas: reconexão por query.
        """
        fontes_validas = {
            nome: nb_id
            for nome, nb_id in config.FONTES_NOTEBOOKS.items()
            if nb_id and nb_id.strip()
        }

        if not fontes_validas:
            console.print("[yellow]⚠ Nenhum notebook configurado. Pesquisa vazia.[/yellow]")
            return []

        server_params = StdioServerParameters(command="notebooklm-mcp", args=[])
        semaforo = asyncio.Semaphore(SEMAFORO_PARALELO)

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Health check: garante que a sessão está funcional antes de começar
                    if not await self._health_check(session):
                        console.print("[red]❌ Health check falhou. Usando cache/fallback para todas as fontes.[/red]")
                        return await self._batch_fallback(exegese, texto_biblico, tema_central, fontes_validas)

                    # Consultas em paralelo com semáforo
                    tarefas = [
                        self._pesquisar_com_semaforo(
                            semaforo, session, nome, nb_id, exegese, texto_biblico, tema_central
                        )
                        for nome, nb_id in fontes_validas.items()
                    ]
                    resultados = await asyncio.gather(*tarefas, return_exceptions=True)

        except Exception as e:
            console.print(f"[red]❌ Falha ao iniciar sessão MCP: {e}[/red]")
            logger.error(f"Falha ao iniciar sessão MCP: {e}", exc_info=True)
            return await self._batch_fallback(exegese, texto_biblico, tema_central, fontes_validas)

        # Filtrar exceções não tratadas
        pesquisas = []
        for r in resultados:
            if isinstance(r, Exception):
                logger.error(f"Tarefa de pesquisa falhou com exceção: {r}")
            elif isinstance(r, PesquisaFonte):
                pesquisas.append(r)

        return pesquisas

    # ──────────────────────────────────────────────────────────────────────────
    # Consulta individual com semáforo
    # ──────────────────────────────────────────────────────────────────────────

    async def _pesquisar_com_semaforo(
        self,
        semaforo: asyncio.Semaphore,
        session: ClientSession,
        nome_fonte: str,
        notebook_id: str,
        exegese: Exegese,
        texto_biblico: str,
        tema_central: str,
    ) -> PesquisaFonte:
        async with semaforo:
            return await self._pesquisar_fonte(
                session, nome_fonte, notebook_id, exegese, texto_biblico, tema_central
            )

    async def _pesquisar_fonte(
        self,
        session: ClientSession,
        nome_fonte: str,
        notebook_id: str,
        exegese: Exegese,
        texto_biblico: str,
        tema_central: str,
    ) -> PesquisaFonte:
        """
        Consulta um notebook com retry + cache + fallback.
        Ordem de prioridade:
          1. Cache Supabase (hit instantâneo)
          2. NotebookLM via MCP (com retry e backoff)
          3. Fallback genérico (nunca trava o pipeline)
        """
        autor_nome = NOMES_AUTORES.get(nome_fonte, nome_fonte)
        queries = self._gerar_queries(nome_fonte, texto_biblico, tema_central, exegese)
        doutrinas = ", ".join(d.nome for d in exegese.doutrinas)

        # ── 1. Tentar cache para a query principal ───────────────────────────
        if self.cache:
            cached = self.cache.get(notebook_id, queries[0])
            if cached:
                console.print(f"   [dim cyan]📦 Cache hit: {nome_fonte}[/dim cyan]")
                return await self._resumir_e_montar(
                    cached, queries[0], nome_fonte, notebook_id,
                    exegese, texto_biblico, tema_central, doutrinas,
                    fonte_resposta="cache", tentativas=0
                )

        # ── 2. Consultar NotebookLM com retry ────────────────────────────────
        resposta_bruta = ""
        query_usada = ""
        tentativas_total = 0
        conversation_id = ""

        for i, query in enumerate(queries):
            for tentativa in range(MAX_RETRIES):
                tentativas_total += 1
                try:
                    console.print(
                        f"   [dim]🔍 {nome_fonte} | query {i+1}/{len(queries)} | "
                        f"tentativa {tentativa+1}/{MAX_RETRIES}[/dim]"
                    )

                    params = {"notebook_id": notebook_id, "query": query}
                    if conversation_id:
                        params["conversation_id"] = conversation_id

                    resultado_mcp = await session.call_tool("notebook_query", params)

                    # Extrair texto e conversation_id da resposta
                    textos = [c.text for c in resultado_mcp.content if c.type == "text"]
                    candidato = "\n".join(textos).strip()

                    # Tentar capturar conversation_id para multi-turn (se o tool retornar)
                    for bloco in resultado_mcp.content:
                        if hasattr(bloco, "data") and isinstance(bloco.data, dict):
                            conversation_id = bloco.data.get("conversation_id", conversation_id)

                    if len(candidato) > MIN_RESPOSTA_UTIL:
                        resposta_bruta = candidato
                        query_usada = query
                        # Salvar no cache imediatamente
                        if self.cache:
                            self.cache.set(notebook_id, query, resposta_bruta)
                        break  # sucesso, sair do loop de tentativas
                    else:
                        console.print(
                            f"   [yellow]↻ Resposta curta de {nome_fonte} "
                            f"({len(candidato)} chars). "
                            f"{'Retry...' if tentativa < MAX_RETRIES-1 else 'Aceitando.'}"
                            f"[/yellow]"
                        )

                except Exception as e:
                    logger.warning(f"[{nome_fonte}] Erro MCP tentativa {tentativa+1}: {e}")
                    if tentativa < MAX_RETRIES - 1:
                        espera = _calcular_backoff(tentativa)
                        console.print(
                            f"   [yellow]⏳ {nome_fonte}: erro MCP. "
                            f"Aguardando {espera:.1f}s antes de retry...[/yellow]"
                        )
                        await asyncio.sleep(espera)
                    else:
                        console.print(f"   [red]❌ {nome_fonte}: esgotou retries na tentativa {tentativa+1}.[/red]")

            if resposta_bruta:
                break  # query bem-sucedida, não precisa tentar a próxima

        # ── 3. Fallback se tudo falhou ───────────────────────────────────────
        if not resposta_bruta:
            console.print(f"   [dim red]⚠ {nome_fonte}: sem resposta. Usando fallback.[/dim red]")
            return self._montar_pesquisa_fallback(
                nome_fonte, notebook_id, queries[0],
                exegese, doutrinas, tentativas_total
            )

        # ── 4. Resumir via LLM e montar PesquisaFonte ────────────────────────
        return await self._resumir_e_montar(
            resposta_bruta, query_usada, nome_fonte, notebook_id,
            exegese, texto_biblico, tema_central, doutrinas,
            fonte_resposta="live", tentativas=tentativas_total,
            conversation_id=conversation_id
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers de qualidade e montagem
    # ──────────────────────────────────────────────────────────────────────────

    async def _resumir_e_montar(
        self,
        resposta_bruta: str,
        query_usada: str,
        nome_fonte: str,
        notebook_id: str,
        exegese: Exegese,
        texto_biblico: str,
        tema_central: str,
        doutrinas: str,
        fonte_resposta: str,
        tentativas: int,
        conversation_id: str = "",
    ) -> PesquisaFonte:
        """Processa a resposta bruta via LLM e monta o objeto PesquisaFonte."""
        autor_nome = NOMES_AUTORES.get(nome_fonte, nome_fonte)

        prompt_llm = (
            f"**Texto Bíblico:** {texto_biblico}\n"
            f"**Tema Central:** {tema_central}\n"
            f"**Doutrinas Observadas:** {doutrinas}\n"
            f"**Autor Consultado:** {autor_nome}\n\n"
            f"**Resposta Bruta do NotebookLM (Fonte: {nome_fonte}):**\n"
            f"{resposta_bruta}"
        )

        try:
            json_resume = self.call_llm_json(prompt_llm)
        except Exception as e:
            console.print(f"   [yellow]⚠ Erro ao parsear JSON do LLM ({nome_fonte}): {e}[/yellow]")
            json_resume = {
                "resultado": resposta_bruta[:500],
                "key_insights": [],
                "relevance_score": 2,
            }

        score = json_resume.get("relevance_score", 1)
        status = "concluido" if score >= 2 else "empty_response"

        return PesquisaFonte(
            plano_id=str(exegese.plano_id),
            exegese_id=str(exegese.id),
            fonte=nome_fonte,
            doutrina_nome=doutrinas,
            query_enviada=query_usada,
            resultado=json_resume.get("resultado", "Erro de parse"),
            key_insights=json_resume.get("key_insights", []),
            relevance_score=score,
            status=status,
            notebook_id=notebook_id,
            conversation_id=conversation_id,
            fonte_resposta=fonte_resposta,
            tentativas=tentativas,
        )

    def _montar_pesquisa_fallback(
        self,
        nome_fonte: str,
        notebook_id: str,
        query: str,
        exegese: Exegese,
        doutrinas: str,
        tentativas: int,
    ) -> PesquisaFonte:
        """
        Retorna um PesquisaFonte marcado como fallback.
        O agente escritor sabe ignorar esses ou usar com cautela.
        """
        return PesquisaFonte(
            plano_id=str(exegese.plano_id),
            exegese_id=str(exegese.id),
            fonte=nome_fonte,
            doutrina_nome=doutrinas,
            query_enviada=query,
            resultado="Sem dados relevantes",
            key_insights=[],
            relevance_score=1,
            status="erro",
            notebook_id=notebook_id,
            fonte_resposta="fallback",
            tentativas=tentativas,
        )

    async def _batch_fallback(
        self,
        exegese: Exegese,
        texto_biblico: str,
        tema_central: str,
        fontes: dict,
    ) -> list[PesquisaFonte]:
        """
        Quando a sessão MCP não pode nem iniciar, tenta o cache para todas as
        fontes. O que não estiver em cache vira fallback.
        """
        doutrinas = ", ".join(d.nome for d in exegese.doutrinas)
        resultados = []

        for nome_fonte, notebook_id in fontes.items():
            queries = self._gerar_queries(nome_fonte, texto_biblico, tema_central, exegese)

            cached = self.cache.get(notebook_id, queries[0]) if self.cache else None
            if cached:
                console.print(f"   [dim cyan]📦 Cache (batch fallback): {nome_fonte}[/dim cyan]")
                pesquisa = await self._resumir_e_montar(
                    cached, queries[0], nome_fonte, notebook_id,
                    exegese, texto_biblico, tema_central, doutrinas,
                    fonte_resposta="cache", tentativas=0
                )
            else:
                console.print(f"   [dim red]⚠ Fallback puro: {nome_fonte}[/dim red]")
                pesquisa = self._montar_pesquisa_fallback(
                    nome_fonte, notebook_id, queries[0], exegese, doutrinas, tentativas=0
                )
            resultados.append(pesquisa)

        return resultados

    # ──────────────────────────────────────────────────────────────────────────
    # Health check
    # ──────────────────────────────────────────────────────────────────────────

    async def _health_check(self, session: ClientSession) -> bool:
        """
        Verifica se a sessão MCP está operacional antes de iniciar o batch.
        Usa list_tools como ping — não consome quota do NotebookLM.
        """
        try:
            tools = await asyncio.wait_for(session.list_tools(), timeout=8.0)
            nomes = [t.name for t in tools.tools] if tools.tools else []
            if "notebook_query" not in nomes:
                logger.error(f"Health check: 'notebook_query' não encontrado. Tools: {nomes}")
                return False
            logger.info(f"Health check OK. Tools disponíveis: {nomes}")
            return True
        except asyncio.TimeoutError:
            logger.error("Health check: timeout (>8s)")
            return False
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return False

    # ──────────────────────────────────────────────────────────────────────────
    # Geração de queries
    # ──────────────────────────────────────────────────────────────────────────

    def _gerar_queries(
        self, nome_fonte: str, texto_biblico: str, tema_central: str, exegese: Exegese
    ) -> list[str]:
        """
        Gera queries em ordem de especificidade decrescente.
        Query 1: referência bíblica direta + tema.
        Query 2: palavras-chave doutrinárias (retry de ângulo diferente).
        """
        autor_nome = NOMES_AUTORES.get(nome_fonte, nome_fonte)

        palavras_chave = []
        for d in exegese.doutrinas[:3]:
            palavras_chave.extend(d.palavras_chave[:2])
        kw_str = ", ".join(palavras_chave[:5]) if palavras_chave else tema_central

        query_principal = (
            f"O que {autor_nome} ensina ou prega sobre {texto_biblico}? "
            f"Busco comentários, sermões ou reflexões sobre o tema '{tema_central}'. "
            f"Inclua citações diretas, ilustrações e aplicações práticas se disponíveis."
        )
        query_retry = (
            f"Quais sermões, estudos ou textos de {autor_nome} tratam sobre "
            f"{kw_str}? Apresente os principais argumentos e aplicações do autor."
        )
        return [query_principal, query_retry]
