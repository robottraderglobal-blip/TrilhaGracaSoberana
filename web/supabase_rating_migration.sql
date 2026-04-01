-- 1. Adicionar colunas de métricas de avaliação
ALTER TABLE devocionais_final 
ADD COLUMN IF NOT EXISTS rating_total INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS rating_count INT DEFAULT 0;

-- 2. Criar função RPC para incrementar pontuação de forma atômica
CREATE OR REPLACE FUNCTION increment_rating(
    p_devocional_id UUID,
    p_stars INT
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE devocionais_final
    SET 
        rating_total = COALESCE(rating_total, 0) + p_stars,
        rating_count = COALESCE(rating_count, 0) + 1,
        updated_at = now()
    WHERE id = p_devocional_id;
END;
$$;
