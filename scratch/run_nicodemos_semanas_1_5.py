import subprocess
import time
import sys
import io

# Ajustar codificação para Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Lista de semanas de 2 a 5
semanas = range(2, 6)

print("=" * 60)
print(f"📖 INICIANDO ORQUESTRADOR NICODEMOS (SEMANAS 2 A 5) em {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

env = dict(subprocess.os.environ)
env["PYTHONIOENCODING"] = "utf-8"

for sem in semanas:
    print(f"\n[{time.strftime('%H:%M:%S')}] 🚀 Iniciando processamento da Semana {sem}...")
    try:
        result = subprocess.run(
            ['python', '-m', 'nicodemos_pipeline_100.pipeline', 'executar-semana', '--semana', str(sem), '--force'],
            check=True,
            env=env
        )
        print(f"[{time.strftime('%H:%M:%S')}] ✅ Semana {sem} finalizada com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"[{time.strftime('%H:%M:%S')}] ❌ ERRO ao processar a Semana {sem}. Tentando novamente em 15 segundos...")
        time.sleep(15)
        try:
            result = subprocess.run(
                ['python', '-m', 'nicodemos_pipeline_100.pipeline', 'executar-semana', '--semana', str(sem), '--force'],
                check=True,
                env=env
            )
            print(f"[{time.strftime('%H:%M:%S')}] ✅ Semana {sem} finalizada com sucesso na segunda tentativa.")
        except Exception as ex:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Falha crítica persistente na Semana {sem}: {ex}")
            print("Prosseguindo para a próxima semana para não travar o lote...")
            
    time.sleep(5)

print("\n" + "=" * 60)
print(f"🎉 FIM DO PROCESSAMENTO DE TODAS AS SEMANAS em {time.strftime('%Y-%m-%d %H:%M:%S')}!")
print("=" * 60)
