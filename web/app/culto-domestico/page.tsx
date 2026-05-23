import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import styles from '../semanas/page.module.css';
import DevocionaisCarousel from '../components/DevocionaisCarousel';

export const revalidate = 60;

interface PlanoDia {
  id: string;
  semana: number;
  dia: number;
  ref: string;
  status: string;
}

interface TopDevocional {
  ref: string;
  versiculo: string;
  score_final: number;
  pergunta_reflexao: string;
  nico_plano: {
    semana: number;
    dia: number;
  };
}

export default async function CultoDomesticoPage() {
  const supabase = await createClient();

  // Count progress and load all days
  const { data: rawPlanoData } = await supabase
    .from('nico_plano')
    .select('id, semana, dia, ref, status')
    .order('dia');

  const planoData = (rawPlanoData || []) as PlanoDia[];
  const total = planoData.length;
  const aprovados = planoData.filter((d) => d.status === 'aprovado').length;

  // Top devotionals for the Carousel
  let topData: TopDevocional[] = [];
  const { data: rawDevocionaisData } = await supabase
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

  if (rawDevocionaisData) {
    const formattedData = (rawDevocionaisData as unknown) as TopDevocional[];
    topData = formattedData.sort((a, b) => a.nico_plano.dia - b.nico_plano.dia);
  }

  // Group planoData by week (semana)
  const semanasMap: Record<number, PlanoDia[]> = {};
  planoData.forEach((p) => {
    if (!semanasMap[p.semana]) {
      semanasMap[p.semana] = [];
    }
    semanasMap[p.semana].push(p);
  });

  const semanasOrdenadas = Object.keys(semanasMap)
    .map(Number)
    .sort((a, b) => a - b);

  return (
    <div style={{ paddingBottom: '4rem' }}>
      <h1 className={styles.title} style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
        Culto Doméstico
      </h1>
      <p className={styles.subtitle} style={{ textAlign: 'center', marginBottom: '1.5rem', maxWidth: '600px', margin: '0 auto 1.5rem', lineHeight: '1.6' }}>
        Uma jornada de versículos essenciais selecionados para meditação em família. Estude e memorize a Palavra no seu{' '}
        <span style={{ color: 'var(--accent-gold)' }}>Culto Doméstico</span>.
      </p>

      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <span style={{ 
          fontSize: '0.85rem', 
          color: 'var(--text-secondary)',
          padding: '0.3rem 0.8rem',
          border: '1px solid var(--glass-border)',
          borderRadius: '12px',
          background: 'rgba(255,255,255,0.02)',
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
            Devocionais Recentes
          </h2>
          <DevocionaisCarousel data={(topData as unknown) as any[]} />
        </>
      )}

      {/* Seção de Navegação por Semanas */}
      {semanasOrdenadas.length > 0 && (
        <div style={{ marginTop: '3.5rem', width: '100%', maxWidth: '800px', margin: '3.5rem auto 0' }}>
          <h2 style={{ 
            fontFamily: 'var(--font-serif)', 
            fontSize: '1.35rem', 
            marginBottom: '1.5rem',
            textAlign: 'left',
            borderBottom: '1px solid var(--glass-border)',
            paddingBottom: '0.5rem',
            color: 'var(--text-primary)'
          }}>
            Navegação por Semanas
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {semanasOrdenadas.map((semanaNum) => {
              const diasSemana = semanasMap[semanaNum];
              const aprovadosSemana = diasSemana.filter((d) => d.status === 'aprovado').length;
              const totalSemana = diasSemana.length;
              
              return (
                <details 
                  key={semanaNum}
                  className="weekAccordion"
                  style={{
                    background: 'var(--glass-bg)',
                    border: '1px solid var(--glass-border)',
                    borderRadius: '12px',
                    padding: '1rem',
                    backdropFilter: 'blur(8px)',
                  }}
                >
                  <summary style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    fontWeight: 600,
                    fontSize: '1.05rem',
                    listStyle: 'none',
                    WebkitUserSelect: 'none',
                    userSelect: 'none',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span style={{ fontSize: '0.7rem' }}>▶</span>
                      <span>Semana {semanaNum}</span>
                    </div>
                    <span style={{ 
                      fontSize: '0.75rem', 
                      color: 'var(--text-secondary)',
                      background: 'rgba(255,255,255,0.02)',
                      padding: '0.2rem 0.6rem',
                      borderRadius: '8px',
                      border: '1px solid var(--glass-border)'
                    }}>
                      {aprovadosSemana}/{totalSemana} devocionais
                    </span>
                  </summary>
                  
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', 
                    gap: '0.6rem',
                    marginTop: '1rem',
                    borderTop: '1px solid rgba(255,255,255,0.05)',
                    paddingTop: '0.85rem'
                  }}>
                    {diasSemana.map((dia) => {
                      const isAprovado = dia.status === 'aprovado';
                      
                      return isAprovado ? (
                        <Link 
                          key={dia.id}
                          href={`/culto-domestico/${dia.semana}/${dia.dia}`}
                          className="dayCardHover"
                          style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            padding: '0.65rem 0.4rem',
                            borderRadius: '8px',
                            border: '1px solid var(--glass-border)',
                            background: 'rgba(255,255,255,0.01)',
                            textAlign: 'center',
                          }}
                        >
                          <span style={{ 
                            fontSize: '0.7rem', 
                            fontWeight: 700, 
                            color: 'var(--accent-gold)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                            marginBottom: '0.15rem'
                          }}>
                            Dia {dia.dia}
                          </span>
                          <span style={{ 
                            fontSize: '0.75rem', 
                            color: 'var(--text-primary)',
                            fontWeight: 500,
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            width: '100%',
                            padding: '0 0.2rem'
                          }} title={dia.ref}>
                            {dia.ref}
                          </span>
                        </Link>
                      ) : (
                        <div 
                          key={dia.id}
                          style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            padding: '0.65rem 0.4rem',
                            borderRadius: '8px',
                            border: '1px solid var(--glass-border)',
                            background: 'rgba(0,0,0,0.15)',
                            textAlign: 'center',
                            opacity: 0.35,
                          }}
                        >
                          <span style={{ 
                            fontSize: '0.7rem', 
                            fontWeight: 700, 
                            color: 'var(--text-secondary)',
                            marginBottom: '0.15rem'
                          }}>
                            Dia {dia.dia}
                          </span>
                          <span style={{ 
                            fontSize: '0.7rem', 
                            color: 'var(--text-secondary)',
                          }}>
                            Em breve
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </details>
              );
            })}
          </div>
        </div>
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
