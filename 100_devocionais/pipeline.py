#!/usr/bin/env python3
import json, os, subprocess, time, sys, re
from pathlib import Path

BASE = Path('/home/claude/pipeline')
SKILL_GERADOR = (BASE / 'SKILL_gerador_devocional.md').read_text()
SKILL_REVISOR = (BASE / 'SKILL_revisor_devocional.md').read_text()
PLANO_RAW     = json.loads((BASE / 'plano_100dias.json').read_text())
OUTPUTS       = BASE / 'outputs'
LOGS          = BASE / 'logs'
OUTPUTS.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)
LOG_FILE      = LOGS / 'revisoes.jsonl'
PROGRESS_FILE = LOGS / 'progress.json'

API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
MODEL   = 'claude-haiku-4-5-20251001'

dias = [d for week in PLANO_RAW for d in week['days']]

def api_call(system_prompt, user_message, retries=3):
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 2000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    })
    for attempt in range(retries):
        result = subprocess.run([
            'curl', '-s', '--max-time', '60',
            'https://api.anthropic.com/v1/messages',
            '-H', 'content-type: application/json',
            '-H', 'anthropic-version: 2023-06-01',
            '-H', f'x-api-key: {API_KEY}',
            '-d', payload
        ], capture_output=True, text=True)
        try:
            data = json.loads(result.stdout)
            if 'error' in data:
                raise ValueError(data['error']['message'])
            return data['content'][0]['text']
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)
            else:
                raise RuntimeError(f"API falhou: {e} | raw: {result.stdout[:200]}")

def load_progress():
    try:    return json.loads(PROGRESS_FILE.read_text())['lastCompleted']
    except: return 0

def save_progress(n):
    PROGRESS_FILE.write_text(json.dumps({'lastCompleted': n}))

def log_entry(entry):
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def extract_status(text):
    if '❌' in text or 'REQUER REESCRITA' in text: return 'REESCRITA'
    if '⚠️' in text or 'APROVADO COM AJUSTES' in text: return 'AJUSTADO'
    return 'APROVADO'

def extract_final_text(revisao, devocional):
    marker = revisao.find('### Texto final:')
    if marker != -1:
        return revisao[marker + 16:].strip()
    # fallback: find first italic verse line
    for i, line in enumerate(revisao.split('\n')):
        if line.strip().startswith('*"') or line.strip().startswith('_"'):
            return '\n'.join(revisao.split('\n')[i:]).strip()
    return devocional.strip()

def process_day(dia, tentativa):
    user_g = f"DIA: {dia['day']}\nVERSÍCULO: {dia['ref']} — {dia['t']}"
    print(f"    [Gerador]...", flush=True)
    devocional = api_call(SKILL_GERADOR, user_g)
    time.sleep(1)

    user_r = f"DIA: {dia['day']}\nVERSÍCULO: {dia['ref']} — {dia['t']}\nDEVOCIONAL GERADA:\n{devocional}"
    print(f"    [Revisor]...", flush=True)
    revisao = api_call(SKILL_REVISOR, user_r)
    time.sleep(1)

    status = extract_status(revisao)
    texto_final = devocional if status == 'REESCRITA' else extract_final_text(revisao, devocional)
    return devocional, revisao, status, texto_final

def run():
    if not API_KEY:
        print("ERRO: variável ANTHROPIC_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)

    start = load_progress()
    total = len(dias)
    print(f"\n{'='*50}")
    print(f"  PIPELINE — 100 DIAS DE CULTO DOMÉSTICO")
    print(f"  Modelo: {MODEL}")
    print(f"  Retomando do dia {start+1}/{total}")
    print(f"{'='*50}\n")

    for i in range(start, total):
        dia = dias[i]
        num = str(dia['day']).zfill(3)
        print(f"Dia {dia['day']:>3}/100  {dia['ref']}", flush=True)

        resultado = None
        for tentativa in range(1, 3):
            try:
                devocional, revisao, status, texto_final = process_day(dia, tentativa)
                log_entry({
                    'dia': dia['day'], 'ref': dia['ref'],
                    'tentativa': tentativa, 'status': status,
                    'palavras': len(texto_final.split()),
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                })
                print(f"    Status: {status} | {len(texto_final.split())} palavras", flush=True)
                resultado = (status, texto_final)
                if status != 'REESCRITA':
                    break
                if tentativa < 2:
                    print(f"    Reescrita — tentativa 2...", flush=True)
                    time.sleep(2)
            except Exception as e:
                print(f"    ERRO tentativa {tentativa}: {e}", flush=True)
                log_entry({'dia': dia['day'], 'ref': dia['ref'], 'tentativa': tentativa,
                           'status': 'ERRO', 'erro': str(e),
                           'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
                time.sleep(5)

        if resultado:
            status, texto_final = resultado
            sufixo = '_REVISAR' if status == 'REESCRITA' else ''
            fname = OUTPUTS / f"dia_{num}{sufixo}.md"
            fname.write_text(f"# Dia {dia['day']} — {dia['ref']}\n\n{texto_final}\n", encoding='utf8')

        save_progress(i + 1)
        pct = (i + 1) / total * 100
        print(f"    Salvo. [{i+1}/{total}] {pct:.0f}%\n", flush=True)

        if i < total - 1:
            time.sleep(1.5)

    print(f"\n{'='*50}")
    print(f"  PIPELINE CONCLUÍDO — {total} devocionais geradas")
    print(f"  Saída: {OUTPUTS}")
    print(f"  Log:   {LOG_FILE}")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    run()
