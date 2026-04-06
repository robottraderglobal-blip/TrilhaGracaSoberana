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

// Ordem canônica dos livros da Bíblia
const ORDEM_CANONICA: Record<string, number> = {
  'Gênesis': 1, 'Êxodo': 2, 'Levítico': 3, 'Números': 4, 'Deuteronômio': 5,
  'Josué': 6, 'Juízes': 7, 'Rute': 8, '1 Samuel': 9, '2 Samuel': 10,
  '1 Reis': 11, '2 Reis': 12, '1 Crônicas': 13, '2 Crônicas': 14,
  'Esdras': 15, 'Neemias': 16, 'Ester': 17, 'Jó': 18,
  'Salmos': 19, 'Provérbios': 20, 'Eclesiastes': 21, 'Cantares': 22,
  'Isaías': 23, 'Jeremias': 24, 'Lamentações': 25, 'Ezequiel': 26, 'Daniel': 27,
  'Oséias': 28, 'Joel': 29, 'Amós': 30, 'Obadias': 31, 'Jonas': 32,
  'Miquéias': 33, 'Naum': 34, 'Habacuque': 35, 'Sofonias': 36, 'Ageu': 37,
  'Zacarias': 38, 'Malaquias': 39,
  'Mateus': 40, 'Marcos': 41, 'Lucas': 42, 'João': 43, 'Atos': 44,
  'Romanos': 45, '1 Coríntios': 46, '2 Coríntios': 47, 'Gálatas': 48,
  'Efésios': 49, 'Filipenses': 50, 'Colossenses': 51,
  '1 Tessalonicenses': 52, '2 Tessalonicenses': 53,
  '1 Timóteo': 54, '2 Timóteo': 55, 'Tito': 56, 'Filemom': 57,
  'Hebreus': 58, 'Tiago': 59, '1 Pedro': 60, '2 Pedro': 61,
  '1 João': 62, '2 João': 63, '3 João': 64, 'Judas': 65, 'Apocalipse': 66,
};

function extrairLivro(ref: string): string {
  // Remove chapter:verse do final, ex: "1 Crônicas 16.34" → "1 Crônicas"
  return ref.replace(/\s+\d+[.:].+$/, '');
}

function extrairCapVerso(ref: string): [number, number] {
  // Extrai capítulo e versículo, ex: "Salmos 100.4" → [100, 4], "Romanos 4.20-21" → [4, 20]
  const match = ref.match(/(\d+)[.:](\d+)/);
  if (match) return [parseInt(match[1], 10), parseInt(match[2], 10)];
  return [0, 0];
}

function sortByCapVerso(a: NicoDia, b: NicoDia): number {
  const [capA, versoA] = extrairCapVerso(a.ref);
  const [capB, versoB] = extrairCapVerso(b.ref);
  if (capA !== capB) return capA - capB;
  return versoA - versoB;
}

export default function NicoSidebar({ dias }: { dias: NicoDia[] }) {
  const pathname = usePathname();
  const [openLivro, setOpenLivro] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  // Agrupar dias por livro da Bíblia
  const livrosMap = new Map<string, NicoDia[]>();
  dias.forEach((dia) => {
    const livro = extrairLivro(dia.ref);
    if (!livrosMap.has(livro)) livrosMap.set(livro, []);
    livrosMap.get(livro)?.push(dia);
  });

  // Ordenar livros na ordem canônica
  const livrosOrdenados = Array.from(livrosMap.entries()).sort(([a], [b]) => {
    return (ORDEM_CANONICA[a] || 99) - (ORDEM_CANONICA[b] || 99);
  });

  // Detectar livro atual pela URL
  useEffect(() => {
    const match = pathname.match(/\/culto-domestico\/(\d+)\/(\d+)/);
    if (match) {
      const semana = parseInt(match[1], 10);
      const dia = parseInt(match[2], 10);
      const diaAtual = dias.find(d => d.semana === semana && d.dia === dia);
      if (diaAtual) {
        setOpenLivro(extrairLivro(diaAtual.ref));
      }
    }
  }, [pathname, dias]);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const toggleLivro = (livro: string) => {
    setOpenLivro(openLivro === livro ? null : livro);
  };

  const totalAprovados = dias.filter(d => d.status === 'aprovado').length;

  // Scroll para o dia ativo
  useEffect(() => {
    const timer = setTimeout(() => {
      const currentEl = document.querySelector('[data-current-dia="true"]');
      if (currentEl) {
        currentEl.scrollIntoView({ block: 'center', behavior: 'smooth' });
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [pathname]);

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
          {livrosOrdenados.map(([livro, diasLivro]) => {
            const isLivroOpen = openLivro === livro;
            const aprovadosLivro = diasLivro.filter(d => d.status === 'aprovado').length;

            return (
              <div key={livro} className={styles.semanaBlock}>
                <button
                  className={`${styles.semanaBtn} ${isLivroOpen ? styles.semanaActive : ''}`}
                  onClick={() => toggleLivro(livro)}
                >
                  <span className={styles.semanaInfo}>
                    <span className={styles.semanaTema}>{livro}</span>
                  </span>
                  <span className={styles.semanaProgress}>
                    <span className={styles.progressDots}>
                      {diasLivro.map((d, i) => (
                        <span
                          key={i}
                          className={`${styles.dot} ${d.status === 'aprovado' ? styles.dotActive : ''}`}
                        />
                      ))}
                    </span>
                  </span>
                </button>

                {isLivroOpen && (
                  <div className={styles.diasContainer}>
                    {diasLivro
                      .sort(sortByCapVerso)
                      .map((dia) => {
                        const isAprovado = dia.status === 'aprovado';
                        const isCurrentPage =
                          pathname === `/culto-domestico/${dia.semana}/${dia.dia}`;

                        return isAprovado ? (
                          <Link
                            href={`/culto-domestico/${dia.semana}/${dia.dia}`}
                            key={dia.id}
                            className={`${styles.diaItem} ${isCurrentPage ? styles.diaCurrent : ''}`}
                            data-current-dia={isCurrentPage ? 'true' : undefined}
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
