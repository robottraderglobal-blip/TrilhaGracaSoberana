import sys
import os
sys.path.insert(0, os.getcwd())
from ryle_pipeline.utils.db import supabase

def check_pendings():
    res = supabase.table('plano_devocional').select('id, semana, dia_semana, titulo').neq('status', 'aprovado').order('semana').order('dia_semana').execute()
    pending = res.data
    print(f"Total pendentes: {len(pending)}")
    for p in pending:
        print(f"Semana {p['semana']}, Dia {p['dia_semana']}: {p['titulo']}")

if __name__ == '__main__':
    check_pendings()
