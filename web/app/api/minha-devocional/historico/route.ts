import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

function getSupabase() {
  return createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

// GET /api/minha-devocional/historico?sessionKey=xxx
// Retorna todas as sessões desta chave anônima com análise e devocional
export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const sessionKey = searchParams.get('sessionKey');

    if (!sessionKey) {
      return NextResponse.json({ error: 'sessionKey é obrigatório' }, { status: 400 });
    }

    const { data, error } = await getSupabase()
      .from('usuario_passagens_sugeridas')
      .select(`
        id,
        input_usuario,
        passagem_ref,
        passagem_texto,
        justificativa,
        confirmada,
        created_at,
        usuario_analises (
          id,
          conteudo_md,
          created_at
        ),
        usuario_devocionais (
          id,
          titulo,
          conteudo_md,
          palavras,
          created_at
        )
      `)
      .eq('session_key', sessionKey)
      .eq('confirmada', true)
      .order('created_at', { ascending: false });

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ historico: data || [] });
  } catch (err) {
    console.error('[historico]', err);
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 });
  }
}
