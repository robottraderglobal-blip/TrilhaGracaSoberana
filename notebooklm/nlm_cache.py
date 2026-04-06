"""
Ryle Pipeline — Cache de Respostas NotebookLM
Persiste respostas no Supabase para evitar perda de dados em quedas de conexão.

Estratégia:
  1. Antes de consultar o NLM: verificar se já existe resposta válida no cache.
  2. Após consulta bem-sucedida: salvar no cache.
  3. Se NLM cair: devolver do cache com fonte_resposta="cache".
  4. Se cache também vazio: devolver fallback genérico com fonte_resposta="fallback".

SQL para criar a tabela (rodar uma vez no Supabase):

    CREATE TABLE nlm_cache (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        cache_key   TEXT UNIQUE NOT NULL,
        notebook_id TEXT NOT NULL,
        query       TEXT NOT NULL,
        resposta    TEXT NOT NULL,
        expires_at  TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '21 days',
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE INDEX idx_nlm_cache_key ON nlm_cache(cache_key);
    CREATE INDEX idx_nlm_cache_expires ON nlm_cache(expires_at);

Limpeza automática (opcional, rodar como cron no Supabase):
    DELETE FROM nlm_cache WHERE expires_at < NOW();
"""
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def _make_cache_key(notebook_id: str, query: str) -> str:
    """Chave determinística: hash MD5 de notebook_id + query normalizada."""
    raw = f"{notebook_id}:{query.strip().lower()}"
    return hashlib.md5(raw.encode()).hexdigest()


class NLMCache:
    """
    Camada de cache entre o Agente Pesquisador e o NotebookLM.
    Usa Supabase como storage persistente.
    """

    def __init__(self, supabase_client):
        self.sb = supabase_client
        self.tabela = "nlm_cache"

    def get(self, notebook_id: str, query: str) -> Optional[str]:
        """
        Busca resposta válida no cache.
        Retorna None se não encontrar ou se o cache estiver expirado.
        """
        chave = _make_cache_key(notebook_id, query)
        try:
            result = (
                self.sb.table(self.tabela)
                .select("resposta, expires_at")
                .eq("cache_key", chave)
                .single()
                .execute()
            )
            if not result.data:
                return None

            # Verificar expiração (proteção extra além do índice)
            expires_str = result.data.get("expires_at", "")
            if expires_str:
                expires = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
                if expires < datetime.now(timezone.utc):
                    logger.debug(f"[cache] Entrada expirada para chave {chave[:8]}...")
                    return None

            logger.info(f"[cache] HIT para notebook={notebook_id[:8]}... query={query[:40]}...")
            return result.data["resposta"]

        except Exception as e:
            # Cache read nunca deve derrubar o pipeline
            logger.warning(f"[cache] Erro ao ler cache: {e}")
            return None

    def set(self, notebook_id: str, query: str, resposta: str) -> bool:
        """
        Salva resposta no cache.
        Usa upsert para sobrescrever entradas antigas da mesma chave.
        Retorna True se bem-sucedido.
        """
        if not resposta or len(resposta.strip()) < 50:
            # Não cachear respostas trivialmente curtas
            return False

        chave = _make_cache_key(notebook_id, query)
        try:
            self.sb.table(self.tabela).upsert({
                "cache_key": chave,
                "notebook_id": notebook_id,
                "query": query,
                "resposta": resposta,
                # Renovar TTL a cada escrita bem-sucedida
                "expires_at": "NOW() + INTERVAL '21 days'",
                "created_at": "NOW()",
            }).execute()
            logger.info(f"[cache] SET para chave {chave[:8]}... ({len(resposta)} chars)")
            return True
        except Exception as e:
            logger.warning(f"[cache] Erro ao escrever cache: {e}")
            return False

    def invalidate(self, notebook_id: str, query: str) -> None:
        """Invalida uma entrada específica do cache (útil para forçar re-consulta)."""
        chave = _make_cache_key(notebook_id, query)
        try:
            self.sb.table(self.tabela).delete().eq("cache_key", chave).execute()
        except Exception as e:
            logger.warning(f"[cache] Erro ao invalidar cache: {e}")
