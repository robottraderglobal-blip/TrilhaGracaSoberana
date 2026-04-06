-- ============================================================
-- Migração: Pesquisador v3 — Colunas + Tabela de Cache
-- Execute no Supabase Dashboard: SQL Editor → New Query
-- ============================================================

-- 1. Novas colunas em pesquisa_fontes (safe: IF NOT EXISTS)
ALTER TABLE pesquisa_fontes 
  ADD COLUMN IF NOT EXISTS key_insights JSONB DEFAULT '[]'::JSONB;

ALTER TABLE pesquisa_fontes 
  ADD COLUMN IF NOT EXISTS relevance_score INT DEFAULT 0;

ALTER TABLE pesquisa_fontes 
  ADD COLUMN IF NOT EXISTS fonte_resposta TEXT DEFAULT 'live';

ALTER TABLE pesquisa_fontes 
  ADD COLUMN IF NOT EXISTS tentativas INT DEFAULT 0;

-- 2. Tabela de cache NLM (evita re-consultas ao NotebookLM)
CREATE TABLE IF NOT EXISTS nlm_cache (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key   TEXT UNIQUE NOT NULL,
    notebook_id TEXT NOT NULL,
    query       TEXT NOT NULL,
    resposta    TEXT NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '21 days',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nlm_cache_key ON nlm_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_nlm_cache_expires ON nlm_cache(expires_at);
