const fs = require('fs');

let dev = fs.readFileSync('devocionais_cordeiro', 'utf-8').split('\n').slice(0, 230).join('\n');
const files = ['Eixo II - Dias 8 a 12.md', 'Eixo III - Dias 13 a 18.md', 'Eixo IV - Dias 19 a 28.md'];

files.forEach(f => {
  let c = fs.readFileSync(f, 'utf-8');
  
  // Remove backslash escapes before exclamation marks
  c = c.replace(/\\!/g, '!');
  
  // Format the versículo:
  // From: *"Text"* \n\n — Ref
  // To: "Text" — Ref
  c = c.replace(/\*"([^"]+?)"\*\s*\n+\s*—\s*([^\n]+)/g, '"$1" — $2');
  
  // Fix the Dia titles: ## **Dia 8 — Title** -> ## Dia 8 — Title
  c = c.replace(/## \*\*Dia ([0-9]+) — (.*?)\*\*/g, '## Dia $1 — $2');
  
  // Fix EIXO titles: ## **EIXO II — Title** -> ## EIXO II — Title
  c = c.replace(/## \*\*EIXO (.*?) — (.*?)\*\*/g, '## EIXO $1 — $2');
  
  dev += '\n\n' + c;
});

fs.writeFileSync('devocionais_cordeiro', dev);
console.log('devocionais_cordeiro updated!');
