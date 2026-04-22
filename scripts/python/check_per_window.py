"""Conta devocionais aprovados por janela de cookie."""
import re

lines = open('ryle_pipeline.log', encoding='utf-8').readlines()

# Janela 1: 20:51 - 22:24 (primeiro cookie)
# Janela 2: 22:42 - 00:40 (segundo cookie, notebooklm-mcp-auth)
j1, j2, j_fallback = [], [], []

for line in lines:
    match = re.search(r'(\d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2})).*?(S\d+D\d+) APROVADO score=([\d.]+) v=(\d+) palavras=(\d+)', line.strip())
    if match:
        ts_full, ts_time, sd, score, ver, words = match.groups()
        date_part = ts_full.split(' ')[0]
        
        # Janela 1: 05 abr 20:51 - 22:24
        if date_part == '2026-04-05' and '20:51' <= ts_time <= '22:24':
            j1.append((sd, score, ver, words))
        # Janela 2: 05 abr 22:42 - 06 abr 00:40
        elif (date_part == '2026-04-05' and ts_time >= '22:42') or (date_part == '2026-04-06' and ts_time <= '00:40'):
            j2.append((sd, score, ver, words))
        else:
            j_fallback.append((sd, score, ver, words))

print("=" * 55)
print("  JANELA 1 — Cookie manual (F12)")
print(f"  Período: 20:51 - 22:24 (~1h33)")
print(f"  Devocionais com pesquisa REAL: {len(j1)}")
for sd, score, ver, words in j1:
    print(f"    {sd:8s} | score={score} | v={ver} | {words}p")

print()
print("=" * 55)
print("  JANELA 2 — Cookie notebooklm-mcp-auth")
print(f"  Período: 22:42 - 00:40 (~2h)")
print(f"  Devocionais com pesquisa REAL: {len(j2)}")
for sd, score, ver, words in j2:
    print(f"    {sd:8s} | score={score} | v={ver} | {words}p")

print()
print("=" * 55)
print(f"  TOTAL COM PESQUISA REAL:  {len(j1) + len(j2)} devocionais")
print(f"  TOTAL COM FALLBACK:       {len(j_fallback)} devocionais")
print("=" * 55)
