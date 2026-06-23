import sys
from ryle_pipeline.db import client

# Setup encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

c = client.get_client()

p = c.table('plano_devocional').select('id, texto_biblico').eq('semana', 15).eq('dia_semana', 2).maybe_single().execute().data
if p:
    dev = c.table('devocionais_final').select('conteudo_md').eq('plano_id', p['id']).maybe_single().execute().data
    if dev:
        with open("scratch/s15d2_debug.md", "w", encoding="utf-8") as f:
            f.write(dev['conteudo_md'])
        print("Salvo em scratch/s15d2_debug.md")
