import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import styles from '../cordeiro.module.css';

export const revalidate = 60;

export default async function CordeiroDiaPage({
  params,
}: {
  params: Promise<{ dia: string }>
}) {
  const { dia } = await params;
  const diaNum = parseInt(dia, 10);
  
  if (isNaN(diaNum)) {
    notFound();
  }

  const supabase = await createClient();

  const { data: devocional, error } = await supabase
    .from('cordeiro_devocionais')
    .select('*')
    .eq('dia', diaNum)
    .single();

  if (error || !devocional) {
    notFound();
  }

  // Format content (assuming paragraphs are separated by \n\n)
  const paragraphs = devocional.conteudo.split('\n\n').filter((p: string) => p.trim() !== '');

  return (
    <div className={styles.container} style={{ maxWidth: '800px' }}>
      <Link href="/cordeiro" className={styles.backLink}>
        &larr; Voltar para o Plano
      </Link>

      <div className={styles.detailHeader}>
        <span className={styles.detailBadge}>Dia {devocional.dia} • {devocional.eixo}</span>
        <h1 className={styles.title}>{devocional.titulo}</h1>
      </div>

      <div className={styles.versiculoBox}>
        <div className={styles.versiculoText}>"{devocional.versiculo}"</div>
        <div className={styles.versiculoRef}>— {devocional.referencia}</div>
      </div>

      <div className={styles.conteudo}>
        {paragraphs.map((p: string, i: number) => (
          <p key={i}>{p}</p>
        ))}
      </div>

      <div className={styles.perguntaBox}>
        <div className={styles.perguntaTitle}>Para Refletir</div>
        <div className={styles.perguntaText}>{devocional.pergunta}</div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4rem', borderTop: '1px solid var(--glass-border)', paddingTop: '2rem' }}>
        {diaNum > 1 ? (
          <Link href={`/cordeiro/${diaNum - 1}`} className={styles.backLink} style={{ marginBottom: 0 }}>
            &larr; Dia {diaNum - 1}
          </Link>
        ) : <div />}
        
        {diaNum < 28 && (
          <Link href={`/cordeiro/${diaNum + 1}`} className={styles.backLink} style={{ marginBottom: 0 }}>
            Dia {diaNum + 1} &rarr;
          </Link>
        )}
      </div>
    </div>
  );
}
