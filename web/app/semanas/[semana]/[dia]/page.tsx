import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import DayNav from '@/app/components/DayNav';
import RatingStars from '@/app/components/RatingStars';
import styles from './page.module.css';

export const revalidate = 3600; // ISR cache por 1 hora

interface PageProps {
  params: Promise<{
    semana: string;
    dia: string;
  }>;
}

export default async function DevocionalPage({ params }: PageProps) {
  const supabase = await createClient();
  const resolvedParams = await params;
  const semana = parseInt(resolvedParams.semana, 10);
  const dia = parseInt(resolvedParams.dia, 10);

  // 1. Busca o ID do plano_devocional cruzando semana/dia
  const { data: plano, error: planoError } = await supabase
    .from('plano_devocional')
    .select('id, texto_biblico, dia_nome, tema_semana, dia_semana')
    .eq('semana', semana)
    .eq('dia_semana', dia)
    .single();

  if (planoError || !plano) {
    return notFound();
  }

  // 2. Busca o conteúdo final aprovado
  const { data: devocional, error: devError } = await supabase
    .from('devocionais_final')
    .select('id, titulo, subtema, conteudo_md, palavras, rating_total, rating_count')
    .eq('plano_id', plano.id)
    .single();

  if (devError || !devocional) {
    return (
      <div className={styles.container}>
        <div className={styles.notReadyBox}>
          <p className={styles.notReadyTitle}>📖 Em processo de maturação</p>
          <p>Esta leitura está sendo preparada com cuidado e zelo teológico. Retorne em breve.</p>
          <Link href="/semanas" className={styles.notReadyLink}>← Voltar ao índice</Link>
        </div>
      </div>
    );
  }

  // 3. Buscar dias adjacentes para a navegação
  const { data: vizinhos } = await supabase
    .from('plano_devocional')
    .select('semana, dia_semana, status, tema_semana')
    .or(
      `and(semana.eq.${semana},dia_semana.eq.${dia - 1}),` +
      `and(semana.eq.${semana},dia_semana.eq.${dia + 1}),` +
      `and(semana.eq.${semana - 1},dia_semana.eq.7),` +
      `and(semana.eq.${semana + 1},dia_semana.eq.1)`
    )
    .eq('status', 'aprovado');

  const anterior = vizinhos?.find(
    (v: any) =>
      (v.semana === semana && v.dia_semana === dia - 1) ||
      (v.semana === semana - 1 && v.dia_semana === 7 && dia === 1)
  );
  const proximo = vizinhos?.find(
    (v: any) =>
      (v.semana === semana && v.dia_semana === dia + 1) ||
      (v.semana === semana + 1 && v.dia_semana === 1 && dia === 7)
  );

  // Extrair verso para o sneak-peak
  const versoSnippet = plano.texto_biblico.split(',')[0];
  const NOME_DIAS = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
  const nomeDiaCorreto = NOME_DIAS[plano.dia_semana - 1] || plano.dia_nome;

  return (
    <>
      <article className={styles.article}>
        <header className={styles.header}>
          <div className={styles.metaRow}>
            <Link href="/semanas" className={styles.backLink}>
              ← Índice
            </Link>
            <span className={styles.weekTag}>
              Semana {semana} · {nomeDiaCorreto}
            </span>
          </div>

          <h1 className={styles.title}>{devocional.titulo}</h1>
          <p className={styles.subtema}>{devocional.subtema}</p>

          <div className={styles.verseBox}>
            <p className={styles.verseText}>"{versoSnippet}"</p>
            <p className={styles.verseRef}>— {plano.texto_biblico}</p>
          </div>
        </header>

        <main className={styles.prose}>
          <ReactMarkdown
            components={{
              h1: ({node, ...props}) => <h2 className={styles.h2} {...props} />,
              h2: ({node, ...props}) => <h2 className={styles.h2} {...props} />,
              h3: ({node, ...props}) => <h3 className={styles.h3} {...props} />,
              p: ({node, ...props}) => <p className={styles.p} {...props} />,
              ul: ({node, ...props}) => <ul className={styles.ul} {...props} />,
              li: ({node, ...props}) => <li className={styles.li} {...props} />,
              blockquote: ({node, ...props}) => <blockquote className={styles.blockquote} {...props} />,
            }}
          >
            {devocional.conteudo_md}
          </ReactMarkdown>
        </main>

        <footer className={styles.footer}>
          <p className={styles.stats}>
            {devocional.palavras} palavras · Aproximadamente {Math.ceil(devocional.palavras / 200)} min de leitura
          </p>
          
          <RatingStars 
            devocionalId={devocional.id} 
            initialTotal={devocional.rating_total || 0}
            initialCount={devocional.rating_count || 0}
          />
          
          <div className={styles.divider}>⁂</div>
        </footer>

        <DayNav
          semanaAtual={semana}
          diaAtual={dia}
          totalDiasSemana={7}
          temAnterior={!!anterior}
          temProximo={!!proximo}
          tituloAnterior={anterior?.tema_semana}
          tituloProximo={proximo?.tema_semana}
        />
      </article>
    </>
  );
}
