import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import styles from '../series.module.css';

export const revalidate = 60;

export default async function SeriePage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params;
  const supabase = await createClient();

  const { data: devocionais, error } = await supabase
    .from('series_devocionais')
    .select('dia, semana, titulo, nome_serie')
    .eq('slug_serie', slug)
    .order('dia', { ascending: true });

  if (error || !devocionais || devocionais.length === 0) {
    notFound();
  }

  // Agrupar por semana
  const grouped: Record<string, typeof devocionais> = {};
  devocionais.forEach(d => {
    if (!grouped[d.semana]) {
      grouped[d.semana] = [];
    }
    grouped[d.semana]!.push(d);
  });

  const nomeSerie = devocionais[0]?.nome_serie;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>{nomeSerie}</h1>
        <p className={styles.subtitle}>
          Um plano devocional de 21 dias focado em aprofundar seu entendimento na Palavra de Deus.
        </p>
      </div>

      <Link href="/series" className={styles.backLink} style={{ marginBottom: '2rem', display: 'inline-block' }}>
        &larr; Ver todas as séries
      </Link>

      {Object.keys(grouped).map(semana => (
        <div key={semana}>
          <h2 className={styles.eixoTitle}>{semana}</h2>
          <div className={styles.grid}>
            {grouped[semana]?.map(d => (
              <Link href={`/series/${slug}/${d.dia}`} key={d.dia} className={styles.card}>
                <span className={styles.cardDia}>Dia {d.dia}</span>
                <span className={styles.cardTitulo}>{d.titulo}</span>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
