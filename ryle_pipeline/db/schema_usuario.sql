-- ============================================================
-- Minha Devocional — Schema (3 Tabelas para geração manual)
-- Execute no Supabase Dashboard: SQL Editor → New Query
-- ============================================================

-- 1. PASSAGENS SUGERIDAS
-- Registra TODAS as sugestões (confirmadas e recusadas)
CREATE TABLE IF NOT EXISTS usuario_passagens_sugeridas (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_key     TEXT NOT NULL,          -- chave anônima gerada no browser (sessionStorage)
  input_usuario   TEXT NOT NULL,          -- tema ou texto digitado pelo usuário
  passagem_ref    TEXT NOT NULL,          -- ex: "Filipenses 4.6-7"
  passagem_texto  TEXT NOT NULL,          -- texto completo ARA
  justificativa   TEXT,                   -- por que o LLM escolheu essa passagem
  confirmada      BOOLEAN NOT NULL DEFAULT FALSE,  -- TRUE quando o usuário confirma
  modelo_llm      TEXT,
  created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_passagens_session   ON usuario_passagens_sugeridas(session_key);
CREATE INDEX IF NOT EXISTS idx_passagens_confirmada ON usuario_passagens_sugeridas(confirmada);

-- ============================================================
-- 2. ANÁLISES EXEGÉTICAS (geradas pelo Analista Confessional)
-- Uma por passagem confirmada; sobrescreve em regeneração
CREATE TABLE IF NOT EXISTS usuario_analises (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  passagem_id     UUID NOT NULL REFERENCES usuario_passagens_sugeridas(id) ON DELETE CASCADE,
  -- Saída dos 6 passos do analista_usuario.md (texto markdown por passo)
  oracao          TEXT,                   -- Passo 1 — Oração
  observacao      TEXT,                   -- Passo 2 — Observação
  contexto        TEXT,                   -- Passo 3 — Contexto
  analise_gramatical TEXT,               -- Passo 4 — Gramática/Léxico
  interpretacao   TEXT,                   -- Passo 5 — Interpretação
  aplicacao       TEXT,                   -- Passo 6 — Aplicação
  conteudo_md     TEXT NOT NULL,          -- Markdown completo dos 6 passos (fallback/display)
  modelo_llm      TEXT,
  tokens_input    INT,
  tokens_output   INT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE(passagem_id)                     -- sobrescreve via upsert em regeneração
);

CREATE INDEX IF NOT EXISTS idx_analises_passagem ON usuario_analises(passagem_id);

-- ============================================================
-- 3. DEVOCIONAIS GERADAS (no estilo J.C. Ryle)
-- Uma por passagem confirmada; sobrescreve em regeneração
CREATE TABLE IF NOT EXISTS usuario_devocionais (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  passagem_id     UUID NOT NULL REFERENCES usuario_passagens_sugeridas(id) ON DELETE CASCADE,
  analise_id      UUID NOT NULL REFERENCES usuario_analises(id),
  titulo          TEXT,
  conteudo_md     TEXT NOT NULL,
  palavras        INT DEFAULT 0,
  modelo_llm      TEXT,
  tokens_input    INT,
  tokens_output   INT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE(passagem_id)                     -- sobrescreve via upsert em regeneração
);

CREATE INDEX IF NOT EXISTS idx_devocionais_passagem ON usuario_devocionais(passagem_id);
CREATE INDEX IF NOT EXISTS idx_devocionais_analise  ON usuario_devocionais(analise_id);

-- ============================================================
-- Função de atualização automática do updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers (apenas nas tabelas que têm updated_at)
CREATE TRIGGER trg_analises_usuario_updated_at
  BEFORE UPDATE ON usuario_analises
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_devocionais_usuario_updated_at
  BEFORE UPDATE ON usuario_devocionais
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
