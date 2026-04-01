'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';

interface DiaInfo {
  id: string;
  semana: number;
  dia_semana: number;
  dia_nome: string;
  tema_semana: string;
  status: string;
}

export default function Sidebar({ dias }: { dias: DiaInfo[] }) {
  const anoAtual = new Date().getFullYear();
  const primeiroDomingo = new Date(anoAtual, 0, 1);
  while (primeiroDomingo.getDay() !== 0) {
    primeiroDomingo.setDate(primeiroDomingo.getDate() + 1);
  }

  // Agrupar semanas em meses baseando-se no domingo de cada semana
  const MESES = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ];

  // Identifica a qual mês pertence cada semana (1 a 52)
  const getMesDaSemana = (numSemana: number) => {
    const dataSemana = new Date(primeiroDomingo.getTime());
    dataSemana.setDate(primeiroDomingo.getDate() + (numSemana - 1) * 7);
    return dataSemana.getMonth();
  };

  const pathname = usePathname();
  const [openMes, setOpenMes] = useState<number | null>(null);
  const [openSemana, setOpenSemana] = useState<number | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  // Agrupar dias por semana
  const semanasMap = new Map<number, DiaInfo[]>();
  dias.forEach((dia: DiaInfo) => {
    if (!semanasMap.has(dia.semana)) {
      semanasMap.set(dia.semana, []);
    }
    semanasMap.get(dia.semana)?.push(dia);
  });

  // Detectar semana/dia atual pela URL e abrir automaticamente
  useEffect(() => {
    const match = pathname.match(/\/semanas\/(\d+)\/(\d+)/);
    if (match) {
      const semanaAtual = parseInt(match[1], 10);
      setOpenMes(getMesDaSemana(semanaAtual));
      setOpenSemana(semanaAtual);
    }
  }, [pathname]);

  // Fechar sidebar mobile ao navegar
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const toggleMes = (idx: number) => {
    setOpenMes(openMes === idx ? null : idx);
  };

  const toggleSemana = (num: number) => {
    setOpenSemana(openSemana === num ? null : num);
  };

  return (
    <>
      <button
        className={styles.mobileToggle}
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Abrir índice"
      >
        <span className={styles.toggleIcon}>{mobileOpen ? '✕' : '☰'}</span>
        <span className={styles.toggleLabel}>Índice</span>
      </button>

      {mobileOpen && (
        <div
          className={styles.overlay}
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside className={`${styles.sidebar} ${mobileOpen ? styles.open : ''}`}>
        <div className={styles.sidebarHeader}>
          <h2 className={styles.sidebarTitle}>Índice</h2>
          <Link href="/hoje" prefetch={false} className={styles.hojeButton}>
            📖 Hoje
          </Link>
        </div>

        <nav className={styles.nav}>
          {MESES.map((nomeMes, mesIdx) => {
            const isMesOpen = openMes === mesIdx;
            
            // Encontrar as semanas que pertencem a este mês
            const semanasNoMes = Array.from(semanasMap.keys())
              .filter((s) => getMesDaSemana(s) === mesIdx)
              .sort((a, b) => a - b);

            if (semanasNoMes.length === 0) return null;

            const totalAprovados = semanasNoMes.reduce((acc, s) => {
              const diasSemana = semanasMap.get(s) || [];
              return acc + diasSemana.filter((d) => d.status === 'aprovado').length;
            }, 0);
            const totalDias = semanasNoMes.length * 7;

            return (
              <div key={mesIdx} className={styles.trimestreBlock}>
                <button
                  className={`${styles.trimestreBtn} ${isMesOpen ? styles.active : ''}`}
                  onClick={() => toggleMes(mesIdx)}
                >
                  <span className={styles.trimestreLabel}>
                    <span className={styles.chevron}>{isMesOpen ? '▾' : '▸'}</span>
                    {nomeMes}
                  </span>
                  <span className={styles.trimestreCount}>
                    {totalAprovados}/{totalDias}
                  </span>
                </button>

                {isMesOpen && (
                  <div className={styles.semanasContainer}>
                    {semanasNoMes.map((semanaNum) => {
                      const diasSemana = semanasMap.get(semanaNum) || [];
                      const tema = diasSemana[0]?.tema_semana || '';
                      const isSemanaOpen = openSemana === semanaNum;
                      const aprovadosSemana = diasSemana.filter(
                        (d) => d.status === 'aprovado'
                      ).length;

                      return (
                        <div key={semanaNum} className={styles.semanaBlock}>
                          <button
                            className={`${styles.semanaBtn} ${isSemanaOpen ? styles.semanaActive : ''}`}
                            onClick={() => toggleSemana(semanaNum)}
                          >
                            <span className={styles.semanaInfo}>
                              <span className={styles.semanaNum}>S{semanaNum}</span>
                              <span className={styles.semanaTema}>{tema}</span>
                            </span>
                            <span className={styles.semanaProgress}>
                              {aprovadosSemana > 0 && (
                                <span className={styles.progressDots}>
                                  {diasSemana.map((d, i) => (
                                    <span
                                      key={i}
                                      className={`${styles.dot} ${d.status === 'aprovado' ? styles.dotActive : ''}`}
                                    />
                                  ))}
                                </span>
                              )}
                            </span>
                          </button>

                          {isSemanaOpen && (
                            <div className={styles.diasContainer}>
                              {diasSemana.map((dia: DiaInfo) => {
                                const isAprovado = dia.status === 'aprovado';
                                const isCurrentPage =
                                  pathname === `/semanas/${semanaNum}/${dia.dia_semana}`;
                                const NOME_DIAS = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
                                const nomeDiaCorreto = NOME_DIAS[dia.dia_semana - 1] || dia.dia_nome;

                                return isAprovado ? (
                                  <Link
                                    href={`/semanas/${semanaNum}/${dia.dia_semana}`}
                                    key={dia.id}
                                    className={`${styles.diaItem} ${isCurrentPage ? styles.diaCurrent : ''}`}
                                  >
                                    <span className={styles.diaNum}>Dia {dia.dia_semana}</span>
                                    <span className={styles.diaNome}>{nomeDiaCorreto}</span>
                                    {isCurrentPage && <span className={styles.currentDot} />}
                                  </Link>
                                ) : (
                                  <div
                                    key={dia.id}
                                    className={`${styles.diaItem} ${styles.diaDisabled}`}
                                  >
                                    <span className={styles.diaNum}>Dia {dia.dia_semana}</span>
                                    <span className={styles.diaNome}>{nomeDiaCorreto}</span>
                                    <span className={styles.diaStatus}>Em breve</span>
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </nav>

        {/* Progresso global */}
        <div className={styles.globalProgress}>
          <div className={styles.progressLabel}>
            Progresso Geral
          </div>
          <div className={styles.progressBar}>
            <div
              className={styles.progressFill}
              style={{
                width: `${(dias.filter((d: DiaInfo) => d.status === 'aprovado').length / Math.max(dias.length, 1)) * 100}%`,
              }}
            />
          </div>
          <div className={styles.progressText}>
            {dias.filter((d: DiaInfo) => d.status === 'aprovado').length} de {dias.length} devocionais
          </div>
        </div>
      </aside>
    </>
  );
}
