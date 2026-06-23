import os
import re
import sys
import io
from pathlib import Path

# Adjust output encoding for Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nicodemos_pipeline_100.db.client import get_client

def parse_md_file(filepath):
    filepath = Path(filepath)
    filename = filepath.name
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    slug = ''
    current_nome_serie = ''
    if filename == 'devocionais_cordeiro':
        slug = 'cordeiro'
        current_nome_serie = 'O Cordeiro na Bíblia'
    else:
        slug_match = re.match(r'serie\d+-(.+)-21-devocionais', filename)
        slug = slug_match.group(1) if slug_match else filename.replace('.md', '')
        
    devocionais = []
    current_semana = ''
    current_day = None
    state = 'IDLE' # IDLE, VERSICULO, REFERENCIA, CONTEUDO, PERGUNTA
    
    for line in lines:
        line_stripped = line.strip()
        
        # Match Nome da Serie
        if line_stripped.startswith('# Série'):
            current_nome_serie = line_stripped[7:].strip()
            continue
            
        # Match Semana / Eixo
        if line_stripped.startswith('## SEMANA') or line_stripped.startswith('## EIXO'):
            current_semana = re.sub(r'^## (SEMANA|EIXO)[A-Z\sIVX]*[—\-]\s*', '', line_stripped).strip()
            continue
            
        # Match Dia
        if line_stripped.startswith('## Dia '):
            if current_day:
                devocionais.append(current_day)
                
            match = re.match(r'## Dia (\d+)\s*[—\-]\s*(.+)', line_stripped)
            if match:
                current_day = {
                    "slug_serie": slug,
                    "nome_serie": current_nome_serie,
                    "semana": current_semana,
                    "dia": int(match.group(1)),
                    "titulo": match.group(2).strip(),
                    "versiculo": "",
                    "referencia": "",
                    "conteudo": "",
                    "pergunta": ""
                }
                state = 'VERSICULO'
            continue
            
        if not current_day:
            continue
            
        if state == 'VERSICULO':
            if line_stripped.startswith('*') and line_stripped.endswith('*'):
                v = line_stripped
                if v.startswith('*') and v.endswith('*'):
                    v = v[1:-1].strip()
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1].strip()
                current_day["versiculo"] = v
                state = 'REFERENCIA'
            elif filename == 'devocionais_cordeiro' and not line_stripped.startswith('—') and line_stripped != '':
                dash_idx = line_stripped.find('—')
                if dash_idx > 0 and line_stripped.startswith('"'):
                    current_day["versiculo"] = line_stripped[:dash_idx].strip().strip('"').strip()
                    current_day["referencia"] = line_stripped[dash_idx+1:].strip()
                    state = 'CONTEUDO'
                else:
                    current_day["versiculo"] = line_stripped.strip('"').strip()
                    state = 'REFERENCIA'
            continue
            
        if state == 'REFERENCIA':
            if line_stripped.startswith('—'):
                current_day["referencia"] = line_stripped[1:].strip()
                state = 'CONTEUDO'
            elif filename == 'devocionais_cordeiro' and line_stripped != '':
                current_day["referencia"] = line_stripped
                state = 'CONTEUDO'
            continue
            
        if state == 'CONTEUDO':
            if line_stripped.startswith('*A pergunta que fica:') or line_stripped.startswith('**A pergunta que fica:**') or line_stripped.startswith('A pergunta que fica:'):
                q = re.sub(r'^\*?\*?A pergunta que fica:\*?\*?', '', line_stripped).strip()
                current_day["pergunta"] = q
                state = 'IDLE'
            elif line_stripped != '---' and not line_stripped.startswith('**Fim da Série'):
                current_day["conteudo"] += ('\n' if current_day["conteudo"] else '') + line
            continue
            
    if current_day:
        devocionais.append(current_day)
        
    for d in devocionais:
        d["conteudo"] = d["conteudo"].strip()
        
    return devocionais

def main():
    root_dir = Path("c:/Users/ryzen/Downloads/Antigravity/TrilhaGracaSoberana")
    novos_dir = root_dir / "novos"
    
    # List files just like the JS script
    files_novos = sorted([novos_dir / f for f in os.listdir(novos_dir) if f.endswith('.md')])
    file_cordeiro = root_dir / "devocionais_cordeiro"
    
    files_all = files_novos + [file_cordeiro]
    
    all_devocionais = []
    for fp in files_all:
        if fp.exists():
            devs = parse_md_file(fp)
            print(f"Parsed {len(devs)} devocionais from {fp.name}")
            all_devocionais.extend(devs)
        else:
            print(f"Warning: File {fp} does not exist.")
            
    print(f"Total devocionais parsed: {len(all_devocionais)}")
    
    # Connect to Supabase
    sb = get_client()
    
    # We will upload the data using upsert.
    # Since there are 140 devocionais, doing them in batches or in a single upsert is very efficient.
    # We will format the list to match the Supabase table column names.
    entries = []
    for d in all_devocionais:
        entries.append({
            "slug_serie": d["slug_serie"],
            "nome_serie": d["nome_serie"],
            "dia": d["dia"],
            "semana": d["semana"],
            "titulo": d["titulo"],
            "versiculo": d["versiculo"],
            "referencia": d["referencia"],
            "conteudo": d["conteudo"],
            "pergunta": d["pergunta"]
        })
        
    # First, let's do a quick validation checks on some of them
    # For example, does Dia 13 of counseling have Helena?
    counseling_d13 = next((x for x in entries if x["slug_serie"] == "aconselhamento-biblico" and x["dia"] == 13), None)
    if counseling_d13:
        print("\nValidation of parsed data (Dia 13 counseling):")
        print(f"  Title: {counseling_d13['titulo']}")
        print(f"  Contains 'Helena' in content? {'Helena' in counseling_d13['conteudo']}")
        print(f"  Snippet: {counseling_d13['conteudo'][:150]}...")
    
    print("\nStarting upsert to Supabase table 'series_devocionais'...")
    # Perform upsert
    # In Supabase client Python, upsert can be done like this:
    try:
        # Use upsert with on_conflict="slug_serie,dia" to prevent duplicate rows and update existing ones
        res = sb.table("series_devocionais").upsert(entries, on_conflict="slug_serie,dia").execute()
        print(f"✅ Success! Upserted {len(res.data)} records in Supabase.")
    except Exception as e:
        print(f"❌ Error during upsert: {e}")
        
if __name__ == '__main__':
    main()
