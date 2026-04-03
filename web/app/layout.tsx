import type { Metadata } from 'next';
import { Playfair_Display, Outfit } from 'next/font/google';
import Link from 'next/link';
import './globals.css';

const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair',
  display: 'swap',
});

const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Trilha da Graça Soberana',
  description: 'Devocionais reformadas baseadas em J.C. Ryle e teologia puritana clássica.',
};

import { ThemeProvider } from './components/ThemeProvider';
import { ThemeToggle } from './components/ThemeToggle';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className={`${playfair.variable} ${outfit.variable}`}>
        <ThemeProvider attribute="class" defaultTheme="dark">
          {/* Navbar */}
          <nav className="navbar glass">
            <div className="navLeft">
              <Link href="/" className="logoLink">
                Graça <span className="logoAccent">Soberana</span>
              </Link>
            </div>
            <div className="navRight" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <ThemeToggle />
              <Link href="/hoje" className="navLink navHighlight">
                📖 Hoje
              </Link>
              <Link href="/semanas" className="navLink">
                Devocionais
              </Link>
              <Link href="/culto-domestico" className="navLink">
                Culto Doméstico
              </Link>
              <Link href="/" className="navLink">
                Sobre
              </Link>
            </div>
          </nav>

          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
