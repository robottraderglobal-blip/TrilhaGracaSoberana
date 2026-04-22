from ryle_pipeline.db import client
c = client.get_client()
r = c.table('plano_devocional').select('semana, dia_semana, status').gte('semana', 16).lte('semana', 25).order('semana').order('dia_semana').execute()
for d in r.data:
    print(f"S{d['semana']}D{d['dia_semana']}: {d['status']}")
