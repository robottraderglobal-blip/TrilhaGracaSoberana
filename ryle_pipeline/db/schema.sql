-- ============================================================
-- Ryle Pipeline — Schema Completo (7 Tabelas)
-- Execute no Supabase Dashboard: SQL Editor → New Query
-- ============================================================

-- 1. PLANO DEVOCIONAL (Tabela Mestre — 364 linhas)
CREATE TABLE IF NOT EXISTS plano_devocional (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  semana        INT NOT NULL,
  dia_semana    INT NOT NULL,              -- 1=Sáb, 2=Dom, 3=Seg, 4=Ter, 5=Qua, 6=Qui, 7=Sex
  dia_nome      TEXT NOT NULL,
  mes           INT NOT NULL,
  tema_mes      TEXT NOT NULL,
  tema_semana   TEXT NOT NULL,
  texto_biblico TEXT NOT NULL,
  tema_central  TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'pending',
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now(),
  UNIQUE(semana, dia_semana)
);

CREATE INDEX IF NOT EXISTS idx_plano_status ON plano_devocional(status);
CREATE INDEX IF NOT EXISTS idx_plano_semana ON plano_devocional(semana);
CREATE INDEX IF NOT EXISTS idx_plano_mes ON plano_devocional(mes);

-- 2. EXEGESES (Saída do Agente Exegeta — 5 passos puritanos)
CREATE TABLE IF NOT EXISTS exegeses (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  plano_id        UUID NOT NULL REFERENCES plano_devocional(id) ON DELETE CASCADE,
  status          TEXT NOT NULL DEFAULT 'pending',
  contexto_autor         TEXT,
  contexto_data          TEXT,
  contexto_destinatarios TEXT,
  contexto_situacao      TEXT,
  contexto_posicao       TEXT,
  contexto_genero        TEXT,
  doutrinas       JSONB,
  demonstracao    JSONB,
  aplicacao_instrucao   TEXT,
  aplicacao_correcao    TEXT,
  aplicacao_exortacao   TEXT,
  aplicacao_consolacao  TEXT,
  aplicacao_autoexame   JSONB,
  sintese               TEXT,
  titulo_sugerido       TEXT,
  modelo_llm     TEXT,
  tokens_input   INT,
  tokens_output  INT,
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now(),
  UNIQUE(plano_id)
);

-- 3. PESQUISA_FONTES (Saída do Agente Pesquisador — NotebookLM)
CREATE TABLE IF NOT EXISTS pesquisa_fontes (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  plano_id          UUID NOT NULL REFERENCES plano_devocional(id) ON DELETE CASCADE,
  exegese_id        UUID NOT NULL REFERENCES exegeses(id) ON DELETE CASCADE,
  fonte             TEXT NOT NULL,
  doutrina_nome     TEXT NOT NULL,
  query_enviada     TEXT,
  resultado         TEXT,
  status            TEXT NOT NULL DEFAULT 'pending',
  notebook_id       TEXT,
  conversation_id   TEXT,
  created_at        TIMESTAMPTZ DEFAULT now(),
  updated_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pesquisa_plano ON pesquisa_fontes(plano_id);
CREATE INDEX IF NOT EXISTS idx_pesquisa_fonte ON pesquisa_fontes(fonte);
CREATE INDEX IF NOT EXISTS idx_pesquisa_status ON pesquisa_fontes(status);

-- 4. ESCRITOR_TRABALHO (Rascunhos do Agente Escritor)
CREATE TABLE IF NOT EXISTS escritor_trabalho (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  plano_id        UUID NOT NULL REFERENCES plano_devocional(id) ON DELETE CASCADE,
  exegese_id      UUID NOT NULL REFERENCES exegeses(id) ON DELETE CASCADE,
  versao          INT NOT NULL DEFAULT 1,
  titulo          TEXT,
  conteudo_md     TEXT,
  palavras        INT DEFAULT 0,
  status          TEXT NOT NULL DEFAULT 'rascunho',
  feedback_revisor TEXT,
  modelo_llm      TEXT,
  tokens_input    INT,
  tokens_output   INT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE(plano_id, versao)
);

-- 5. REVISOES (Críticas do Agente Revisor)
CREATE TABLE IF NOT EXISTS revisoes (
  id                     UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  plano_id               UUID NOT NULL REFERENCES plano_devocional(id) ON DELETE CASCADE,
  escritor_trabalho_id   UUID NOT NULL REFERENCES escritor_trabalho(id) ON DELETE CASCADE,
  ciclo                  INT NOT NULL,
  fidelidade_exegetica   INT,
  extensao_adequada      INT,
  estrutura_ryle         INT,
  densidade_doutrinaria  INT,
  clareza_pastoral       INT,
  ausencia_antipadroes   INT,
  score_total            FLOAT,
  aprovado               BOOLEAN NOT NULL DEFAULT FALSE,
  pontos_fortes          TEXT,
  problemas_encontrados  TEXT,
  sugestoes_reescrita    TEXT,
  modelo_llm             TEXT,
  created_at             TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_revisoes_plano ON revisoes(plano_id);

-- 6. DEVOCIONAIS_FINAL (Devocional aprovado para publicação)
CREATE TABLE IF NOT EXISTS devocionais_final (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  plano_id        UUID NOT NULL REFERENCES plano_devocional(id) ON DELETE CASCADE UNIQUE,
  titulo          TEXT NOT NULL,
  texto_biblico   TEXT NOT NULL,
  subtema         TEXT,
  tema_semana     TEXT,
  tema_mes        TEXT,
  conteudo_md     TEXT NOT NULL,
  palavras        INT NOT NULL,
  exegese_id             UUID REFERENCES exegeses(id),
  escritor_trabalho_id   UUID REFERENCES escritor_trabalho(id),
  revisao_final_id       UUID REFERENCES revisoes(id),
  versao_aprovada        INT,
  score_final            FLOAT,
  status          TEXT NOT NULL DEFAULT 'aprovado',
  published_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- 7. DEVOCIONAIS_NARRACAO (Texto puro para TTS/narração)
CREATE TABLE IF NOT EXISTS devocionais_narracao (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  plano_id            UUID NOT NULL REFERENCES plano_devocional(id) ON DELETE CASCADE UNIQUE,
  devocional_final_id UUID NOT NULL REFERENCES devocionais_final(id) ON DELETE CASCADE,
  titulo              TEXT NOT NULL,
  texto_puro          TEXT NOT NULL,
  palavras            INT NOT NULL,
  indicacoes_leitura  TEXT,
  status              TEXT NOT NULL DEFAULT 'pending',
  created_at          TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- RLS Policies (opcional — desabilitar para uso via service key)
-- ============================================================
-- ALTER TABLE plano_devocional ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow all for service role" ON plano_devocional
--   FOR ALL USING (true) WITH CHECK (true);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers de updated_at
CREATE TRIGGER trg_plano_updated_at BEFORE UPDATE ON plano_devocional
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_exegeses_updated_at BEFORE UPDATE ON exegeses
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_pesquisa_updated_at BEFORE UPDATE ON pesquisa_fontes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_escritor_updated_at BEFORE UPDATE ON escritor_trabalho
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_final_updated_at BEFORE UPDATE ON devocionais_final
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_narracao_updated_at BEFORE UPDATE ON devocionais_narracao
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
