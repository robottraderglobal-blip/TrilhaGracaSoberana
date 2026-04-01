'use client';

import Link from 'next/link';
import styles from './CalendarView.module.css';

interface DiaInfo {
  id: string;
  semana: number;
  dia_semana: number;
  dia_nome: string;
  tema_semana: string;
  status: string;
}

interface CalendarViewProps {
  dias: DiaInfo[];
}

const MESES = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];
const DIAS_DA_SEMANA = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];

export default function CalendarView({ dias }: CalendarViewProps) {
  const anoAtual = new Date().getFullYear();
  const primeiroDomingo = new Date(anoAtual, 0, 1);
  while (primeiroDomingo.getDay() !== 0) {
    primeiroDomingo.setDate(primeiroDomingo.getDate() + 1);
  }

  // Identifica a qual constelação de mês o devocional pertence
  const getMesDaSemana = (numSemana: number) => {
    const dataSemana = new Date(primeiroDomingo.getTime());
    dataSemana.setDate(primeiroDomingo.getDate() + (numSemana - 1) * 7);
    return dataSemana.getMonth();
  };

  // Mapeia os dias num objeto por Mês -> Semana -> array[7 slots]
  const calendario = Array.from({ length: 12 }, () => [] as (DiaInfo | null)[][]);

  // Primeiro agrupamos por semana
  const semanasMap = new Map<number, (DiaInfo | null)[]>();
  // Preenche 52 semanas com arrays de 7 nulls
  for (let s = 1; s <= 52; s++) {
    semanasMap.set(s, Array(7).fill(null));
  }

  dias.forEach((dia) => {
    const semanaArr = semanasMap.get(dia.semana);
    if (semanaArr && dia.dia_semana >= 1 && dia.dia_semana <= 7) {
      semanaArr[dia.dia_semana - 1] = dia;
    }
  });

  // Distribuir semanas nos meses
  for (let s = 1; s <= 52; s++) {
    const mesIdx = getMesDaSemana(s);
    calendario[mesIdx].push(semanasMap.get(s)!);
  }

  return (
    <div className={styles.calendarWrapper}>
      <h2 className={styles.calendarTitle}>Plano de Leitura {anoAtual}</h2>
      <p className={styles.calendarSubtitle}>Acompanhe sua constância ao longo de 52 semanas.</p>

      <div className={styles.monthsGrid}>
        {MESES.map((nomeMes, mesIdx) => {
          const semanasDoMes = calendario[mesIdx];
          if (semanasDoMes.length === 0) return null;

          // Extrair algumas infos para exibir
          const totalDias = semanasDoMes.length * 7;
          let lidos = 0;
          semanasDoMes.forEach((sem) => {
            sem.forEach((d) => {
              if (d && d.status === 'aprovado') lidos++;
            });
          });

          return (
            <div key={mesIdx} className={styles.monthCard}>
              <div className={styles.monthHeader}>
                <h3 className={styles.monthName}>{nomeMes}</h3>
                <span className={styles.monthStats}>{lidos}/{totalDias}</span>
              </div>

              <div className={styles.daysGrid}>
                {/* Cabeçalho dos dias da semana */}
                {DIAS_DA_SEMANA.map((letra, i) => (
                  <div key={`head-${i}`} className={styles.dayLetter}>{letra}</div>
                ))}
                
                {/* Cada semana é uma linha de 7 slots */}
                {semanasDoMes.map((semanaArr, sIdx) => (
                  semanaArr.map((dia, dIdx) => {
                    if (!dia) {
                      return <div key={`empty-${sIdx}-${dIdx}`} className={styles.dayBoxEmpty} />;
                    }
                    
                    const isAprovado = dia.status === 'aprovado';
                    
                    if (isAprovado) {
                      return (
                        <Link 
                          key={dia.id} 
                          href={`/semanas/${dia.semana}/${dia.dia_semana}`}
                          className={`${styles.dayBox} ${styles.dayAprovado}`}
                          title={`S${dia.semana} D${dia.dia_semana}: ${dia.tema_semana}`}
                        >
                          <span className={styles.srOnly}>Dia {dia.dia_semana} Semana {dia.semana}</span>
                        </Link>
                      );
                    } else {
                      return (
                        <div 
                          key={dia.id} 
                          className={`${styles.dayBox} ${styles.dayPendente}`}
                          title={`Em breve: S${dia.semana}`}
                        />
                      );
                    }
                  })
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
