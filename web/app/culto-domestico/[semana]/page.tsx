import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import styles from './page.module.css';

export const revalidate = 60;

interface Props {
  params: Promise<{ semana: string }>;
}

export async function generateMetadata({ params }: Props) {
  const { semana } = await params;
  return {
    title: `Semana ${semana} — Culto Doméstico | Trilha da Graça Soberana`,
    description: `Devocionais da semana ${semana} do plano de 100 dias de culto doméstico.`,
  };
}

export default async function SemanaPage({ params }: Props) {
  const { semana: semanaStr } = await params;
  const semana = parseInt(semanaStr, 10);
  if (isNaN(semana) || semana < 1 || semana > 15) notFound();

  const supabase = await createClient();

  // Load days for this week
  const { data: planoData } = await supabase
    .from('nico_plano')
    .select('dia, semana, dia_semana, ref, versiculo, status')
    .eq('semana', semana)
    .order('dia', { ascending: true });

  if (!planoData || planoData.length === 0) notFound();

  // Load completed devotionals for this week
  const { data: finaisData } = await supabase
    .from('nico_devocionais_final')
    .select('dia, ref, score_final, pergunta_reflexao, palavras')
    .eq('semana', semana)
    .order('dia', { ascending: true });

  const finaisMap = new Map((finaisData || []).map((f: any) => [f.dia, f]));

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <Link href="/culto-domestico" className={styles.backLink}>
          ← Voltar ao plano
        </Link>
        <h1 className={styles.title}>Semana {semana}</h1>
        <p className={styles.subtitle}>
          {planoData.length} devocionais para o culto doméstico
        </p>
      </div>

      <div className={styles.daysGrid}>
        {planoData.map((dia: any) => {
          const final = finaisMap.get(dia.dia);
          const isReady = dia.status === 'aprovado' && final;

          return (
            <div key={dia.dia} className={`${styles.dayCard} glass ${!isReady ? styles.dayLocked : ''}`}>
              <div className={styles.dayHeader}>
                <span className={styles.dayNum}>Dia {dia.dia}</span>
                {isReady && (
                  <span className={styles.scoreTag}>
                    {final.score_final?.toFixed(0)}/100
                  </span>
                )}
                {!isReady && <span className={styles.pendingTag}>⏳</span>}
              </div>

              <h3 className={styles.dayRef}>{dia.ref}</h3>
              <p className={styles.dayVerse}>
                {dia.versiculo.length > 120
                  ? dia.versiculo.substring(0, 120) + '...'
                  : dia.versiculo}
              </p>

              {isReady ? (
                <Link
                  href={`/culto-domestico/${semana}/${dia.dia}`}
                  className={styles.readButton}
                >
                  Ler devocional →
                </Link>
              ) : (
                <span className={styles.comingSoon}>Em breve</span>
              )}
            </div>
          );
        })}
      </div>
    </main>
  );
}
