const fs = require('fs');
const path = require('path');

let supabaseUrl = '', supabaseKey = '';
fs.readFileSync(path.join(__dirname, 'web/.env.local'), 'utf-8').split('\n').forEach(l => {
    if (l.startsWith('NEXT_PUBLIC_SUPABASE_URL=')) supabaseUrl = l.split('=')[1].trim();
    if (l.startsWith('NEXT_PUBLIC_SUPABASE_ANON_KEY=')) supabaseKey = l.split('=')[1].trim();
});

async function analyze() {
    const allData = [];
    let offset = 0;
    const limit = 1000;
    
    // Paginate
    while (true) {
        const res = await fetch(`${supabaseUrl}/rest/v1/pesquisa_fontes?select=id,fonte,status,resultado,query_enviada,doutrina_nome&order=created_at.asc&offset=${offset}&limit=${limit}`, {
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
        });
        const chunk = await res.json();
        if (!chunk.length) break;
        allData.push(...chunk);
        if (chunk.length < limit) break;
        offset += limit;
    }
    
    const data = allData;
    const lines = [];
    lines.push(`=== ANALISE DE PESQUISA NOTEBOOKLM ===`);
    lines.push(`Total de registros: ${data.length}`);
    
    const porFonte = {};
    const porStatus = {};
    let shortCount = 0;
    const shortSamples = [];
    
    for (const r of data) {
        if (!porFonte[r.fonte]) porFonte[r.fonte] = { total: 0, concluido: 0, empty: 0, charTotal: 0 };
        porFonte[r.fonte].total++;
        if (r.status === 'concluido') porFonte[r.fonte].concluido++;
        else porFonte[r.fonte].empty++;
        porFonte[r.fonte].charTotal += (r.resultado || '').length;
        porStatus[r.status] = (porStatus[r.status] || 0) + 1;
        
        if ((r.resultado || '').length < 50) {
            shortCount++;
            if (shortSamples.length < 10) {
                shortSamples.push({ fonte: r.fonte, resultado: r.resultado, doutrina: r.doutrina_nome });
            }
        }
    }
    
    lines.push(`\n--- POR FONTE ---`);
    for (const [fonte, stats] of Object.entries(porFonte)) {
        const taxa = ((stats.concluido / stats.total) * 100).toFixed(1);
        const media = Math.round(stats.charTotal / stats.total);
        lines.push(`${fonte.padEnd(15)} | Total: ${String(stats.total).padStart(4)} | Efetivos: ${String(stats.concluido).padStart(4)} | Vazios: ${String(stats.empty).padStart(4)} | Taxa: ${taxa.padStart(5)}% | Media chars: ${media}`);
    }
    
    lines.push(`\n--- POR STATUS ---`);
    for (const [status, count] of Object.entries(porStatus)) {
        lines.push(`${status.padEnd(20)} : ${count}`);
    }
    
    lines.push(`\nResultados curtos (<50 chars): ${shortCount} de ${data.length} (${((shortCount/data.length)*100).toFixed(1)}%)`);
    lines.push(`\n--- AMOSTRAS CURTAS ---`);
    for (const sr of shortSamples) {
        lines.push(`  [${sr.fonte}] "${sr.resultado}" (doutrina: ${sr.doutrina})`);
    }
    
    const sorted = [...data].sort((a, b) => (b.resultado || '').length - (a.resultado || '').length);
    lines.push(`\n--- TOP 5 RESULTADOS MAIS RICOS ---`);
    for (const sr of sorted.slice(0, 5)) {
        lines.push(`  [${sr.fonte}] ${(sr.resultado || '').length} chars | doutrina: ${sr.doutrina_nome}`);
        lines.push(`    Preview: ${(sr.resultado || '').substring(0, 150)}`);
    }
    
    lines.push(`\n--- QUERY EXEMPLOS ---`);
    for (const sr of data.slice(0, 3)) {
        lines.push(`  [${sr.fonte}] Query: ${sr.query_enviada}`);
        lines.push(`  Resultado (${(sr.resultado || '').length} chars): ${(sr.resultado || '').substring(0, 100)}`);
    }
    
    const output = lines.join('\n');
    fs.writeFileSync('analise_resultado.md', output, 'utf-8');
    console.log('Analise salva em analise_resultado.md');
}

analyze();
