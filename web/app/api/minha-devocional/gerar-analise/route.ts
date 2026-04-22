import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
import { join } from 'path';
import { callLLM } from '../llm';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const PROMPTS_DIR = join(process.cwd(), '..', 'ryle_pipeline', 'prompts');

function loadPrompt(filename: string): string {
  return readFileSync(join(PROMPTS_DIR, filename), 'utf-8');
}


function contarPalavras(texto: string): number {
  return texto.trim().split(/\s+/).length;
}

function extrairPassos(markdown: string): Record<string, string> {
  const passos: Record<string, string> = {};
  const regexes: Array<[string, RegExp]> = [
    ['oracao',             /##\s*Passo\s*1[^#]*([\s\S]*?)(?=##\s*Passo\s*2|$)/i],
    ['observacao',         /##\s*Passo\s*2[^#]*([\s\S]*?)(?=##\s*Passo\s*3|$)/i],
    ['contexto',           /##\s*Passo\s*3[^#]*([\s\S]*?)(?=##\s*Passo\s*4|$)/i],
    ['analise_gramatical', /##\s*Passo\s*4[^#]*([\s\S]*?)(?=##\s*Passo\s*5|$)/i],
    ['interpretacao',      /##\s*Passo\s*5[^#]*([\s\S]*?)(?=##\s*Passo\s*6|$)/i],
    ['aplicacao',          /##\s*Passo\s*6[^#]*([\s\S]*?)$/i],
  ];

  for (const [key, regex] of regexes) {
    const match = markdown.match(regex);
    passos[key] = match ? match[1].trim() : '';
  }
  return passos;
}

// POST /api/minha-devocional/gerar-analise
export async function POST(req: NextRequest) {
  try {
    const { passagemId } = await req.json();

    if (!passagemId) {
      return NextResponse.json(
        { error: 'passagemId é obrigatório' },
        { status: 400 }
      );
    }

    // Buscar a passagem confirmada
    const { data: passagem, error: errPassagem } = await supabase
      .from('usuario_passagens_sugeridas')
      .select('*')
      .eq('id', passagemId)
      .eq('confirmada', true)
      .single();

    if (errPassagem || !passagem) {
      return NextResponse.json(
        { error: 'Passagem não encontrada ou não confirmada' },
        { status: 404 }
      );
    }

    const systemPrompt = loadPrompt('analista_usuario.md');
    const userMessage = `Texto: ${passagem.passagem_ref} (ARA)\nPassagem: ${passagem.passagem_texto}\nFoco: devocional pessoal`;

    const analiseMarkdown = await callLLM(systemPrompt, userMessage);
    const passos = extrairPassos(analiseMarkdown);
    const palavras = contarPalavras(analiseMarkdown);

    // Upsert (sobrescreve se já existir para esta passagem)
    const { data, error } = await supabase
      .from('usuario_analises')
      .upsert(
        {
          passagem_id: passagemId,
          oracao: passos.oracao,
          observacao: passos.observacao,
          contexto: passos.contexto,
          analise_gramatical: passos.analise_gramatical,
          interpretacao: passos.interpretacao,
          aplicacao: passos.aplicacao,
          conteudo_md: analiseMarkdown,
          modelo_llm: process.env.LLM_PROVIDER || 'gemini',
        },
        { onConflict: 'passagem_id' }
      )
      .select('id')
      .single();

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({
      analiseId: data.id,
      conteudoMd: analiseMarkdown,
      palavras,
      passos,
    });
  } catch (err) {
    console.error('[gerar-analise]', err);
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 });
  }
}
