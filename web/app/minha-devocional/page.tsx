import type { Metadata } from 'next';
import MinhaDevocionalClient from './MinhaDevocionalClient';

export const metadata: Metadata = {
  title: 'Minha Devocional — Trilha da Graça Soberana',
  description:
    'Gere sua própria devocional personalizada. Informe um tema ou passagem e receba uma meditação bíblica no estilo J.C. Ryle com análise exegética reformada.',
};

export default function MinhaDevocionalPage() {
  return <MinhaDevocionalClient />;
}
