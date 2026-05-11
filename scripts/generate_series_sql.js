const fs = require('fs');
const path = require('path');

const inputDirNovos = path.join(__dirname, '../novos');
const inputDirCordeiro = path.join(__dirname, '../devocionais_cordeiro');
const outputFile = path.join(__dirname, '../series_setup.sql');

// Extract all md files
const filesNovos = fs.readdirSync(inputDirNovos).filter(f => f.endsWith('.md')).map(f => path.join(inputDirNovos, f));
const filesAll = [...filesNovos, inputDirCordeiro]; // add Cordeiro

const series = [];

// Helper to escape SQL strings
const escapeSql = (str) => {
  return str.replace(/'/g, "''").trim();
};

filesAll.forEach(filepath => {
  const filename = path.basename(filepath);
  let content = '';
  try {
    content = fs.readFileSync(filepath, 'utf-8');
  } catch(e) {
    console.error(`Erro ao ler ${filepath}`);
    return;
  }
  const lines = content.split('\n');

  // Infer slug
  let slug = '';
  let currentNomeSerie = '';
  
  if (filename === 'devocionais_cordeiro') {
    slug = 'cordeiro';
    currentNomeSerie = 'O Cordeiro na Bíblia';
  } else {
    const slugMatch = filename.match(/serie\d+-(.+)-21-devocionais/);
    slug = slugMatch ? slugMatch[1] : filename.replace('.md', '');
  }

  let devocionais = [];
  let currentSemana = '';
  let currentDay = null;
  let state = 'IDLE'; // IDLE, VERSICULO, REFERENCIA, CONTEUDO, PERGUNTA

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Match Nome da Serie
    if (line.startsWith('# Série')) {
      currentNomeSerie = line.replace(/^# /, '').trim();
      continue;
    }

    // Match Semana / Eixo
    if (line.startsWith('## SEMANA') || line.startsWith('## EIXO')) {
      currentSemana = line.replace(/^## (SEMANA|EIXO)[A-Z\sIVX]*[—\-]\s*/, '').trim();
      continue;
    }

    // Match Dia
    if (line.startsWith('## Dia ')) {
      if (currentDay) {
        devocionais.push(currentDay);
      }
      
      const match = line.match(/## Dia (\d+) — (.+)/);
      if (match) {
        currentDay = {
          slug_serie: slug,
          nome_serie: currentNomeSerie,
          semana: currentSemana,
          dia: parseInt(match[1], 10),
          titulo: match[2].trim(),
          versiculo: '',
          referencia: '',
          conteudo: '',
          pergunta: ''
        };
        state = 'VERSICULO';
      }
      continue;
    }

    if (!currentDay) continue;

    if (state === 'VERSICULO') {
      if (line.startsWith('*') && line.endsWith('*')) {
        currentDay.versiculo = line.replace(/^\*"/, '').replace(/"\*$/, '').trim();
        state = 'REFERENCIA';
      } else if (filename === 'devocionais_cordeiro' && !line.startsWith('—') && line !== '') {
         // Cordeiro versiculo
         currentDay.versiculo = line.replace(/^"/, '').replace(/"$/, '').trim();
         state = 'REFERENCIA';
      }
      continue;
    }

    if (state === 'REFERENCIA') {
      if (line.startsWith('—')) {
        currentDay.referencia = line.replace(/^—\s*/, '').trim();
        state = 'CONTEUDO';
      } else if (filename === 'devocionais_cordeiro' && line !== '') {
        currentDay.referencia = line.trim();
        state = 'CONTEUDO';
      }
      continue;
    }

    if (state === 'CONTEUDO') {
      if (line.startsWith('*A pergunta que fica:') || line.startsWith('**A pergunta que fica:**') || line.startsWith('A pergunta que fica:')) {
         currentDay.pergunta = line.replace(/^\*?\*?A pergunta que fica:\*?\*?/, '').trim();
         state = 'IDLE';
      } else if (line !== '---' && !line.startsWith('**Fim da Série')) {
        currentDay.conteudo += (currentDay.conteudo ? '\n' : '') + lines[i];
      }
      continue;
    }
  }

  // Push last day
  if (currentDay) {
    devocionais.push(currentDay);
  }

  series.push(...devocionais);
});

// Create SQL statements
let sql = `-- Script gerado automaticamente para criar e popular a tabela series_devocionais (incluindo O Cordeiro)\n\n`;
sql += `CREATE TABLE IF NOT EXISTS series_devocionais (\n`;
sql += `    id SERIAL PRIMARY KEY,\n`;
sql += `    slug_serie TEXT NOT NULL,\n`;
sql += `    nome_serie TEXT NOT NULL,\n`;
sql += `    dia INTEGER NOT NULL,\n`;
sql += `    semana TEXT NOT NULL,\n`;
sql += `    titulo TEXT NOT NULL,\n`;
sql += `    versiculo TEXT NOT NULL,\n`;
sql += `    referencia TEXT NOT NULL,\n`;
sql += `    conteudo TEXT NOT NULL,\n`;
sql += `    pergunta TEXT NOT NULL,\n`;
sql += `    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\n`;
sql += `    UNIQUE(slug_serie, dia)\n`;
sql += `);\n\n`;

// RLS 
sql += `-- Ativa RLS e cria política de leitura pública\n`;
sql += `ALTER TABLE series_devocionais ENABLE ROW LEVEL SECURITY;\n`;
sql += `DROP POLICY IF EXISTS "Permitir leitura pública nas series" ON series_devocionais;\n`;
sql += `CREATE POLICY "Permitir leitura pública nas series" ON series_devocionais FOR SELECT USING (true);\n\n`;

sql += `TRUNCATE TABLE series_devocionais;\n\n`;

series.forEach(d => {
  // Clean empty lines at start/end of content
  let cont = d.conteudo.replace(/^\s*\n/g, '').replace(/\n\s*$/g, '');
  sql += `INSERT INTO series_devocionais (slug_serie, nome_serie, dia, semana, titulo, versiculo, referencia, conteudo, pergunta) VALUES (\n`;
  sql += `    '${escapeSql(d.slug_serie)}',\n`;
  sql += `    '${escapeSql(d.nome_serie)}',\n`;
  sql += `    ${d.dia},\n`;
  sql += `    '${escapeSql(d.semana)}',\n`;
  sql += `    '${escapeSql(d.titulo)}',\n`;
  sql += `    '${escapeSql(d.versiculo)}',\n`;
  sql += `    '${escapeSql(d.referencia)}',\n`;
  sql += `    '${escapeSql(cont)}',\n`;
  sql += `    '${escapeSql(d.pergunta)}'\n`;
  sql += `);\n\n`;
});

fs.writeFileSync(outputFile, sql, 'utf-8');
console.log(`Gerado: ${outputFile} com ${series.length} devocionais.`);
