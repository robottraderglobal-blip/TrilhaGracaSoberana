const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

const envFile = fs.readFileSync(path.join(__dirname, '.env.local'), 'utf-8');
let supabaseUrl = '';
let supabaseKey = ''; // We must use Service Role Key to delete

envFile.split('\n').forEach(line => {
    if (line.startsWith('NEXT_PUBLIC_SUPABASE_URL=')) supabaseUrl = line.split('=')[1].trim();
    if (line.startsWith('SUPABASE_SERVICE_ROLE_KEY=')) supabaseKey = line.split('=')[1].trim(); 
    // Wait, the web env.local didn't have the secret! Let's read from the root .env
});

const rootEnvFile = fs.readFileSync(path.join(__dirname, '../.env'), 'utf-8');
rootEnvFile.split('\n').forEach(line => {
    if (line.startsWith('SUPABASE_ANON_KEY=')) {
        supabaseKey = line.split('=')[1].trim(); 
    }
});

const supabase = createClient(supabaseUrl, supabaseKey);

async function clean() {
    const { data: pendentes } = await supabase.from('plano_devocional').select('id, semana, dia_semana').neq('status', 'aprovado');
    
    console.log(`Encontrados ${pendentes.length} pendentes.`);
    for (const p of pendentes) {
        console.log(`Limpando Semana ${p.semana}, Dia ${p.dia_semana}...`);
        await supabase.from('escritor_trabalho').delete().eq('plano_id', p.id);
        await supabase.from('revisor_trabalho').delete().eq('plano_id', p.id);
        await supabase.from('exegese_trabalho').delete().eq('plano_id', p.id);
        await supabase.from('agente_historico').delete().eq('plano_id', p.id);
        
        await supabase.from('plano_devocional').update({ status: 'pendente' }).eq('id', p.id);
    }
    console.log("Limpeza concluída.");
}

clean();
