import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
import { join } from 'path';
import { callLLM } from '../llm';

function getSupabase() {
  return createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

const PROMPTS_DIR = join(process.cwd(), '..', 'ryle_pipeline', 'prompts');

function loadPrompt(filename: string): string {
  return readFileSync(join(PROMPTS_DIR, filename), 'utf-8');
}


function contarPalavras(texto: string): number {
  return texto.trim().split(/\s+/).length;
}

function extrairTitulo(markdown: string): string {
  const match = markdown.match(/^#\s+(.+)/m);
  return match ? match[1].trim() : '';
}

// POST /api/minha-devocional/gerar-devocional
export async function POST(req: NextRequest) {
  try {
    const { passagemId, analiseId } = await req.json();

    if (!passagemId || !analiseId) {
      return NextResponse.json(
        { error: 'passagemId e analiseId são obrigatórios' },
        { status: 400 }
      );
    }

    // Buscar passagem e análise
    const [{ data: passagem, error: errP }, { data: analise, error: errA }] =
      await Promise.all([
        supabase
          .from('usuario_passagens_sugeridas')
          .select('passagem_ref, passagem_texto')
          .eq('id', passagemId)
          .single(),
        supabase
          .from('usuario_analises')
          .select('conteudo_md')
          .eq('id', analiseId)
          .single(),
      ]);

    if (errP || !passagem) {
      return NextResponse.json({ error: 'Passagem não encontrada' }, { status: 404 });
    }
    if (errA || !analise) {
      return NextResponse.json({ error: 'Análise não encontrada' }, { status: 404 });
    }

    const systemPrompt = loadPrompt('escritor_system.md');
    const userMessage = `## Passagem Bíblica\n\n"${passagem.passagem_texto}"\n— ${passagem.passagem_ref} (ARA)\n\n## Análise Exegética\n\n${analise.conteudo_md}`;

    const devocionalMarkdown = await callLLM(systemPrompt, userMessage, 'google/gemini-2.5-flash');
    const titulo = extrairTitulo(devocionalMarkdown);
    const palavras = contarPalavras(devocionalMarkdown);

    // Upsert (sobrescreve se já existir para esta passagem)
    const { data, error } = await supabase
      .from('usuario_devocionais')
      .upsert(
        {
          passagem_id: passagemId,
          analise_id: analiseId,
          titulo: titulo || passagem.passagem_ref,
          conteudo_md: devocionalMarkdown,
          palavras,
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
      devocionalId: data.id,
      titulo: titulo || passagem.passagem_ref,
      conteudoMd: devocionalMarkdown,
      palavras,
    });
  } catch (err) {
    console.error('[gerar-devocional]', err);
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 });
  }
}
