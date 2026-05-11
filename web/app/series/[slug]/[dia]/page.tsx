import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import styles from '../../series.module.css';

export const revalidate = 60;

export default async function SerieDiaPage({
  params,
}: {
  params: Promise<{ slug: string; dia: string }>
}) {
  const { slug, dia } = await params;
  const diaNum = parseInt(dia, 10);
  
  if (isNaN(diaNum)) {
    notFound();
  }

  const supabase = await createClient();

  const { data: devocional, error } = await supabase
    .from('series_devocionais')
    .select('*')
    .eq('slug_serie', slug)
    .eq('dia', diaNum)
    .single();

  if (error || !devocional) {
    notFound();
  }

  // Buscar total de dias para esta série
  const { count } = await supabase
    .from('series_devocionais')
    .select('id', { count: 'exact', head: true })
    .eq('slug_serie', slug);

  const maxDia = count || 21; // fallback para 21 caso a contagem falhe

  // Usamos uma função auxiliar para remover barras invertidas de escape do Mammoth (\)
  // que podem poluir títulos curtos ou referências
  const cleanEscapes = (text: string) => text.replace(/\\([.\-()])/g, '$1');

  return (
    <div className={styles.container} style={{ maxWidth: '800px' }}>
      <Link href={`/series/${slug}`} className={styles.backLink}>
        &larr; Voltar para o Plano
      </Link>

      <div className={styles.detailHeader}>
        <span className={styles.detailBadge}>Dia {devocional.dia} • {cleanEscapes(devocional.semana)}</span>
        <h1 className={styles.title}><ReactMarkdown components={{ p: ({node, ...props}) => <span {...props} /> }}>{cleanEscapes(devocional.titulo)}</ReactMarkdown></h1>
      </div>

      <div className={styles.versiculoBox}>
        <div className={styles.versiculoText}>
          <ReactMarkdown components={{ p: ({node, ...props}) => <span {...props} /> }}>{`"${cleanEscapes(devocional.versiculo)}"`}</ReactMarkdown>
        </div>
        <div className={styles.versiculoRef}>
          <ReactMarkdown components={{ p: ({node, ...props}) => <span {...props} /> }}>{`— ${cleanEscapes(devocional.referencia)}`}</ReactMarkdown>
        </div>
      </div>

      <div className={styles.conteudo}>
        <ReactMarkdown>{cleanEscapes(devocional.conteudo)}</ReactMarkdown>
      </div>

      <div className={styles.perguntaBox}>
        <div className={styles.perguntaTitle}>Para Refletir</div>
        <div className={styles.perguntaText}>
          <ReactMarkdown components={{ p: ({node, ...props}) => <span {...props} /> }}>{cleanEscapes(devocional.pergunta)}</ReactMarkdown>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4rem', borderTop: '1px solid var(--glass-border)', paddingTop: '2rem' }}>
        {diaNum > 1 ? (
          <Link href={`/series/${slug}/${diaNum - 1}`} className={styles.backLink} style={{ marginBottom: 0 }}>
            &larr; Dia {diaNum - 1}
          </Link>
        ) : <div />}
        
        {diaNum < maxDia && (
          <Link href={`/series/${slug}/${diaNum + 1}`} className={styles.backLink} style={{ marginBottom: 0 }}>
            Dia {diaNum + 1} &rarr;
          </Link>
        )}
      </div>
    </div>
  );
}
