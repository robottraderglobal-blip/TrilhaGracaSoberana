import sys
from ryle_pipeline.db import client

# Setup encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

c = client.get_client()

# Fetch all final devotionals
print("Carregando devocionais_final...")
r = c.table('devocionais_final').select('plano_id, titulo, conteudo_md').execute()
devs = r.data

print("Carregando plano_devocional...")
p_res = c.table('plano_devocional').select('id, semana, dia_semana').execute()
planos = {p['id']: p for p in p_res.data}

print(f"Total devocionais: {len(devs)}")
print(f"Total planos: {len(planos)}")

weird_bold_patterns = [
    "**.", # Bold dot
    "**-",
    "**  **",
    "**\n",
    "**\t",
]

lines_patterns = [
    "---",
    "___",
    "***",
]

issues_found = []

for d in devs:
    plano_id = d['plano_id']
    if plano_id not in planos:
        continue
    plano = planos[plano_id]
    sem, dia = plano['semana'], plano['dia_semana']
    
    md = d['conteudo_md'] or ''
    lines = md.splitlines()
    body_lines = lines[5:] if len(lines) > 5 else lines
    body_text = "\n".join(body_lines)
    
    found_lines = []
    for lp in lines_patterns:
        if lp in body_text:
            found_lines.append(lp)
            
    found_bolds = []
    for wp in weird_bold_patterns:
        if wp in md:
            found_bolds.append(wp)
            
    first_line = md.strip().split('\n')[0] if md.strip() else ''
    first_line_issue = ""
    if first_line.startswith('*') and not first_line.startswith('> '):
        first_line_issue = "falta blockquote"
        
    if found_lines or found_bolds or first_line_issue:
        issues_found.append({
            "semana": sem,
            "dia": dia,
            "titulo": d['titulo'],
            "lines": found_lines,
            "bolds": found_bolds,
            "first_line_issue": first_line_issue
        })

print(f"\nEncontradas {len(issues_found)} devocionais com possíveis problemas:")
for issue in sorted(issues_found, key=lambda x: (x['semana'], x['dia'])):
    print(f"S{issue['semana']}D{issue['dia']} - {issue['titulo']}:")
    if issue['lines']:
        print(f"  Linhas encontradas: {issue['lines']}")
    if issue['bolds']:
        print(f"  Negritos estranhos: {issue['bolds']}")
    if issue['first_line_issue']:
        print(f"  Problema de blockquote: {issue['first_line_issue']}")
