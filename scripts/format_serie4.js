const fs = require('fs');
const path = require('path');

const inputFile = path.join(__dirname, '../novos/serie4-oficialato-21-devocionais.md');

let content = fs.readFileSync(inputFile, 'utf-8');

const lines = content.split('\n');
const outLines = [];

outLines.push('# Série 4 — Oficialato');

let state = 'NORMAL';
let tempSemana = '';
let tempDia = '';
let tempTexto = '';
let isPergunta = false;
let perguntaAcc = [];

for (let i = 0; i < lines.length; i++) {
  const line = lines[i].trim();

  if (line === '__SEMANA 1__' || line === '__SEMANA 2__' || line === '__SEMANA 3__') {
     tempSemana = line.replace(/__/g, '');
     state = 'SEMANA_NAME';
     continue;
  }
  if (state === 'SEMANA_NAME') {
     if (line !== '') {
        const name = line.replace(/\*/g, '');
        outLines.push(`## ${tempSemana} — ${name}`);
        state = 'NORMAL';
     }
     continue;
  }

  const diaMatch = line.match(/^# __DIA (\d+)__/);
  if (diaMatch) {
     if (perguntaAcc.length > 0) {
        outLines.push(`*A pergunta que fica: ${perguntaAcc.join(' ')}*`);
        outLines.push('---');
        perguntaAcc = [];
        isPergunta = false;
     }

     tempDia = diaMatch[1];
     state = 'DIA_TITLE';
     continue;
  }
  if (state === 'DIA_TITLE') {
     if (line !== '') {
        const title = line.replace(/\*/g, '');
        outLines.push(`## Dia ${tempDia} — ${title}`);
        state = 'NORMAL';
     }
     continue;
  }

  const textoMatch = line.match(/^__Texto: (.+)__/);
  if (textoMatch) {
     tempTexto = textoMatch[1].replace(' (ARA)', '');
     state = 'VERSICULO';
     continue;
  }
  if (state === 'VERSICULO') {
     if (line !== '' && line !== '❦') {
        outLines.push(line); // O versículo
        outLines.push(`— ${tempTexto}`);
        state = 'NORMAL';
     }
     continue;
  }

  if (line.includes('Para autoexame do candidato')) {
     isPergunta = true;
     continue;
  }

  if (isPergunta) {
     if (line !== '' && !line.includes('---')) {
        perguntaAcc.push(line);
     }
  } else {
     if (line !== '' && line !== '❦' && !line.includes('# __Apresentação da Série__') && !line.includes('__Sumário__') && !line.includes('__PASTOREAR SOB O ARQUIPASTOR__') && !line.includes('Devocionais para Candidatos') && !line.includes('Estilo: J.C. Ryle') && !line.includes('Presbíteros e Diáconos') && !line.includes('Série completa de 21 dias') && !line.includes('Versão: ARA')) {
        // Pula sumário (linhas com 'Dia X —')
        if (line.match(/^__Dia \d+ —/)) continue;
        if (line.match(/^\*         /)) continue;
        
        outLines.push(line);
     }
  }
}

if (perguntaAcc.length > 0) {
  outLines.push(`*A pergunta que fica: ${perguntaAcc.join(' ')}*`);
}

fs.writeFileSync(inputFile, outLines.join('\n'), 'utf-8');
console.log('Série 4 formatada com sucesso!');
