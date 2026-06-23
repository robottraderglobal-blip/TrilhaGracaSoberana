from nicodemos_pipeline_100.db.client import get_client
c = get_client()
res = c.table("nico_plano").select("dia, semana").order("dia").execute()
dias = res.data
semanas = {}
for d in dias:
    sem = d["semana"]
    semanas[sem] = semanas.get(sem, []) + [d["dia"]]

for sem, ds in sorted(semanas.items()):
    print(f"Semana {sem}: dias {ds[0]} a {ds[-1]} ({len(ds)} dias)")
