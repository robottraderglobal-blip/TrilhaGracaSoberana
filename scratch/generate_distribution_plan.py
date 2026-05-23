import json
from pathlib import Path

# Paths
WORKSPACE = Path(r"c:\Users\ryzen\Downloads\Antigravity\TrilhaGracaSoberana")
PLANO_100 = WORKSPACE / "100_devocionais" / "plano_100dias.json"
PLANO_50 = WORKSPACE / "100_devocionais" / "plano_expansao_50.json"
OUTPUT_ARTIFACT = Path(r"C:\Users\ryzen\.gemini\antigravity-ide\brain\cccf21cc-73ee-4685-9069-b6d3fb2d31a2\cifras_distribution_plan.md")

# Load planos
plano_100_data = json.loads(PLANO_100.read_text(encoding="utf-8"))
plano_50_data = json.loads(PLANO_50.read_text(encoding="utf-8"))

# Load hymn titles
hymn_titles_file = Path(r"C:\Users\ryzen\.gemini\antigravity-ide\brain\cccf21cc-73ee-4685-9069-b6d3fb2d31a2\scratch\hymn_titles.json")
hymns = json.loads(hymn_titles_file.read_text(encoding="utf-8"))

# Filter to get only main hymns (excluding suffixes and 400s)
# Main hymns are 1 to 61
main_hymns = []
for i in range(1, 62):
    filename = f"{i}.txt"
    if filename in hymns:
        main_hymns.append((i, hymns[filename]))

# Prepare 150 days list
days_list = []
for week in plano_100_data:
    for day in week["days"]:
        days_list.append({
            "semana": week["week"],
            "dia": day["day"],
            "ref": day["ref"],
            "t": day["t"]
        })

for week in plano_50_data:
    for day in week["days"]:
        days_list.append({
            "semana": week["week"],
            "dia": day["day"],
            "ref": day["ref"],
            "t": day["t"]
        })

# We have exactly 150 days. Let's do a systematic rotation of the 61 main hymns
# Rotation index: i % 61
md_content = """# Plano de Distribuição de Hinos — 150 Dias de Culto Doméstico

Este documento apresenta o planejamento estratégico para a distribuição sistemática das **61 cifras do Hinário Novo Cântico (NC)** (disponíveis no repositório `savioa/cifras-novo-cantico`) ao longo dos **150 dias** de devocionais (Culto Doméstico de 100 dias + Expansão de 50 dias).

---

## 🎯 Diretrizes do Planejamento
1. **Diversidade Máxima (Sem Repetição Precoce)**: Executamos uma rotação sistemática dos 61 hinos exclusivos. Isso garante que nenhum hino seja repetido em menos de **61 dias** (cerca de 9 semanas).
2. **Autossuficiência**: A cifra e letra completas do hino serão embutidas em texto ao final de cada devocional.
3. **Mapeamento Preciso**: Cada um dos 150 dias tem um hino pré-definido, evitando qualquer duplicidade desordenada.

---

## 📊 Tabela de Distribuição Completa: Dias 1 a 150 (Semanas 1 a 23)

| Dia | Semana | Referência Bíblica | Tema/Versículo | Hino Novo Cântico Selecionado | Cifra no GitHub |
| :---: | :---: | :--- | :--- | :--- | :---: |
"""

for idx, d in enumerate(days_list):
    hymn_idx = idx % len(main_hymns)
    hymn_num, hymn_title = main_hymns[hymn_idx]
    
    # Escape markdown pipes in text
    verse_text = d["t"].replace("|", "\\|")
    if len(verse_text) > 80:
        verse_text = verse_text[:77] + "..."
        
    md_content += f"| **{d['dia']:03d}** | S{d['semana']:02d} | {d['ref']} | *{verse_text}* | **{hymn_title}** | [Visualizar](https://github.com/savioa/cifras-novo-cantico/blob/main/txt/{hymn_num}.txt) |\n"

md_content += """
---

## 📈 Resumo do Planejamento de 150 Dias
- **Total de dias mapeados:** 150
- **Total de hinos exclusivos no repositório:** 61
- **Frequência de repetição:** 
  - Hinos do **1 ao 28**: Cantados 3 vezes em 150 dias.
  - Hinos do **29 ao 61**: Cantados 2 vezes em 150 dias.
- **Janela de segurança contra repetições:** **Exatamente 61 dias**. Nenhuma música se repetirá em menos de 8 semanas, garantindo máxima variedade para a adoração do lar.
"""

OUTPUT_ARTIFACT.write_text(md_content, encoding="utf-8")
print(f"Gerado com sucesso para 150 dias: {OUTPUT_ARTIFACT}")
