import { createClient } from '@/utils/supabase/server';
import NicoSidebar from '../components/NicoSidebar';
import styles from '../semanas/layout.module.css';

export const metadata = {
  title: 'Culto Doméstico — 100 Dias | Trilha da Graça Soberana',
  description: 'Devocionais para culto doméstico no estilo de Augustus Nicodemus. 100 dias de meditação bíblica em família.',
};

export default async function CultoDomesticoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();

  const { data: dias } = await supabase
    .from('nico_plano')
    .select('id, semana, dia, dia_semana, ref, status')
    .order('dia', { ascending: true });

  return (
    <div className={styles.layoutWrapper}>
      <NicoSidebar dias={dias || []} />
      <main className={styles.mainContent}>
        {children}
      </main>
    </div>
  );
}
