import os
import subprocess
import time

missing_semanas = [23, 32, 45]

for semana in missing_semanas:
    print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando recuperação da Semana {semana}...")
    try:
        subprocess.run(
            ['python', '-m', 'ryle_pipeline.pipeline', 'executar-semana', '--semana', str(semana)],
            check=True
        )
        print(f"[{time.strftime('%H:%M:%S')}] Semana {semana} finalizada com sucesso.")
    except Exception as e:
        print(f"Exceção fatal na semana {semana}: {e}")

print("\n🎉 Todas as semanas ausentes foram processadas!")
