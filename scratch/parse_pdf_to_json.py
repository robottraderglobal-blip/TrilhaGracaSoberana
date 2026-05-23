import pdfplumber
import json
import re
from pathlib import Path

PDF_PATH = Path(r"c:\Users\ryzen\Downloads\Antigravity\TrilhaGracaSoberana\HInario Novo Cantico\novo_cantico.pdf")
OUTPUT_JSON = Path(r"C:\Users\ryzen\.gemini\antigravity-ide\brain\cccf21cc-73ee-4685-9069-b6d3fb2d31a2\scratch\novo_cantico_letras.json")

def parse_pdf():
    print("Iniciando abertura do PDF...")
    pdf = pdfplumber.open(PDF_PATH)
    print(f"PDF aberto. Total de páginas: {len(pdf.pages)}")
    
    hymns = {}
    current_hymn_num = None
    current_hymn_lines = []
    
    # Padrão para detectar o início de um hino: número + espaço + letra maiúscula
    # Exemplo: "32 O Deus fiel", "100 A ti, ó Deus"
    hymn_start_pattern = re.compile(r"^\s*([1-9]\d{0,2})\s+([A-Z\xc0-\xdf].*)$")
    
    for idx, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text:
            continue
            
        lines = text.splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            # Verificar se inicia um novo hino
            match = hymn_start_pattern.match(line_str)
            if match:
                hymn_num = int(match.group(1))
                hymn_title = match.group(2).strip()
                
                # Se já vínhamos processando um hino, salvamos o anterior
                if current_hymn_num is not None:
                    hymns[current_hymn_num] = "\n".join(current_hymn_lines).strip()
                
                current_hymn_num = hymn_num
                current_hymn_lines = [f"{hymn_num} - {hymn_title}"]
            else:
                # Se não é início de hino, mas já temos um hino ativo, adicionamos a linha
                if current_hymn_num is not None:
                    # Ignorar rodapés óbvios ou cabeçalhos de página repetitivos se houver
                    if "www.novocantico.com.br" in line_str or "Hinário Novo Cântico" in line_str:
                        continue
                    current_hymn_lines.append(line_str)
                    
    # Salvar o último hino
    if current_hymn_num is not None:
        hymns[current_hymn_num] = "\n".join(current_hymn_lines).strip()
        
    print(f"Processamento concluído. Total de hinos catalogados: {len(hymns)}")
    
    # Salvar em JSON com codificação UTF-8
    OUTPUT_JSON.write_text(json.dumps(hymns, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Salvo com sucesso em: {OUTPUT_JSON}")

if __name__ == "__main__":
    parse_pdf()
