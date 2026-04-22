import sys
import os
sys.path.insert(0, os.getcwd())

from ryle_pipeline.db.client import get_client

supabase = get_client()

pendentes = supabase.table('plano_devocional').select('id, semana, dia_semana').neq('status', 'aprovado').execute().data

for p in pendentes:
    pid = p['id']
    print(f"Checando {p['semana']} - {p['dia_semana']} ({pid})")
    
    # Verifica se já está na devocionais_final
    res = supabase.table('devocionais_final').select('id').eq('plano_id', pid).execute()
    if res.data:
        print("  -> Já estava finalizado! Atualizando status para aprovado.")
        supabase.table('plano_devocional').update({'status': 'aprovado'}).eq('id', pid).execute()
    else:
        print("  -> Realmente incompleto. Limpando rascunhos sem devocionais_final...")
        try:
            supabase.table('escritor_trabalho').delete().eq('plano_id', pid).execute()
            supabase.table('revisor_trabalho').delete().eq('plano_id', pid).execute()
        except BaseException as e:
            print(f"Erro ao limpar: {e}")

print("Fim.")
