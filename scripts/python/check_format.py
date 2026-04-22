from ryle_pipeline.db import client
c = client.get_client()

# Check which devocionals have the old italic format (without blockquote)
r = c.table('devocionais_final').select('plano_id, titulo, conteudo_md').execute()

broken = []
for d in r.data:
    md = d['conteudo_md'] or ''
    # The correct format starts with "> *" (blockquote + italic)
    # The broken format starts with just "*" (italic only, no blockquote)
    first_line = md.strip().split('\n')[0] if md.strip() else ''
    if first_line.startswith('*') and not first_line.startswith('> '):
        # Get the semana/dia
        plano = c.table('plano_devocional').select('semana, dia_semana').eq('id', d['plano_id']).maybe_single().execute()
        if plano.data:
            s, dia = plano.data['semana'], plano.data['dia_semana']
            broken.append(f"S{s}D{dia}: {d['titulo'][:50]}  -> '{first_line[:80]}'")

print(f"\n=== {len(broken)} devocionais com formatação quebrada ===")
for b in broken:
    print(b)
