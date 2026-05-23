import pdfplumber
import re
from pathlib import Path

PDF_PATH = Path(r"c:\Users\ryzen\Downloads\Antigravity\TrilhaGracaSoberana\HInario Novo Cantico\novo_cantico.pdf")

def find_hymn(hymn_num):
    pdf = pdfplumber.open(PDF_PATH)
    # Procurar por linhas como "32 O Deus fiel", "100 ", "157 " ou similares
    # Vamos verificar cada página
    target_pattern = re.compile(rf"^\s*{hymn_num}\s+[A-Z\d]", re.IGNORECASE)
    target_pattern_simple = re.compile(rf"^\s*{hymn_num}\b", re.IGNORECASE)
    
    for idx, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines):
            # Se a linha começa com o número do hino
            if line.strip().startswith(str(hymn_num)):
                # Verificar se é o início do hino
                parts = line.strip().split()
                if parts and parts[0] == str(hymn_num):
                    # Encontramos! Vamos retornar todo o texto da página a partir dali, ou a página inteira
                    # Geralmente um hino cabe em uma ou duas páginas. Podemos retornar o texto limpo da página.
                    return idx + 1, text
    return None, None

for num in [1, 32, 100, 150, 200, 300, 400]:
    page_num, text = find_hymn(num)
    if page_num:
        print(f"Hino {num} encontrado na página {page_num}!")
        print("Primeiras linhas:")
        print("\n".join(text.splitlines()[:5]))
        print("-" * 50)
    else:
        print(f"Hino {num} NÃO encontrado.")
        print("-" * 50)
