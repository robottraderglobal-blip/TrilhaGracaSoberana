'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';

interface NicoDia {
  id: string;
  semana: number;
  dia: number;
  dia_semana: number;
  ref: string;
  status: string;
}

const TEMAS_SEMANAS = [
  "A Majestade de Deus",             // Semana 1
  "A Providência e o Cuidado",       // Semana 2
  "A Queda e o Pecado",              // Semana 3
  "A Necessidade de Redenção",       // Semana 4
  "A Encarnação e Vida de Cristo",   // Semana 5 // Placeholder themes
  "A Cruz e o Sacrifício",           // Semana 6
  "A Ressurreição de Jesus",         // Semana 7
  "Justificação e Fé",               // Semana 8
  "A Obra do Espírito Santo",        // Semana 9
  "A Adoção e Identidade",           // Semana 10
  "Santificação Diária",             // Semana 11
  "A Igreja e a Comunhão",           // Semana 12
  "O Culto e a Oração",              // Semana 13
  "Provação e Perseverança",         // Semana 14
  "A Esperança na Glória"            // Semana 15
];

export default function NicoSidebar({ dias }: { dias: NicoDia[] }) {
  const pathname = usePathname();
  const [openSemana, setOpenSemana] = useState<number | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  // Agrupar dias por semana
  const semanasMap = new Map<number, NicoDia[]>();
  dias.forEach((dia) => {
    if (!semanasMap.has(dia.semana)) semanasMap.set(dia.semana, []);
    semanasMap.get(dia.semana)?.push(dia);
  });

  // Detectar semana/dia atual pela URL
  useEffect(() => {
    const match = pathname.match(/\/culto-domestico\/(\d+)/);
    if (match) setOpenSemana(parseInt(match[1], 10));
  }, [pathname]);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const toggleSemana = (num: number) => {
    setOpenSemana(openSemana === num ? null : num);
  };

  const totalAprovados = dias.filter(d => d.status === 'aprovado').length;

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
          <h2 className={styles.sidebarTitle}>Culto Doméstico</h2>
          <Link href="/culto-domestico" prefetch={false} className={styles.hojeButton}>
            📖 Início
          </Link>
        </div>

        <nav className={styles.nav}>
          {Array.from(semanasMap.entries())
            .sort(([a], [b]) => a - b)
            .map(([semanaNum, diasSemana]) => {
              const isSemanaOpen = openSemana === semanaNum;
              const aprovadosSemana = diasSemana.filter(d => d.status === 'aprovado').length;

              return (
                <div key={semanaNum} className={styles.semanaBlock}>
                  <button
                    className={`${styles.semanaBtn} ${isSemanaOpen ? styles.semanaActive : ''}`}
                    onClick={() => toggleSemana(semanaNum)}
                  >
                    <span className={styles.semanaInfo}>
                      <span className={styles.semanaNum}>S{semanaNum}</span>
                      <span className={styles.semanaTema}>
                        {TEMAS_SEMANAS[semanaNum - 1] || `Semana ${semanaNum}`}
                      </span>
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
                      {diasSemana
                        .sort((a, b) => a.dia - b.dia)
                        .map((dia) => {
                          const isAprovado = dia.status === 'aprovado';
                          const isCurrentPage =
                            pathname === `/culto-domestico/${semanaNum}/${dia.dia}`;

                          return isAprovado ? (
                            <Link
                              href={`/culto-domestico/${semanaNum}/${dia.dia}`}
                              key={dia.id}
                              className={`${styles.diaItem} ${isCurrentPage ? styles.diaCurrent : ''}`}
                            >
                              <span className={styles.diaNum}>Dia {dia.dia}</span>
                              <span className={styles.diaNome}>{dia.ref}</span>
                              {isCurrentPage && <span className={styles.currentDot} />}
                            </Link>
                          ) : (
                            <div
                              key={dia.id}
                              className={`${styles.diaItem} ${styles.diaDisabled}`}
                            >
                              <span className={styles.diaNum}>Dia {dia.dia}</span>
                              <span className={styles.diaNome}>{dia.ref}</span>
                              <span className={styles.diaStatus}>Em breve</span>
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
          <div className={styles.progressLabel}>Progresso Geral</div>
          <div className={styles.progressBar}>
            <div
              className={styles.progressFill}
              style={{
                width: `${(totalAprovados / Math.max(dias.length, 1)) * 100}%`,
              }}
            />
          </div>
          <div className={styles.progressText}>
            {totalAprovados} de {dias.length} devocionais
          </div>
        </div>
      </aside>
    </>
  );
}
