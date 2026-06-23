import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nicodemos_pipeline_100.db.client import get_client
c = get_client()

# Puxar dia 40 (Semana 6)
res = c.table("nico_devocionais_final").select("*").eq("dia", 40).maybe_single().execute()
if res.data:
    dev = res.data
    print(f"=== DIA {dev['dia']} - REF: {dev['ref']} ===")
    print("Pergunta de reflexão extraída:")
    print(f"  {dev['pergunta_reflexao']}")
    print("\nConteúdo MD:")
    print(dev["conteudo_md"])
else:
    print("Dia 40 não encontrado.")
