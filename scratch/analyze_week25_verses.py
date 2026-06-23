import sys
from pathlib import Path
from ryle_pipeline.utils.bible_fetcher import obter_texto_biblico

# Setup encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

dias_ref = {
    1: "Hebreus 12.1-3",
    2: "2 Timóteo 4.6-8",
    3: "Filipenses 3.12-16",
    4: "1 Coríntios 9.24-27",
    5: "Gálatas 6.7-10",
    6: "Salmo 90.10-12",
    7: "Apocalipse 2.10-11",
}

for dia, ref in dias_ref.items():
    print(f"\n=== DIA {dia} ({ref}) ===")
    
    # 1. Obter da ARA oficial
    ara_text = obter_texto_biblico(ref)
    print(f"ARA Oficial:\n  {ara_text}")
    
    # 2. Obter do arquivo baixado
    md_file = Path(f"scratch/semana25_dia{dia}.md")
    if md_file.exists():
        md = md_file.read_text(encoding='utf-8')
        lines = md.splitlines()
        verse_lines = []
        for line in lines:
            if line.startswith(">"):
                verse_lines.append(line)
        print("No Markdown:")
        for vl in verse_lines:
            print(f"  {vl}")
    else:
        print("Arquivo MD não encontrado.")
