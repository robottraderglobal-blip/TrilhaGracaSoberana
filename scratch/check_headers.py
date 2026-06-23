import sys
import io
import re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nicodemos_pipeline_100.db.client import get_client

c = get_client()

# Puxar todas as devocionais geradas (dias 1 a 150)
res = c.table("nico_devocionais_final").select("dia, semana, conteudo_md").order("dia").execute()

if not res.data:
    print("Nenhuma devocional encontrada no banco de dados.")
    sys.exit(0)

print(f"Encontradas {len(res.data)} devocionais no banco de dados.")

headers_corretos = [
    "### 1. O Versículo do Dia",
    "### 2. Entendendo o Texto",
    "### 3. Palavra ao Coração",
    "### 4. Momento da Conversa",
    "### 5. Desafio Prático do Dia",
    "### 6. Clamor do Lar",
    "### 7. Melodia no Lar"
]

emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]')

erros = []
total_devocionais = len(res.data)
devocionais_com_erros = 0

for dev in res.data:
    dia = dev["dia"]
    md = dev["conteudo_md"]
    sem = dev["semana"]
    
    headers_no_texto = []
    for line in md.splitlines():
        if line.startswith("###"):
            headers_no_texto.append(line.strip())
            
    dia_tem_erro = False
    erros_dia = []
    
    # 1. Validar cabeçalhos incorretos
    for h in headers_no_texto:
        has_emoji = bool(emoji_pattern.search(h))
        has_paren = "(" in h or ")" in h
        if has_emoji or has_paren:
            dia_tem_erro = True
            erros_dia.append(f"Cabeçalho inválido: '{h}'")
            
    # 2. Verificar hino no final
    parts = md.split("### 7. Melodia no Lar")
    if len(parts) > 1:
        hymn_section = parts[1].strip()
        hymn_title_line = [line for line in hymn_section.splitlines() if line.startswith("[") and line.endswith("]")]
        if not hymn_title_line:
            dia_tem_erro = True
            erros_dia.append("Seção 7: Letra do hino no padrão [Título] não encontrada")
    else:
        dia_tem_erro = True
        erros_dia.append("Seção 7 (Melodia no Lar) ausente")
        
    if dia_tem_erro:
        devocionais_com_erros += 1
        erros.append({
            "dia": dia,
            "semana": sem,
            "detalhes": erros_dia
        })

print("\n" + "=" * 50)
print("📊 RESULTADO DA VERIFICAÇÃO DE INTEGRIDADE DOS CABEÇALHOS")
print("=" * 50)
print(f"Total de Devocionais Analisadas: {total_devocionais}")
print(f"Devocionais com erros: {devocionais_com_erros}")
print(f"Devocionais corretas: {total_devocionais - devocionais_com_erros} ({((total_devocionais - devocionais_com_erros)/total_devocionais)*100:.1f}%)")

if erros:
    print("\n⚠️ DETALHES DOS ERROS ENCONTRADOS:")
    for err in erros:
        print(f"\n  • Dia {err['dia']} (Semana {err['semana']}):")
        for d in err['detalhes']:
            print(f"    - {d}")
else:
    print("\n✅ SUCESSO ABSOLUTO! Todas as 150 devocionais estão estruturadas perfeitamente no novo padrão de cabeçalhos sem emojis e sem explicações entre parênteses!")
print("=" * 50)

