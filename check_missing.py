import sys, os
sys.path.insert(0, os.getcwd())
from ryle_pipeline.db.client import get_client

client = get_client()
res = client.table("plano_devocional").select("id, semana, dia_semana, status").execute()
data = res.data

published = [d for d in data if d["status"] == "published"]
pending = [d for d in data if d["status"] == "pending"]
error = [d for d in data if d["status"] not in ("published", "pending")]

with open("report_missing.txt", "w", encoding="utf-8") as f:
    f.write(f"Total: {len(data)}\n")
    f.write(f"Published: {len(published)}\n")
    f.write(f"Pending: {len(pending)}\n")
    f.write(f"Other statuses: {len(error)}\n\n")

    if pending:
        f.write("Pending:\n")
        f.write("\n".join(f"  Semana {p['semana']}, Dia {p['dia_semana']}, id: {p['id']}" for p in pending) + "\n\n")

    if error:
        f.write("Other statuses:\n")
        f.write("\n".join(f"  Semana {e['semana']}, Dia {e['dia_semana']}, status: {e['status']}, id: {e['id']}" for e in error) + "\n")
