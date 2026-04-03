import Image from "next/image";
import Link from "next/link";
import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.heroSection}>
        <div className={`animate-fade-in ${styles.contentWrapper}`}>
          <h2 className={styles.kicker}>DEVOCIONAIS REFORMADAS</h2>
          <h1 className={styles.title}>
            A profundidade dos puritanos,<br/>
            para a devoção contemporânea.
          </h1>
          <p className={styles.description}>
            Linguagem acessível, precisão teológica inegociável. 
            Inspirada na obra de J.C. Ryle, para aqueles que buscam a santidade prática 
            no formato de uma leitura diária robusta.
          </p>
          
          <div className={styles.buttonGroup}>
            <Link href="/hoje" prefetch={false} className={styles.primaryButton}>
              Ler a Reflexão de Hoje
            </Link>
            <Link href="/semanas" className={`${styles.secondaryButton} glass`}>
              Explorar Planos
            </Link>
          </div>
        </div>
      </div>
      
      {/* Sneak peek abstract section */}
      <section className={styles.sneakPeek}>
        <div className={styles.verseBox}>
          <p className={styles.verse}>
            "Santifica-os na verdade; a tua palavra é a verdade."
          </p>
          <p className={styles.verseRef}>— João 17:17</p>
        </div>
      </section>

      {/* Culto Doméstico promo */}
      <section className={styles.sneakPeek}>
        <div className={styles.verseBox}>
          <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.3rem', marginBottom: '0.5rem' }}>
            📖 100 Dias de Culto Doméstico
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.7, marginBottom: '1rem' }}>
            Devocionais no estilo de Augustus Nicodemus — clareza pastoral e aplicação para o lar.
          </p>
          <Link href="/culto-domestico" className={styles.secondaryButton} style={{ display: 'inline-block' }}>
            Explorar o plano →
          </Link>
        </div>
      </section>
    </main>
  );
}
