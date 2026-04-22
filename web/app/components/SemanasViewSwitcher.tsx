'use client';

import { useState } from 'react';
import Link from 'next/link';
import CalendarView from './CalendarView';
import styles from './SemanasViewSwitcher.module.css';

interface DiaInfo {
  id: string;
  semana: number;
  dia_semana: number;
  dia_nome: string;
  tema_semana: string;
  status: string;
}

export interface TopDevocional {
  titulo: string;
  rating_total: number;
  rating_count: number;
  semana: number;
  dia_semana: number;
  tema_semana: string;
}

interface Props {
  dias: DiaInfo[];
  topDevocionais: TopDevocional[];
}

export default function SemanasViewSwitcher({ dias, topDevocionais }: Props) {
  const [viewMode, setViewMode] = useState<'dashboard' | 'calendar'>('dashboard');

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Trilha da Graça Soberana</h1>
        <p className={styles.subtitle}>
          52 semanas de devocionais reformadas no estilo J.C. Ryle.
          <br />
          Use o <strong>índice lateral</strong> para navegar ou comece pelo devocional de hoje.
        </p>
        
        <div className={styles.viewToggle}>
          <button 
            className={`${styles.toggleBtn} ${viewMode === 'dashboard' ? styles.active : ''}`}
            onClick={() => setViewMode('dashboard')}
          >
            📊 Painel Geral
          </button>
          <button 
            className={`${styles.toggleBtn} ${viewMode === 'calendar' ? styles.active : ''}`}
            onClick={() => setViewMode('calendar')}
          >
            📅 Calendário Anual
          </button>
        </div>
      </header>

      {viewMode === 'dashboard' ? (
        <div className={styles.dashboardView}>
          <div className={styles.actionRow}>
            <Link href="/hoje" className={styles.hojeLink}>
              📖 Ler o Devocional de Hoje
            </Link>
          </div>

          <div className={styles.minhaDevRow}>
            <Link href="/minha-devocional" className={styles.minhaDevBtn}>
              Gerar minha própria devocional
            </Link>
          </div>

          {topDevocionais && topDevocionais.length > 0 && (
            <section className={styles.recentSection}>
              <h2 className={styles.recentTitle}>Devocionais Mais Bem Avaliadas</h2>
              <div className={styles.recentGrid}>
                {topDevocionais.map((dev, idx) => (
                  <Link
                    key={idx}
                    href={`/semanas/${dev.semana}/${dev.dia_semana}`}
                    className={`${styles.recentCard} glass`}
                  >
                    <span className={styles.recentBadge}>
                      {dev.rating_count > 0 
                        ? `★ ${(dev.rating_total / dev.rating_count).toFixed(1)}` 
                        : '★ --'}
                    </span>
                    <h3 className={styles.recentTema}>{dev.titulo}</h3>
                    <span className={styles.recentMeta}>Semana {dev.semana} • Dia {dev.dia_semana}</span>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>
      ) : (
        <CalendarView dias={dias} />
      )}
    </div>
  );
}
