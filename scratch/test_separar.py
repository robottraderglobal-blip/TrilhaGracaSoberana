import re
from revisar_portugues import separar_cabecalho_e_corpo, aplicar_correcoes

# No overriding sys.stdout

with open("scratch/semana25_dia1.md", "r", encoding="utf-8") as f:
    text = f.read()

ref = "Hebreus 12.1-3"
headers, body = separar_cabecalho_e_corpo(text, ref)
print("HEADERS:")
for h in headers:
    print(f"  [{h}]")
print("BODY PARAS COUNT:", len(body))
print("First body para:", body[0][:100] if body else "None")

text_rev, corrs = aplicar_correcoes(text, ref)
print("CORRECTIONS:")
for c in corrs:
    print(f"  {c}")
