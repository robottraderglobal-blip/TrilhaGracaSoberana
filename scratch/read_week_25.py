import os
import sys
import json
from pathlib import Path
from ryle_pipeline.db import client

# Setup encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

c = client.get_client()

# Fetch week 25 plano
planos = c.table('plano_devocional').select('id, semana, dia_semana, texto_biblico, tema_central').eq('semana', 25).order('dia_semana').execute().data

print(f"Encontrados {len(planos)} planos na semana 25:")
for p in planos:
    dev = c.table('devocionais_final').select('id, titulo, conteudo_md').eq('plano_id', p['id']).maybe_single().execute().data
    if dev:
        print(f"\n--- Dia {p['dia_semana']} (Plano ID: {p['id']}, Devocional ID: {dev['id']}): {dev['titulo']} ---")
        print(f"Ref: {p['texto_biblico']}")
        md = dev['conteudo_md']
        lines = md.splitlines()
        print(f"Total de linhas: {len(lines)}")
        print("Primeiras 5 linhas:")
        for line in lines[:5]:
            print(f"  {line}")
        print("Últimas 5 linhas:")
        for line in lines[-5:]:
            print(f"  {line}")
        # Save each to a file for analysis
        filename = f"scratch/semana25_dia{p['dia_semana']}.md"
        Path(filename).write_text(md, encoding='utf-8')
        print(f"Salvo em {filename}")
    else:
        print(f"Sem devocional final para o dia {p['dia_semana']}")
