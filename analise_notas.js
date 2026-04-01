const fs = require('fs');
const path = require('path');

let supabaseUrl = '', supabaseKey = '';
fs.readFileSync(path.join(__dirname, 'web/.env.local'), 'utf-8').split('\n').forEach(l => {
    if (l.startsWith('NEXT_PUBLIC_SUPABASE_URL=')) supabaseUrl = l.split('=')[1].trim();
    if (l.startsWith('NEXT_PUBLIC_SUPABASE_ANON_KEY=')) supabaseKey = l.split('=')[1].trim();
});

async function analyze() {
    const res = await fetch(`${supabaseUrl}/rest/v1/devocionais_final?select=score_final,versao_aprovada,titulo,tema_semana,palavras&order=score_final.asc`, {
        headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
    });
    const data = await res.json();
    if (!Array.isArray(data)) { console.log("Erro:", JSON.stringify(data)); return; }
    
    const lines = [];
    lines.push(`DISTRIBUICAO DE NOTAS FINAIS`);
    lines.push(`Total aprovadas: ${data.length}`);
    
    const faixas = { '90-100': 0, '80-89': 0, '70-79': 0, '60-69': 0, 'abaixo60': 0, 'semNota': 0 };
    let soma = 0, count = 0, somaV = 0, somaP = 0;
    const comNota = [];
    
    for (const d of data) {
        somaP += d.palavras || 0;
        somaV += d.versao_aprovada || 1;
        const s = d.score_final;
        if (s === null || s === undefined) { faixas['semNota']++; continue; }
        soma += s; count++;
        comNota.push(d);
        if (s >= 90) faixas['90-100']++;
        else if (s >= 80) faixas['80-89']++;
        else if (s >= 70) faixas['70-79']++;
        else if (s >= 60) faixas['60-69']++;
        else faixas['abaixo60']++;
    }
    
    lines.push('');
    lines.push('POR FAIXA:');
    lines.push(`  90-100:    ${faixas['90-100']} (${((faixas['90-100']/data.length)*100).toFixed(1)}%)`);
    lines.push(`  80-89:     ${faixas['80-89']} (${((faixas['80-89']/data.length)*100).toFixed(1)}%)`);
    lines.push(`  70-79:     ${faixas['70-79']} (${((faixas['70-79']/data.length)*100).toFixed(1)}%)`);
    lines.push(`  60-69:     ${faixas['60-69']} (${((faixas['60-69']/data.length)*100).toFixed(1)}%)`);
    lines.push(`  abaixo 60: ${faixas['abaixo60']} (${((faixas['abaixo60']/data.length)*100).toFixed(1)}%)`);
    lines.push(`  sem nota:  ${faixas['semNota']}`);
    
    lines.push('');
    lines.push('ESTATISTICAS:');
    lines.push(`  Media geral:      ${(soma/count).toFixed(2)}`);
    const sorted = comNota.sort((a,b) => a.score_final - b.score_final);
    lines.push(`  Mediana:           ${sorted[Math.floor(count/2)]?.score_final}`);
    lines.push(`  Menor nota:        ${sorted[0]?.score_final}`);
    lines.push(`  Maior nota:        ${sorted[sorted.length-1]?.score_final}`);
    lines.push(`  Media versoes:     ${(somaV/data.length).toFixed(2)}`);
    lines.push(`  Media palavras:    ${Math.round(somaP/data.length)}`);
    
    lines.push('');
    lines.push('5 MENORES NOTAS:');
    for (const d of sorted.slice(0, 5)) {
        lines.push(`  ${d.score_final} - ${d.titulo}`);
    }
    
    lines.push('');
    lines.push('5 MAIORES NOTAS:');
    for (const d of sorted.slice(-5).reverse()) {
        lines.push(`  ${d.score_final} - ${d.titulo}`);
    }
    
    const output = lines.join('\n');
    fs.writeFileSync('notas.txt', output, 'ascii');
    console.log('Salvo em notas.txt');
}

analyze();
