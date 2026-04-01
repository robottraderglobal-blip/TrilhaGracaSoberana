"""Exporta devocionais do Supabase para arquivos .md locais."""
import os, sys
sys.path.insert(0, ".")
os.makedirs("exports", exist_ok=True)

from supabase import create_client
from ryle_pipeline.config import SUPABASE_URL, SUPABASE_ANON_KEY
sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

resp = sb.table("devocionais_final").select("*").execute()
print(f"Total devocionais: {len(resp.data)}\n")

for d in resp.data:
    safe_title = d["titulo"][:30].replace(" ", "_").replace("/", "-")
    fname = f"exports/devocional_{safe_title}.md"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(d["conteudo_md"])
    print(f"Exportado: {fname}")
    print(f"  Titulo: {d['titulo']}")
    print(f"  Texto: {d['texto_biblico']}")
    print(f"  Palavras: {d['palavras']}, Score: {d['score_final']}")
    print()
