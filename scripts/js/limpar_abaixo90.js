const fs = require('fs');
const path = require('path');

let supabaseUrl = '', supabaseKey = '';
fs.readFileSync(path.join(__dirname, 'web/.env.local'), 'utf-8').split('\n').forEach(l => {
    if (l.startsWith('NEXT_PUBLIC_SUPABASE_URL=')) supabaseUrl = l.split('=')[1].trim();
    if (l.startsWith('NEXT_PUBLIC_SUPABASE_ANON_KEY=')) supabaseKey = l.split('=')[1].trim();
});

async function main() {
    // 1. Buscar devocionais_final com score < 90
    const res = await fetch(`${supabaseUrl}/rest/v1/devocionais_final?select=id,plano_id,score_final,titulo,versao_aprovada&score_final=lt.90&order=score_final.asc`, {
        headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
    });
    const finais = await res.json();
    console.log(`Devocionais com nota < 90: ${finais.length}`);
    
    // 2. Buscar semana/dia de cada plano_id
    const planoIds = finais.map(f => f.plano_id);
    const semanas = new Set();
    
    for (const f of finais) {
        const r2 = await fetch(`${supabaseUrl}/rest/v1/plano_devocional?select=semana,dia_semana&id=eq.${f.plano_id}`, {
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
        });
        const plano = await r2.json();
        if (plano[0]) {
            semanas.add(plano[0].semana);
            console.log(`  ${f.score_final} | S${plano[0].semana}D${plano[0].dia_semana} | ${f.titulo}`);
        }
    }
    
    console.log(`\nSemanas envolvidas: ${[...semanas].sort((a,b)=>a-b).join(', ')}`);
    console.log(`Total semanas unicas: ${semanas.size}`);
    
    // 3. Limpar dados antigos para essas devocionais
    console.log(`\nLimpando dados antigos...`);
    let cleaned = 0;
    for (const f of finais) {
        // Delete narracao
        await fetch(`${supabaseUrl}/rest/v1/devocionais_narracao?plano_id=eq.${f.plano_id}`, {
            method: 'DELETE',
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
        });
        // Delete final
        await fetch(`${supabaseUrl}/rest/v1/devocionais_final?id=eq.${f.id}`, {
            method: 'DELETE',
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
        });
        // Delete revisoes
        await fetch(`${supabaseUrl}/rest/v1/revisoes?plano_id=eq.${f.plano_id}`, {
            method: 'DELETE',
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
        });
        // Delete escritor_trabalho
        await fetch(`${supabaseUrl}/rest/v1/escritor_trabalho?plano_id=eq.${f.plano_id}`, {
            method: 'DELETE',
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
        });
        // Delete pesquisa
        await fetch(`${supabaseUrl}/rest/v1/pesquisa_fontes?plano_id=eq.${f.plano_id}`, {
            method: 'DELETE',
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
        });
        // Delete exegese
        await fetch(`${supabaseUrl}/rest/v1/exegeses?plano_id=eq.${f.plano_id}`, {
            method: 'DELETE',
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
        });        
        // Reset status
        await fetch(`${supabaseUrl}/rest/v1/plano_devocional?id=eq.${f.plano_id}`, {
            method: 'PATCH',
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'pendente' })
        });
        cleaned++;
    }
    
    console.log(`Limpeza concluida: ${cleaned} devocionais resetadas.`);
    
    // 4. Salvar lista de semanas para reprocessar
    const semanasArr = [...semanas].sort((a,b) => a-b);
    fs.writeFileSync('semanas_refazer.json', JSON.stringify(semanasArr), 'ascii');
    console.log(`Semanas salvas em semanas_refazer.json: [${semanasArr.join(', ')}]`);
}

main();
