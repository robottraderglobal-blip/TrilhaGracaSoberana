import re

lines = open('ryle_pipeline.log', encoding='utf-8').readlines()

# Find the latest batch of S17-S20 results
results = []
for line in lines:
    match = re.search(r'(\d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2})).*?(S(1[7-9]|20)D\d+) APROVADO score=([\d.]+) v=(\d+) palavras=(\d+)', line.strip())
    if match:
        ts_full, ts_time, sd, _, score, ver, words = match.groups()
        results.append((ts_full, sd, score, ver, words))

# Show only the latest run (after 07:42 today)
latest = [r for r in results if r[0] >= '2026-04-06 07:42']
if not latest:
    latest = results[-28:]  # fallback: last 28

print("=== Resultados S17-S20 (última execução) ===\n")
for ts, sd, score, ver, words in latest:
    print(f"  {sd:8s} | score={score:5s} | v={ver} | {words}p | {ts}")

print(f"\n  Total: {len(latest)} devocionais aprovados")

# Check for auth errors / fallbacks in the same window
auth_errors = [l.strip() for l in lines if 'Auth expirado' in l and l.strip() >= '2026-04-06 07:42']
refresh_ok = [l.strip() for l in lines if 'Auth renovado' in l and l.strip() >= '2026-04-06 07:42']
fallback_lines = [l.strip() for l in lines if 'fallback' in l.lower() and any(f'S{s}D' in l for s in range(17,21)) and l.strip() >= '2026-04-06 07:42']

print(f"\n  🔑 Auth expirado detectado: {len(auth_errors)} vezes")
print(f"  ✅ Auth renovado com sucesso: {len(refresh_ok)} vezes")
print(f"  ⚠  Fallbacks: {len(fallback_lines)} vezes")

# Check cache sizes for real vs fallback
cache_sets = []
for line in lines:
    if line.strip() >= '2026-04-06 07:42' and '[cache] SET' in line:
        m = re.search(r'\((\d+) chars\)', line)
        if m:
            cache_sets.append(int(m.group(1)))

if cache_sets:
    real = [c for c in cache_sets if c > 200]
    fallback = [c for c in cache_sets if c <= 200]
    print(f"\n  📊 Cache: {len(real)} respostas reais (avg {sum(real)//len(real) if real else 0} chars)")
    print(f"  📊 Cache: {len(fallback)} respostas fallback")
