import { createClient } from '@/utils/supabase/server';
import Sidebar from '../components/Sidebar';
import styles from './layout.module.css';

export default async function SemanasLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();

  // Buscar todos os dias para a sidebar
  const { data: dias } = await supabase
    .from('plano_devocional')
    .select('id, semana, dia_semana, dia_nome, tema_semana, status')
    .order('semana', { ascending: true })
    .order('dia_semana', { ascending: true });

  return (
    <div className={styles.layoutWrapper}>
      <Sidebar dias={dias || []} />
      <main className={styles.mainContent}>
        {children}
      </main>
    </div>
  );
}
