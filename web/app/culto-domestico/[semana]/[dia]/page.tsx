import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import DayNav from '@/app/components/DayNav';
import styles from '../../../semanas/[semana]/[dia]/page.module.css';

export const revalidate = 60;

interface PageProps {
  params: Promise<{
    semana: string;
    dia: string;
  }>;
}

export async function generateMetadata({ params }: PageProps) {
  const { semana, dia } = await params;
  const supabase = await createClient();
  const { data } = await supabase
    .from('nico_devocionais_final')
    .select('ref')
    .eq('dia', parseInt(dia, 10))
    .maybeSingle();

  const ref = data?.ref || `Dia ${dia}`;
  return {
    title: `${ref} — Dia ${dia} | Culto Doméstico`,
    description: `Devocional do dia ${dia} — ${ref}. Meditação bíblica para o culto doméstico.`,
  };
}

export default async function NicoDevocionalPage({ params }: PageProps) {
  const supabase = await createClient();
  const resolvedParams = await params;
  const semana = parseInt(resolvedParams.semana, 10);
  const dia = parseInt(resolvedParams.dia, 10);

  // 1. Buscar plano
  const { data: plano, error: planoError } = await supabase
    .from('nico_plano')
    .select('id, ref, versiculo, dia, semana, dia_semana')
    .eq('dia', dia)
    .single();

  if (planoError || !plano) return notFound();

  // 2. Buscar devocional final
  const { data: devocional, error: devError } = await supabase
    .from('nico_devocionais_final')
    .select('id, ref, conteudo_md, palavras, score_final, pergunta_reflexao, versiculo')
    .eq('plano_id', plano.id)
    .single();

  if (devError || !devocional) {
    return (
      <div className={styles.container}>
        <div className={styles.notReadyBox}>
          <p className={styles.notReadyTitle}>📖 Em processo de maturação</p>
          <p>Esta leitura está sendo preparada com cuidado e zelo teológico. Retorne em breve.</p>
          <Link href="/culto-domestico" className={styles.notReadyLink}>← Voltar ao índice</Link>
        </div>
      </div>
    );
  }

  // 3. Buscar adjacentes para navegação
  const { data: prevData } = await supabase
    .from('nico_plano')
    .select('dia, semana, ref, status')
    .lt('dia', dia)
    .eq('status', 'aprovado')
    .order('dia', { ascending: false })
    .limit(1)
    .maybeSingle();

  const { data: nextData } = await supabase
    .from('nico_plano')
    .select('dia, semana, ref, status')
    .gt('dia', dia)
    .eq('status', 'aprovado')
    .order('dia', { ascending: true })
    .limit(1)
    .maybeSingle();

  return (
    <>
      <article className={styles.article}>
        <header className={styles.header}>
          <div className={styles.metaRow}>
            <Link href="/culto-domestico" className={styles.backLink}>
              ← Índice
            </Link>
            <span className={styles.weekTag}>
              Semana {semana} · Dia {dia}
            </span>
          </div>

          <h1 className={styles.title}>{devocional.ref}</h1>
        </header>

        {/* Versículo em destaque */}
        {devocional.versiculo && (
          <blockquote className={styles.blockquote}>
            <p style={{ margin: 0 }}>
              "{devocional.versiculo}"
            </p>
            <p style={{
              margin: '1rem 0 0',
              fontWeight: 700,
              fontStyle: 'normal',
              fontSize: '0.9rem',
              color: 'var(--text-primary)',
            }}>
              — {devocional.ref} (ARA)
            </p>
          </blockquote>
        )}

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

        {/* Pergunta de reflexão */}
        {devocional.pergunta_reflexao && (
          <div style={{
            margin: '2rem 0',
            padding: '1.2rem 1.5rem',
            borderLeft: '3px solid var(--accent-gold)',
            background: 'var(--accent-gold-dim)',
            borderRadius: '0 8px 8px 0',
          }}>
            <p style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '0.8rem',
              fontWeight: 700,
              color: 'var(--accent-gold)',
              marginBottom: '0.4rem',
              letterSpacing: '0.05em',
            }}>
              💬 PERGUNTA PARA REFLEXÃO
            </p>
            <p style={{
              fontFamily: 'var(--font-serif)',
              fontSize: '1rem',
              fontStyle: 'italic',
              lineHeight: 1.6,
            }}>
              {devocional.pergunta_reflexao}
            </p>
          </div>
        )}

        <footer className={styles.footer}>
          <p className={styles.stats}>
            {devocional.palavras} palavras · Aproximadamente {Math.ceil(devocional.palavras / 200)} min de leitura
          </p>
          <div className={styles.divider}>⁂</div>
        </footer>

        <nav style={{
          display: 'flex',
          justifyContent: 'space-between',
          padding: '1.5rem 0',
          borderTop: '1px solid var(--glass-border)',
        }}>
          {prevData ? (
            <Link
              href={`/culto-domestico/${prevData.semana}/${prevData.dia}`}
              style={{ fontSize: '0.9rem', color: 'var(--accent-gold)', fontWeight: 600 }}
            >
              ← Dia {prevData.dia}
            </Link>
          ) : <span />}
          {nextData ? (
            <Link
              href={`/culto-domestico/${nextData.semana}/${nextData.dia}`}
              style={{ fontSize: '0.9rem', color: 'var(--accent-gold)', fontWeight: 600 }}
            >
              Dia {nextData.dia} →
            </Link>
          ) : <span />}
        </nav>
      </article>
    </>
  );
}
