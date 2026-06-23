import subprocess
import time
import sys
import io

# Ajustar codificação para Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Dias a processar
dias = range(151, 197)

print("=" * 60)
print(f"📖 INICIANDO ORQUESTRADOR DE EXPANSÃO (DIAS 151 A 196) em {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

env = dict(subprocess.os.environ)
env["PYTHONIOENCODING"] = "utf-8"

for dia in dias:
    print(f"\n[{time.strftime('%H:%M:%S')}] 🚀 Iniciando processamento do Dia {dia}...")
    try:
        result = subprocess.run(
            ['python', '-m', 'nicodemos_pipeline_100.pipeline', 'executar', '--dia', str(dia), '--force'],
            check=True,
            env=env
        )
        print(f"[{time.strftime('%H:%M:%S')}] ✅ Dia {dia} finalizado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"[{time.strftime('%H:%M:%S')}] ❌ ERRO ao processar o Dia {dia}. Tentando novamente em 15 segundos...")
        time.sleep(15)
        try:
            result = subprocess.run(
                ['python', '-m', 'nicodemos_pipeline_100.pipeline', 'executar', '--dia', str(dia), '--force'],
                check=True,
                env=env
            )
            print(f"[{time.strftime('%H:%M:%S')}] ✅ Dia {dia} finalizado com sucesso na segunda tentativa.")
        except Exception as ex:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Falha crítica persistente no Dia {dia}: {ex}")
            print("Prosseguindo para o próximo dia para não travar o lote...")
            
    time.sleep(3) # Pequena pausa entre os dias

print("\n" + "=" * 60)
print(f"🎉 FIM DA GERAÇÃO DE TODA A EXPANSÃO em {time.strftime('%Y-%m-%d %H:%M:%S')}!")
print("=" * 60)
