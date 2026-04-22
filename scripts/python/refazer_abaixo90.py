import os
import subprocess
import time
import json

# Ler a lista de semanas que precisam de reprocessamento
with open('semanas_refazer.json', 'r') as f:
    semanas = json.load(f)

print(f"Total de semanas para reprocessar: {len(semanas)}")
print(f"Semanas: {semanas}")

for i, semana in enumerate(semanas):
    print(f"\n[{time.strftime('%H:%M:%S')}] ({i+1}/{len(semanas)}) Reprocessando Semana {semana}...")
    try:
        subprocess.run(
            ['python', '-m', 'ryle_pipeline.pipeline', 'executar-semana', '--semana', str(semana)],
            check=True
        )
        print(f"[{time.strftime('%H:%M:%S')}] Semana {semana} finalizada.")
    except subprocess.CalledProcessError as e:
        print(f"[{time.strftime('%H:%M:%S')}] ERRO na Semana {semana}: {e}")
        time.sleep(3)
    except Exception as e:
        print(f"Exceção fatal: {e}")
        break

print(f"\n{'='*50}")
print(f"Reprocessamento concluido!")
print(f"{'='*50}")
