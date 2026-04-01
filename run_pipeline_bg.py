import os
import subprocess
import time

semanas_pendentes = range(20, 53)

for semana in semanas_pendentes:
    print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando processamento da Semana {semana}...")
    try:
        # Run pipeline natively in Python via subprocess to prevent PowerShell pipeline crashes
        result = subprocess.run(
            ['python', '-m', 'ryle_pipeline.pipeline', 'executar-semana', '--semana', str(semana)],
            check=True
        )
        print(f"[{time.strftime('%H:%M:%S')}] Semana {semana} finalizada com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"[{time.strftime('%H:%M:%S')}] ERRO ao processar a Semana {semana}. O script de fallback continuará em 5 segundos...")
        time.sleep(5)
    except Exception as e:
        print(f"Exceção fatal: {e}")
        break
    
print("\n🎉 Todas as semanas programadas foram executadas!")
