import sys
import io
# Ajustar encoding de saída para evitar erros no terminal do Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nicodemos_pipeline_100.db.client import get_client

c = get_client()

# 1. Contar nico_plano por status
res_plano = c.table("nico_plano").select("dia, semana, status").order("dia").execute()
dias_plano = res_plano.data
print(f"Total em nico_plano: {len(dias_plano)}")
status_plano = {}
for d in dias_plano:
    status_plano[d["status"]] = status_plano.get(d["status"], 0) + 1
print("Status em nico_plano:")
for s, val in status_plano.items():
    print(f"  - {s}: {val}")

# 2. Contar nico_devocionais_final
res_final = c.table("nico_devocionais_final").select("dia, semana, score_final").order("dia").execute()
dias_final = res_final.data
print(f"Total em nico_devocionais_final: {len(dias_final)}")

print("\nPrimeiros 5 dias em nico_devocionais_final:")
for d in dias_final[:5]:
    print(f"  Dia {d['dia']} (Semana {d['semana']}): Score {d.get('score_final')}")

print("\nDias 45 a 55 em nico_devocionais_final (transição Semana 7 para Semana 8):")
for d in dias_final:
    if 45 <= d["dia"] <= 55:
        print(f"  Dia {d['dia']} (Semana {d['semana']}): Score {d.get('score_final')}")
