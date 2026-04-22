import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

// POST /api/minha-devocional/confirmar-passagem
// Marca uma passagem sugerida como confirmada pelo usuário
export async function POST(req: NextRequest) {
  try {
    const { passagemId } = await req.json();

    if (!passagemId) {
      return NextResponse.json(
        { error: 'passagemId é obrigatório' },
        { status: 400 }
      );
    }

    const { error } = await supabase
      .from('usuario_passagens_sugeridas')
      .update({ confirmada: true })
      .eq('id', passagemId);

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ ok: true, passagemId });
  } catch (err) {
    console.error('[confirmar-passagem]', err);
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 });
  }
}
