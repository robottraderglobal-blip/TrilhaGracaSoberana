import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import styles from './series.module.css';

export const revalidate = 60;

export default async function SeriesPage() {
  const supabase = await createClient();

  // Buscar lista de séries únicas
  // Como não há tabela 'series' separada, pegamos os distintos
  const { data: series, error } = await supabase
    .from('series_devocionais')
    .select('slug_serie, nome_serie')
    .order('slug_serie');

  // Filtrar para ficar apenas os únicos (simulando um SELECT DISTINCT)
  const uniqueSeries: Record<string, string> = {};
  if (series) {
    series.forEach(s => {
      uniqueSeries[s.slug_serie] = s.nome_serie;
    });
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Séries Devocionais</h1>
        <p className={styles.subtitle}>
          Explore planos de leitura estruturados para o seu crescimento espiritual e aprofundamento na Palavra.
        </p>
      </div>

      {error && (
        <div style={{ color: 'red', textAlign: 'center', marginBottom: '2rem' }}>
          <p>Erro ao carregar séries.</p>
          <pre style={{ fontSize: '0.8rem', opacity: 0.7 }}>{error.message}</pre>
        </div>
      )}

      <div className={styles.grid}>
        {Object.keys(uniqueSeries).map(slug => (
          <Link href={`/series/${slug}`} key={slug} className={styles.card}>
            <span className={styles.cardTitulo}>{uniqueSeries[slug]}</span>
            <span className={styles.cardDia}>Acessar Trilha &rarr;</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
