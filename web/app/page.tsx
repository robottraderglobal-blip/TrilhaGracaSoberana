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
    </main>
  );
}
