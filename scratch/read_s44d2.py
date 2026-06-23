import sys
from ryle_pipeline.db import client

# Setup encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

c = client.get_client()

# Fetch S44D2
# plano_devocional: semana=44, dia_semana=2
p = c.table('plano_devocional').select('id, texto_biblico').eq('semana', 44).eq('dia_semana', 2).maybe_single().execute().data
if p:
    dev = c.table('devocionais_final').select('conteudo_md').eq('plano_id', p['id']).maybe_single().execute().data
    if dev:
        print(dev['conteudo_md'][:1500])
        with open("scratch/s44d2_debug.md", "w", encoding="utf-8") as f:
            f.write(dev['conteudo_md'])
        print("\n\nSalvo em scratch/s44d2_debug.md")
else:
    print("S44D2 não encontrado")
