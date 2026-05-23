import sys
from pathlib import Path

# Add workspace to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from nicodemos_pipeline_100.db.client import get_devocionais_by_semana

output_path = Path(r"C:\Users\ryzen\.gemini\antigravity-ide\brain\cccf21cc-73ee-4685-9069-b6d3fb2d31a2\preview_semana_6_7.md")

md = []
md.append("# 📖 Demonstração das Devocionais — Semanas 6 e 7")
md.append("\nEste documento apresenta os roteiros litúrgicos completos gerados para as **Semanas 6 e 7** (Dias 36 a 49) do Culto Doméstico no novo **Modelo Culto Doméstico Vivo e Interativo**.")
md.append("\n---\n")

for sem in [6, 7]:
    md.append(f"\n## 📅 SEMANA {sem}\n")
    devs = get_devocionais_by_semana(sem)
    # Order by dia
    devs = sorted(devs, key=lambda x: x["dia"])
    for dev in devs:
        md.append(f"\n### ☕ Dia {dev['dia']:03d} — {dev['ref']}")
        md.append(f"\n**Pergunta de Reflexão (Adultos):** {dev['pergunta_reflexao']}\n")
        md.append(dev["conteudo_md"])
        md.append("\n---\n")

output_path.write_text("\n".join(md), encoding="utf-8")
print(f"Exportado com sucesso para {output_path}!")
