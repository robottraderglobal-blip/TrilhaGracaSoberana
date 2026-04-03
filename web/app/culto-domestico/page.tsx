import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import styles from '../semanas/page.module.css';
import DevocionaisCarousel from '../components/DevocionaisCarousel';

export const revalidate = 60;

interface DevocionalFinal {
  ref: string;
  score_final: number;
  pergunta_reflexao: string;
  nico_plano: {
    semana: number;
    dia: number;
  };
}

export default async function CultoDomesticoPage() {
  const supabase = await createClient();

  // Count progress
  const { data: planoData } = await supabase
    .from('nico_plano')
    .select('status')
    .order('dia');

  const total = planoData?.length || 0;
  const aprovados = planoData?.filter((d: any) => d.status === 'aprovado').length || 0;

  // Top devotionals
  let topData = null;
  const { data } = await supabase
    .from('nico_devocionais_final')
    .select(`
      ref,
      versiculo,
      score_final,
      pergunta_reflexao,
      nico_plano!inner (
        semana,
        dia
      )
    `);

  if (data) {
    topData = data.sort((a: any, b: any) => a.nico_plano.dia - b.nico_plano.dia);
  }

  return (
    <div>
      <h1 className={styles.title} style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
        Culto Doméstico
      </h1>
      <p className={styles.subtitle} style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
        100 dias de devocionais para o Culto Doméstico.{' '}
        Use o <Link href="/culto-domestico" style={{ color: 'var(--accent-gold)' }}>índice lateral</Link> para navegar.
      </p>

      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <span style={{ 
          fontSize: '0.85rem', 
          color: 'var(--text-secondary)',
          padding: '0.3rem 0.8rem',
          border: '1px solid var(--glass-border)',
          borderRadius: '12px',
        }}>
          {aprovados}/{total} devocionais prontas
        </span>
      </div>

      {topData && topData.length > 0 && (
        <>
          <h2 className={styles.sectionTitle || ''} style={{ 
            fontFamily: 'var(--font-serif)', 
            fontSize: '1.15rem', 
            marginBottom: '1rem',
            textAlign: 'center' 
          }}>
            Devocionais Disponíveis
          </h2>
          {topData && topData.length > 0 ? (
            <DevocionaisCarousel data={topData as any[]} />
          ) : (
            <div className={styles.recentGrid}>
              <p>Carregando devocionais da Trilha Graça Soberana...</p>
            </div>
          )}
        </>
      )}

      {(!topData || topData.length === 0) && (
        <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-secondary)' }}>
          <p style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>📖 Em processo de maturação</p>
          <p>As devocionais estão sendo geradas com cuidado teológico. Volte em breve.</p>
        </div>
      )}
    </div>
  );
}
