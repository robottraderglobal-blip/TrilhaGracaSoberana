"""Analisa o log para determinar quando o NotebookLM parou de responder."""
import re

lines = open('ryle_pipeline.log', encoding='utf-8').readlines()

# Track cache SET sizes over time to detect when NLM stopped returning real data
# Real data = 1000+ chars, fallback "Sem dados" = ~115 chars
events = []
for line in lines:
    line = line.strip()
    
    # Cache SET events show the size of NLM responses
    match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[cache\] SET para chave .+?\.\.\. \((\d+) chars\)', line)
    if match:
        ts, chars = match.group(1), int(match.group(2))
        events.append((ts, chars, 'real' if chars > 200 else 'fallback'))
    
    # Also track Health check OK events
    match2 = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Health check OK', line)
    if match2:
        events.append((match2.group(1), 0, 'health_ok'))

# Find the transition point
print("=== Análise de Duração dos Cookies NotebookLM ===\n")

if not events:
    print("Nenhum evento encontrado no log.")
else:
    first_real = None
    last_real = None
    first_fallback_after_real = None
    
    for ts, chars, tipo in events:
        if tipo == 'real':
            if not first_real:
                first_real = ts
            last_real = ts
    
    # Find first fallback AFTER a real response
    found_real = False
    for ts, chars, tipo in events:
        if tipo == 'real':
            found_real = True
        elif tipo == 'fallback' and found_real:
            if not first_fallback_after_real:
                first_fallback_after_real = ts
    
    print(f"Primeiro dado REAL do NLM:    {first_real}")
    print(f"Último dado REAL do NLM:      {last_real}")
    if first_fallback_after_real:
        print(f"Primeiro FALLBACK (cookie caiu): {first_fallback_after_real}")
    
    # Show timeline of real vs fallback
    print(f"\n--- Timeline de respostas (chars salvos no cache) ---")
    prev_tipo = None
    for ts, chars, tipo in events:
        if tipo == 'health_ok':
            continue
        if tipo != prev_tipo:
            marker = "✅" if tipo == 'real' else "❌"
            print(f"\n  {marker} {ts} -> {tipo.upper()} ({chars} chars)")
            prev_tipo = tipo
        # Just count consecutive same-type
