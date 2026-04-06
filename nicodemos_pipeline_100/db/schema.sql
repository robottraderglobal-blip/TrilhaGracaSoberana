-- ==============================================
-- Nicodemos Pipeline 100 — Schema SQL
-- Tabelas para devocionais de culto doméstico
-- ==============================================

-- 1. Plano dos 100 dias
CREATE TABLE IF NOT EXISTS nico_plano (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    semana INTEGER NOT NULL CHECK (semana >= 1 AND semana <= 15),
    dia INTEGER NOT NULL UNIQUE CHECK (dia >= 1 AND dia <= 100),
    dia_semana INTEGER NOT NULL CHECK (dia_semana >= 1 AND dia_semana <= 7),
    ref TEXT NOT NULL,                    -- Referência bíblica (ex: "Salmos 100.4")
    versiculo TEXT NOT NULL,              -- Texto completo do versículo (ARA)
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index para buscas por semana
CREATE INDEX IF NOT EXISTS idx_nico_plano_semana ON nico_plano(semana);
CREATE INDEX IF NOT EXISTS idx_nico_plano_status ON nico_plano(status);

-- 2. Trabalho do escritor (rascunhos)
CREATE TABLE IF NOT EXISTS nico_escritor_trabalho (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plano_id UUID NOT NULL REFERENCES nico_plano(id) ON DELETE CASCADE,
    versao INTEGER NOT NULL DEFAULT 1,
    conteudo_md TEXT NOT NULL DEFAULT '',
    palavras INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'rascunho',
    feedback_revisor TEXT DEFAULT '',
    modelo_llm TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(plano_id, versao)
);

CREATE INDEX IF NOT EXISTS idx_nico_escritor_plano ON nico_escritor_trabalho(plano_id);

-- 3. Revisões
CREATE TABLE IF NOT EXISTS nico_revisoes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plano_id UUID NOT NULL REFERENCES nico_plano(id) ON DELETE CASCADE,
    escritor_trabalho_id TEXT DEFAULT '',
    ciclo INTEGER NOT NULL DEFAULT 1,
    conformidade_estrutural INTEGER DEFAULT 0,
    estilo_nicodemos INTEGER DEFAULT 0,
    conformidade_teologica INTEGER DEFAULT 0,
    qualidade_literaria INTEGER DEFAULT 0,
    extensao_adequada INTEGER DEFAULT 0,
    score_total REAL DEFAULT 0.0,
    aprovado BOOLEAN DEFAULT FALSE,
    pontos_fortes TEXT DEFAULT '',
    problemas_encontrados TEXT DEFAULT '',
    sugestoes_reescrita TEXT DEFAULT '',
    modelo_llm TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nico_revisoes_plano ON nico_revisoes(plano_id);

-- 4. Devocionais finais (consumidas pelo site)
CREATE TABLE IF NOT EXISTS nico_devocionais_final (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plano_id UUID NOT NULL REFERENCES nico_plano(id) ON DELETE CASCADE,
    ref TEXT NOT NULL,
    versiculo TEXT NOT NULL,
    conteudo_md TEXT NOT NULL,
    pergunta_reflexao TEXT DEFAULT '',
    palavras INTEGER DEFAULT 0,
    semana INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    escritor_trabalho_id TEXT DEFAULT '',
    revisao_final_id TEXT DEFAULT '',
    versao_aprovada INTEGER DEFAULT 1,
    score_final REAL DEFAULT 0.0,
    status TEXT DEFAULT 'aprovado',
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(plano_id)
);

CREATE INDEX IF NOT EXISTS idx_nico_final_semana ON nico_devocionais_final(semana);
CREATE INDEX IF NOT EXISTS idx_nico_final_dia ON nico_devocionais_final(dia);
CREATE INDEX IF NOT EXISTS idx_nico_final_status ON nico_devocionais_final(status);

-- RLS policies (habilitar para acesso do frontend)
ALTER TABLE nico_plano ENABLE ROW LEVEL SECURITY;
ALTER TABLE nico_devocionais_final ENABLE ROW LEVEL SECURITY;

-- Leitura pública para o site
CREATE POLICY "nico_plano_read" ON nico_plano
    FOR SELECT USING (true);

CREATE POLICY "nico_final_read" ON nico_devocionais_final
    FOR SELECT USING (true);

-- Service role pode tudo (para o pipeline)
CREATE POLICY "nico_plano_service" ON nico_plano
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "nico_escritor_service" ON nico_escritor_trabalho
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "nico_revisoes_service" ON nico_revisoes
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "nico_final_service" ON nico_devocionais_final
    FOR ALL USING (auth.role() = 'service_role');
