import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nicodemos_pipeline_100.db.client import get_client

c = get_client()

# Check series_devocionais table
res = c.table("series_devocionais").select("id, slug_serie, nome_serie, dia, titulo").eq("slug_serie", "aconselhamento-biblico").order("dia").execute()

print(f"Total devocionais in series_devocionais for 'aconselhamento-biblico': {len(res.data)}")
if len(res.data) > 0:
    for idx, d in enumerate(res.data):
        print(f"  Day {d['dia']}: {d['titulo']}")
        if idx >= 5:
            print("  ...")
            break
            
    # Check if a recent change (like Helena's case in Dia 1) is present
    # We can fetch the content of Dia 1
    dia1 = c.table("series_devocionais").select("conteudo").eq("slug_serie", "aconselhamento-biblico").eq("dia", 1).execute()
    if dia1.data:
        cont = dia1.data[0]["conteudo"]
        print("\nDia 1 content snippet:")
        print(cont[:300])
        print("\nDoes it contain 'Helena'?", "Helena" in cont)
    else:
        print("Dia 1 not found.")
else:
    print("No data for counseling series in DB.")
