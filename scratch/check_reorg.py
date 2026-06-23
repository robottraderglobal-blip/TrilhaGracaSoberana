import sys
import io
import re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nicodemos_pipeline_100.db.client import get_client
c = get_client()

# Puxar dias 1, 2 e 3
for dia in [1, 2, 3]:
    res = c.table("nico_devocionais_final").select("dia, conteudo_md").eq("dia", dia).maybe_single().execute()
    if res.data:
        md = res.data["conteudo_md"]
        parts = md.split("### 7. Melodia no Lar")
        hymn_title = "NÃO ENCONTRADO"
        if len(parts) > 1:
            lines = parts[1].strip().splitlines()
            hymn_title = lines[0] if lines else "STRING VAZIA"
        print(f"Dia {dia}: {hymn_title}")
    else:
        print(f"Dia {dia}: não encontrado no banco")
