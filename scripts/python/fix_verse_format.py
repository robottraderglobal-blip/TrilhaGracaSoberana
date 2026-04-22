"""
Migração: corrige formatação do versículo bíblico no topo dos devocionais.
Transforma:
  *"texto do versículo"* — Referência (ARA)
Em:
  > *"texto do versículo"*
  >
  > — **Referência (ARA)**
"""
import re
from ryle_pipeline.db import client

c = client.get_client()
r = c.table('devocionais_final').select('id, plano_id, conteudo_md').execute()

fixed = 0
skipped = 0

for d in r.data:
    md = d['conteudo_md'] or ''
    first_line = md.strip().split('\n')[0] if md.strip() else ''
    
    # Already correct format (blockquote)
    if first_line.startswith('> '):
        skipped += 1
        continue
    
    # Pattern 1: *"texto"* — Referência (ARA)
    # Pattern 2: *texto* — Referência (ARA)  
    # Pattern 3: Just italic text without blockquote
    if first_line.startswith('*'):
        lines = md.strip().split('\n')
        
        # Find where the verse header ends and the body begins
        # Usually it's the first line, or first two lines (verse + blank line)
        header_end = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == '':
                header_end = i
                break
            # Check if this line contains " — " or ends with "(ARA)" 
            if '(ARA)' in stripped or (i > 0 and stripped == ''):
                header_end = i
                break
        else:
            header_end = 0
        
        # Extract the header portion
        header_lines = lines[:header_end + 1] if header_end > 0 else [lines[0]]
        header_text = '\n'.join(header_lines).strip()
        body = '\n'.join(lines[header_end + 1:]).strip() if header_end + 1 < len(lines) else '\n'.join(lines[1:]).strip()
        
        # Try to split verse text from reference
        # Pattern: *"verse text"* — Reference (ARA)
        match = re.match(r'^\*["\u201c]?(.*?)["\u201d]?\*\s*[-—–]\s*(.+?\(ARA\))', header_text, re.DOTALL)
        if match:
            verse_text = match.group(1).strip()
            reference = match.group(2).strip()
            new_header = f'> *"{verse_text}"*\n>\n> — **{reference}**'
        else:
            # Fallback: just wrap the whole header in blockquote
            # Try simpler pattern: *text* — Ref (ARA) or *text — Ref (ARA)*
            match2 = re.match(r'^\*(.*?)\*\s*[-—–]\s*(.+?\(ARA\))', header_text, re.DOTALL)
            if match2:
                verse_text = match2.group(1).strip()
                reference = match2.group(2).strip()
                new_header = f'> *"{verse_text}"*\n>\n> — **{reference}**'
            else:
                # Last resort: just wrap everything as blockquote
                blockquoted = '\n'.join([f'> {l}' for l in header_text.split('\n')])
                new_header = blockquoted
        
        new_md = f'{new_header}\n\n{body}'
        
        # Update in DB
        c.table('devocionais_final').update({'conteudo_md': new_md}).eq('id', d['id']).execute()
        fixed += 1
        
        # Get semana/dia for logging
        plano = c.table('plano_devocional').select('semana, dia_semana').eq('id', d['plano_id']).maybe_single().execute()
        if plano.data:
            print(f"  ✅ S{plano.data['semana']}D{plano.data['dia_semana']} corrigido")

print(f"\n{'='*50}")
print(f"✅ {fixed} devocionais corrigidos")
print(f"⏭  {skipped} já estavam corretos")
print(f"📊 Total: {fixed + skipped}")
