import re
import json
import os
import urllib.request

ARA_URL = "https://raw.githubusercontent.com/damarals/biblias/master/inst/json/ARA.json"
JSON_PATH = os.path.join(os.path.dirname(__file__), "ARA.json")

# Normalizações conhecidas de nomes e abreviações da ARA
LIVROS_MAP = {
    "salmo": "salmos",
    "salmos": "salmos",
    "i joão": "1 joão",
    "ii joão": "2 joão",
    "iii joão": "3 joão",
    "i pedro": "1 pedro",
    "ii pedro": "2 pedro",
    "i coríntios": "1 coríntios",
    "ii coríntios": "2 coríntios",
    "i tessalonicenses": "1 tessalonicenses",
    "ii tessalonicenses": "2 tessalonicenses",
    "i timóteo": "1 timóteo",
    "ii timóteo": "2 timóteo",
    "i samuel": "1 samuel",
    "ii samuel": "2 samuel",
    "i reis": "1 reis",
    "ii reis": "2 reis",
    "i crônicas": "1 crônicas",
    "ii crônicas": "2 crônicas",
}

def baixar_ara_se_necessario():
    if not os.path.exists(JSON_PATH):
        print("Baixando Bíblia ARA.json...")
        response = urllib.request.urlopen(ARA_URL)
        data = response.read()
        with open(JSON_PATH, "wb") as f:
            f.write(data)

def carregar_biblia():
    baixar_ara_se_necessario()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def normalizar_livro(livro: str) -> str:
    l_lower = livro.strip().lower()
    return LIVROS_MAP.get(l_lower, l_lower)

def obter_texto_biblico(referencia: str) -> str:
    """
    Ex: 'Provérbios 23.4-5' -> Retorna o texto exato dos versículos na versão ARA.
    Se não conseguir parsear, tenta retornar algo gracioso ou a referência original pura.
    """
    biblia = carregar_biblia()
    padrao = re.compile(r'^(.+?)\s+(\d+)\.(\d+)(?:-(\d+))?$')
    match = padrao.match(referencia.strip())
    
    if not match:
        return f"({referencia})"

    livro_nome = match.group(1)
    capitulo_str = match.group(2)
    v_inicio_str = match.group(3)
    v_fim_str = match.group(4)
    
    capitulo = int(capitulo_str)
    v_inicio = int(v_inicio_str)
    v_fim = int(v_fim_str) if v_fim_str else v_inicio

    livro_norm = normalizar_livro(livro_nome)
    
    # Busca o livro pela normalização
    livro_obj = None
    for b in biblia:
        if normalizar_livro(b["name"]) == livro_norm or normalizar_livro(b.get("abbrev", "")) == livro_norm:
            livro_obj = b
            break
            
    if not livro_obj:
        return f"({referencia})"
        
    try:
        cap_obj = livro_obj["chapters"][capitulo - 1] # 0-indexed
        versos_texto = []
        # v_inicio e v_fim são 1-indexed. O array de versos é 0-indexed.
        for v in range(v_inicio, v_fim + 1):
            if v - 1 < len(cap_obj):
                versos_texto.append(f"{v} {cap_obj[v - 1]}")
        
        texto_final = " ".join(versos_texto)
        return texto_final
    except Exception as e:
        # Fallback graceful
        return ""

if __name__ == "__main__":
    # Teste
    print(obter_texto_biblico("Provérbios 23.4-5"))
    print(obter_texto_biblico("Salmo 131.1-3"))
    print(obter_texto_biblico("1 Timóteo 6.13-16"))
