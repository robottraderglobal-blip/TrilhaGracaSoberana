/**
 * Utilitário de lookup da Bíblia ARA (Almeida Revista e Atualizada)
 * Fonte: ryle_pipeline/utils/ARA.json
 * Estrutura: Array<{ name: string; abbrev: string; chapters: string[][] }>
 */

import { readFileSync } from 'fs';
import { join } from 'path';

interface BibleBook {
  name: string;
  abbrev: string;
  chapters: string[][];
}

let _bible: BibleBook[] | null = null;

function getBible(): BibleBook[] {
  if (_bible) return _bible;
  const path = join(process.cwd(), '..', 'ryle_pipeline', 'utils', 'ARA.json');
  const raw = readFileSync(path, 'utf-8');
  _bible = JSON.parse(raw) as BibleBook[];
  return _bible;
}

// Mapa de aliases para normalizar abreviações e nomes completos
const ALIAS_MAP: Record<string, string> = {
  // Português extenso → abbrev
  'gênesis': 'Gn', 'genesis': 'Gn',
  'êxodo': 'Ex', 'exodo': 'Ex',
  'levítico': 'Lv', 'levitico': 'Lv',
  'números': 'Nm', 'numeros': 'Nm',
  'deuteronômio': 'Dt', 'deuteronomio': 'Dt',
  'josué': 'Js', 'josue': 'Js',
  'juízes': 'Jz', 'juizes': 'Jz',
  'rute': 'Rt',
  '1 samuel': '1Sm', '1samuel': '1Sm', '1sm': '1Sm',
  '2 samuel': '2Sm', '2samuel': '2Sm', '2sm': '2Sm',
  '1 reis': '1Rs', '1reis': '1Rs', '1rs': '1Rs',
  '2 reis': '2Rs', '2reis': '2Rs', '2rs': '2Rs',
  '1 crônicas': '1Cr', '1cronicas': '1Cr', '1cr': '1Cr',
  '2 crônicas': '2Cr', '2cronicas': '2Cr', '2cr': '2Cr',
  'esdras': 'Ed', 'ed': 'Ed',
  'neemias': 'Ne',
  'ester': 'Et',
  'jó': 'Jó', 'jo': 'Jo', 'job': 'Jó',
  'salmos': 'Sl', 'salmo': 'Sl', 'sl': 'Sl', 'ps': 'Sl',
  'provérbios': 'Pv', 'proverbios': 'Pv', 'pv': 'Pv',
  'eclesiastes': 'Ec',
  'cantares': 'Ct', 'cânticos': 'Ct', 'cantares dos cantares': 'Ct',
  'isaías': 'Is', 'isaias': 'Is', 'is': 'Is',
  'jeremias': 'Jr',
  'lamentações': 'Lm', 'lamentacoes': 'Lm',
  'ezequiel': 'Ez',
  'daniel': 'Dn',
  'oséias': 'Os', 'oseias': 'Os',
  'joel': 'Jl',
  'amós': 'Am', 'amos': 'Am',
  'obadias': 'Ob',
  'jonas': 'Jn',
  'miquéias': 'Mq', 'miqueias': 'Mq',
  'naum': 'Na',
  'habacuque': 'Hc',
  'sofonias': 'Sf',
  'ageu': 'Ag',
  'zacarias': 'Zc',
  'malaquias': 'Ml',
  'mateus': 'Mt', 'mt': 'Mt',
  'marcos': 'Mc', 'mc': 'Mc',
  'lucas': 'Lc', 'lc': 'Lc',
  'joão': 'Jo', 'joao': 'Jo',
  'atos': 'At',
  'romanos': 'Rm', 'rm': 'Rm',
  '1 coríntios': '1Co', '1corintios': '1Co', '1co': '1Co',
  '2 coríntios': '2Co', '2corintios': '2Co', '2co': '2Co',
  'gálatas': 'Gl', 'galatas': 'Gl', 'gl': 'Gl',
  'efésios': 'Ef', 'efesios': 'Ef', 'ef': 'Ef',
  'filipenses': 'Fp', 'fp': 'Fp',
  'colossenses': 'Cl', 'cl': 'Cl',
  '1 tessalonicenses': '1Ts', '1ts': '1Ts',
  '2 tessalonicenses': '2Ts', '2ts': '2Ts',
  '1 timóteo': '1Tm', '1timoteo': '1Tm', '1tm': '1Tm',
  '2 timóteo': '2Tm', '2timoteo': '2Tm', '2tm': '2Tm',
  'tito': 'Tt',
  'filemon': 'Fm', 'filemom': 'Fm',
  'hebreus': 'Hb', 'hb': 'Hb',
  'tiago': 'Tg',
  '1 pedro': '1Pe', '1pe': '1Pe',
  '2 pedro': '2Pe', '2pe': '2Pe',
  '1 joão': '1Jo', '1joao': '1Jo', '1jo': '1Jo',
  '2 joão': '2Jo', '2joao': '2Jo', '2jo': '2Jo',
  '3 joão': '3Jo', '3joao': '3Jo', '3jo': '3Jo',
  'judas': 'Jd',
  'apocalipse': 'Ap', 'ap': 'Ap',
};

function normalizeRef(ref: string): { abbrev: string; startCap: number; startVerse: number; endVerse: number } | null {
  // Exemplos: "Mt 5.3", "Mateus 5.3", "Rm 8.28-30", "Salmos 23", "1Co 13.4-7", "Fp 4.6-7"
  const clean = ref.trim();

  // Regex: captura livro (com possível número inicial) + cap.vers[-vers]
  const match = clean.match(/^(.+?)\s+(\d+)(?:[.:,](\d+)(?:\s*[-–]\s*(\d+))?)?$/i);
  if (!match) return null;

  const bookRaw = match[1].trim().toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, ''); // remove acentos para comparação
  const cap = parseInt(match[2], 10);
  const startV = match[3] ? parseInt(match[3], 10) : 1;
  const endV = match[4] ? parseInt(match[4], 10) : (match[3] ? startV : 999);

  // Tenta encontrar abbrev
  let abbrev: string | undefined;

  // 1. Tenta direto no ALIAS_MAP (sem acento)
  const bookNoAccent = bookRaw.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  abbrev = ALIAS_MAP[bookNoAccent] || ALIAS_MAP[bookRaw];

  if (!abbrev) {
    // 2. Tenta match parcial no nome do livro na Bíblia
    const bible = getBible();
    const found = bible.find(b =>
      b.name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').startsWith(bookNoAccent) ||
      b.abbrev.toLowerCase() === bookNoAccent
    );
    abbrev = found?.abbrev;
  }

  if (!abbrev) return null;
  return { abbrev, startCap: cap, startVerse: startV, endVerse: endV };
}

/**
 * Retorna o texto de uma passagem da ARA.
 * @param ref - Referência como "Mt 5.3-12", "Rm 8.28-30", "Sl 23"
 * @returns Texto concatenado dos versículos, ou null se não encontrado
 */
export function getVerseText(ref: string): string | null {
  try {
    const parsed = normalizeRef(ref);
    if (!parsed) return null;

    const bible = getBible();
    const book = bible.find(b =>
      b.abbrev.toLowerCase() === parsed.abbrev.toLowerCase()
    );
    if (!book) return null;

    const chapter = book.chapters[parsed.startCap - 1];
    if (!chapter) return null;

    const endV = Math.min(parsed.endVerse, chapter.length);
    const startV = parsed.startVerse;

    const verses = chapter.slice(startV - 1, endV);
    return verses.join(' ');
  } catch {
    return null;
  }
}

/**
 * Retorna todas as sugestões de refs validadas com texto real da ARA.
 * Para refs que não encontrar, retorna texto como null (LLM será fallback).
 */
export function enrichWithARA(passagens: Array<{ ref: string; texto: string }>): Array<{ ref: string; texto: string }> {
  return passagens.map(p => {
    const real = getVerseText(p.ref);
    return { ref: p.ref, texto: real ?? p.texto };
  });
}
