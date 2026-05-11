import { createClient } from '@/utils/supabase/server';
import Link from 'next/link';
import styles from './cordeiro.module.css';

export const revalidate = 60;

export default async function CordeiroPage() {
  const supabase = await createClient();

  const { data: devocionais, error } = await supabase
    .from('cordeiro_devocionais')
    .select('dia, eixo, titulo')
    .order('dia', { ascending: true });

  // Group by eixo
  const grouped: Record<string, typeof devocionais> = {};
  
  if (devocionais) {
    devocionais.forEach(d => {
      if (!grouped[d.eixo]) {
        grouped[d.eixo] = [];
      }
      grouped[d.eixo]!.push(d);
    });
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>O Cordeiro na Bíblia</h1>
        <p className={styles.subtitle}>
          Um plano devocional de 28 dias focado na revelação de Cristo como o <strong>Cordeiro de Deus</strong>, de Gênesis a Apocalipse.
        </p>
      </div>

      {error && (
        <div style={{ color: 'red', textAlign: 'center', marginBottom: '2rem' }}>
          <p>Erro ao carregar devocionais. Você já executou o SQL no Supabase?</p>
          <pre style={{ fontSize: '0.8rem', opacity: 0.7 }}>{error.message}</pre>
        </div>
      )}

      {Object.keys(grouped).map(eixo => (
        <div key={eixo}>
          <h2 className={styles.eixoTitle}>{eixo}</h2>
          <div className={styles.grid}>
            {grouped[eixo]?.map(d => (
              <Link href={`/cordeiro/${d.dia}`} key={d.dia} className={styles.card}>
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
