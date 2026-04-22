import os
import sys

# Corrige o Python loop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ryle_pipeline.db.supabase import get_supabase_client

def limpar_drafts():
    supabase = get_supabase_client()
    try:
        # Busca todas as semanas pendentes
        res = supabase.table('plano_devocional').select('id, semana, dia_semana').neq('status', 'aprovado').execute()
        pendentes = res.data
        if not pendentes:
            print("Nenhuma devocional pendente encontrada.")
            return

        print(f"Encontradas {len(pendentes)} devocionais pendentes. Limpando histórico travado...")
        for p in pendentes:
            p_id = p['id']
            print(f"- Limpando Semana {p['semana']}, Dia {p['dia_semana']} ({p_id})...")
            
            # Deletar trabalhos de revisor
            supabase.table('revisor_trabalho').delete().eq('plano_id', p_id).execute()
            # Deletar trabalhos de escritor
            supabase.table('escritor_trabalho').delete().eq('plano_id', p_id).execute()
            # Deletar histórico do agente
            supabase.table('agente_historico').delete().eq('plano_id', p_id).execute()
            # Deletar exegese se travou antes
            supabase.table('exegese_trabalho').delete().eq('plano_id', p_id).execute()
            
            # Atualizar plano_devocional status para pendente e resetar attempts
            supabase.table('plano_devocional').update({'status': 'pendente'}).eq('id', p_id).execute()

        print("\n✅ Limpeza concluída! Você pode rodar a pipeline novamente.")
    except Exception as e:
        print(f"Erro ao limpar: {e}")

if __name__ == '__main__':
    limpar_drafts()
