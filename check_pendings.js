const fs = require('fs');

const envFile = fs.readFileSync('web/.env.local', 'utf-8');
let supabaseUrl = '';
let supabaseKey = '';

envFile.split('\n').forEach(line => {
    if (line.startsWith('NEXT_PUBLIC_SUPABASE_URL=')) supabaseUrl = line.split('=')[1].trim();
    if (line.startsWith('NEXT_PUBLIC_SUPABASE_ANON_KEY=')) supabaseKey = line.split('=')[1].trim();
});

async function checkPendings() {
    const url = `${supabaseUrl}/rest/v1/plano_devocional?select=semana,dia_semana,tema_semana&status=neq.aprovado&order=semana.asc,dia_semana.asc`;
    const res = await fetch(url, {
        headers: {
            'apikey': supabaseKey,
            'Authorization': `Bearer ${supabaseKey}`
        }
    });
    const data = await res.json();
    console.log(`Total pendentes: ${data.length}`);
    data.forEach(p => {
        console.log(`Semana ${p.semana}, Dia ${p.dia_semana}: ${p.tema_semana}`);
    });
}

checkPendings();
