import { redirect } from 'next/navigation';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default function HojePage() {
  const agora = new Date();
  // Zera as horas para meia-noite local para cálculo de dias limpo
  const hoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
  
  const anoAtual = hoje.getFullYear();
  
  // Encontrar o Primeiro Domingo do ano atual
  const primeiroDomingo = new Date(anoAtual, 0, 1);
  while (primeiroDomingo.getDay() !== 0) {
    primeiroDomingo.setDate(primeiroDomingo.getDate() + 1);
  }

  // Diferença em ms com as duas datas alinhadas em meia-noite
  const diffMs = hoje.getTime() - primeiroDomingo.getTime();
  
  // Se ainda estivermos nos dias "limbo" antes do primeiro domingo
  if (diffMs < 0) {
    redirect('/semanas/1/1');
  }

  // Usamos Math.round em vez de floor para evitar o bug do horário de verão (-1h) subtraindo 1 dia inteiro
  const diffDias = Math.round(diffMs / (1000 * 60 * 60 * 24));

  const semana = Math.min(Math.floor(diffDias / 7) + 1, 52);
  const diaSemana = (diffDias % 7) + 1;

  redirect(`/semanas/${semana}/${diaSemana}`);
}
