import Link from 'next/link';
import styles from './DayNav.module.css';

interface DayNavProps {
  semanaAtual: number;
  diaAtual: number;
  totalDiasSemana: number;
  temAnterior: boolean;
  temProximo: boolean;
  tituloAnterior?: string;
  tituloProximo?: string;
}

export default function DayNav({
  semanaAtual,
  diaAtual,
  totalDiasSemana,
  temAnterior,
  temProximo,
  tituloAnterior,
  tituloProximo,
}: DayNavProps) {
  // Calcular links anterior/próximo
  let prevSemana = semanaAtual;
  let prevDia = diaAtual - 1;
  if (prevDia < 1) {
    prevSemana = semanaAtual - 1;
    prevDia = 7; // último dia da semana anterior
  }

  let nextSemana = semanaAtual;
  let nextDia = diaAtual + 1;
  if (nextDia > totalDiasSemana) {
    nextSemana = semanaAtual + 1;
    nextDia = 1; // primeiro dia da próxima semana
  }

  return (
    <nav className={styles.dayNav} aria-label="Navegação entre devocionais">
      <div className={styles.navInner}>
        {temAnterior ? (
          <Link
            href={`/semanas/${prevSemana}/${prevDia}`}
            className={`${styles.navLink} ${styles.prevLink}`}
          >
            <span className={styles.navDirection}>← Anterior</span>
            {tituloAnterior && (
              <span className={styles.navTitle}>{tituloAnterior}</span>
            )}
          </Link>
        ) : (
          <div />
        )}

        <Link href="/semanas" className={styles.indexLink}>
          Índice
        </Link>

        {temProximo ? (
          <Link
            href={`/semanas/${nextSemana}/${nextDia}`}
            className={`${styles.navLink} ${styles.nextLink}`}
          >
            <span className={styles.navDirection}>Próximo →</span>
            {tituloProximo && (
              <span className={styles.navTitle}>{tituloProximo}</span>
            )}
          </Link>
        ) : (
          <div />
        )}
      </div>
    </nav>
  );
}
