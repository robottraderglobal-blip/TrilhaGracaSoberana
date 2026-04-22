import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
import { join } from 'path';
import { callLLM } from '../llm';
import { enrichWithARA } from '../ara';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const PROMPTS_DIR = join(process.cwd(), '..', 'ryle_pipeline', 'prompts');

function loadPrompt(filename: string): string {
  return readFileSync(join(PROMPTS_DIR, filename), 'utf-8');
}

interface PassagemItem {
  ref: string;
  texto: string;
}

// POST /api/minha-devocional/sugerir-passagem
export async function POST(req: NextRequest) {
  try {
    const { input, sessionKey } = await req.json();

    if (!input || !sessionKey) {
      return NextResponse.json(
        { error: 'input e sessionKey são obrigatórios' },
        { status: 400 }
      );
    }

    const systemPrompt = loadPrompt('sugestor_passagem.md');
    const rawResponse = await callLLM(systemPrompt, input);

    // Limpar possíveis blocos de código markdown na resposta
    const cleaned = rawResponse
      .replace(/```json\s*/gi, '')
      .replace(/```\s*/gi, '')
      .trim();

    let parsed: { passagens: PassagemItem[] };
    try {
      const json = JSON.parse(cleaned);
      if (Array.isArray(json.passagens)) {
        parsed = json;
      } else if (json.ref) {
        parsed = { passagens: [json as PassagemItem] };
      } else {
        throw new Error('Formato inesperado');
      }
    } catch {
      return NextResponse.json(
        { error: 'LLM retornou JSON inválido', raw: cleaned },
        { status: 502 }
      );
    }

    // Enriquecer textos com a ARA local (substitui texto do LLM pelo texto real)
    const passagensEnriquecidas = enrichWithARA(parsed.passagens);

    // Salvar todas no banco (confirmada = false — será confirmada ao clicar Analisar)
    const inserts = passagensEnriquecidas.map((p) => ({
      session_key: sessionKey,
      input_usuario: input,
      passagem_ref: p.ref,
      passagem_texto: p.texto,
      justificativa: null,
      confirmada: false,
      modelo_llm: process.env.LLM_PROVIDER || 'openrouter',
    }));

    const { data, error } = await supabase
      .from('usuario_passagens_sugeridas')
      .insert(inserts)
      .select('id, passagem_ref, passagem_texto');

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    const passagens = (data as Array<{
      id: string;
      passagem_ref: string;
      passagem_texto: string;
    }>).map((row) => ({
      passagemId: row.id,
      ref: row.passagem_ref,
      texto: row.passagem_texto,
    }));

    return NextResponse.json({ passagens });
  } catch (err) {
    console.error('[sugerir-passagem]', err);
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 });
  }
}
