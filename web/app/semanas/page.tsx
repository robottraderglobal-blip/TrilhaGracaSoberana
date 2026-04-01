import { createClient } from '@/utils/supabase/server';
import SemanasViewSwitcher, { TopDevocional } from '../components/SemanasViewSwitcher';

export const revalidate = 60;

export default async function SemanasPage() {
  const supabase = await createClient();

  // Load all days for the calendar view
  const { data: planoArray } = await supabase
    .from('plano_devocional')
    .select('id, semana, dia_semana, dia_nome, tema_semana, status')
    .order('semana', { ascending: true })
    .order('dia_semana', { ascending: true });

  const dias = planoArray || [];

  // Load top rated devotionals
  const { data: topData } = await supabase
    .from('devocionais_final')
    .select(`
      titulo,
      rating_total,
      rating_count,
      plano_devocional!inner (
        semana,
        dia_semana,
        tema_semana
      )
    `)
    .order('rating_total', { ascending: false })
    .limit(6);

  const topDevocionais: TopDevocional[] = (topData || []).map((d: any) => ({
    titulo: d.titulo,
    rating_total: d.rating_total,
    rating_count: d.rating_count,
    semana: d.plano_devocional.semana,
    dia_semana: d.plano_devocional.dia_semana,
    tema_semana: d.plano_devocional.tema_semana
  }));

  return (
    <SemanasViewSwitcher 
      dias={dias} 
      topDevocionais={topDevocionais} 
    />
  );
}
