"""
Reorganização: Atualiza os hinos das devocionais dos Dias 1 a 150 no banco de dados
para corresponderem à lista exata de 196 hinos conhecidos do usuário.
Usa as versões pré-formatadas se disponíveis, ou formata de forma rica com o AgenteFormatadorHino.
"""
import sys
import io
import re
import json
import time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar workspace ao path para importar os módulos
import os
sys.path.insert(0, r'c:\Users\ryzen\Downloads\Antigravity\TrilhaGracaSoberana')

from nicodemos_pipeline_100.db.client import get_client
from nicodemos_pipeline_100.agents.hymn_formatter import AgenteFormatadorHino
from nicodemos_pipeline_100.pipeline import _limpar_cabecalhos

# Lista de hinos conhecidos do usuário
raw_hymns = """
2,3,4,6,9,10,11,13,14,1617 18 19 21 22 25 26 27 28 32 33  37  39 40  42 43 47 49 51 52 54 57 61 62 63 64 67 68 71 74 78 86 88 89 92 93 94  97 99 102 104 105 106 107 108  109 110 110-a 111 112 113 114 115 116 117 120 121 127 128 129 130 131 132 134 135 136 137 138 144 145 146 147 148 150 151 153 155 156 157 159 161 162 163 164 165  169   172 176 178 179 180 183 184 185 186 187 191 192 193 194 198 199 201 202 205 209 210 211 213 218 221 222 225 226 227 230 231 232 237 239 240 241 243 245 249 250 251 253 254 260 266 267 268 269 270 272 274 282 283 274 285 286 287 288 289 292 296 297 298 299 300 303 304 306 307 308 311 312 313 315 316 318 319 320 321 334 335 336 339 340 341 350 351 352 354 359 362 367 368 373 374 379 382 392 395 396 397
"""

def parse_hymns(text):
    text = text.replace("1617", "16, 17")
    tokens = re.split(r'[\s,]+', text.strip())
    hymns = []
    for token in tokens:
        if not token:
            continue
        if re.match(r'^\d+$', token) or re.match(r'^\d+-[a-zA-Z]$', token):
            hymns.append(token.lower())
    return hymns

# Gerar lista ordenada de hinos únicos do usuário
hymns_list_raw = parse_hymns(raw_hymns)
hymns_list = []
seen = set()
for h in hymns_list_raw:
    if h not in seen:
        seen.add(h)
        hymns_list.append(h)

def main():
    sb = get_client()
    formatter = AgenteFormatadorHino()
    
    # 1. Carregar letras do JSON
    letras_path = r"C:\Users\ryzen\.gemini\antigravity-ide\brain\cccf21cc-73ee-4685-9069-b6d3fb2d31a2\scratch\novo_cantico_letras.json"
    with open(letras_path, "r", encoding="utf-8") as f:
        letras_data = json.load(f)
        
    # 2. Carregar hinos pré-formatados (se existirem)
    formatted_path = r"c:\Users\ryzen\Downloads\Antigravity\TrilhaGracaSoberana\nicodemos_pipeline_100\utils\novo_cantico_formatado.json"
    with open(formatted_path, "r", encoding="utf-8") as f:
        formatted_data = json.load(f)
        
    # 3. Buscar todas as devocionais dos Dias 1 a 150
    print("Buscando devocionais atuais do Supabase (Dias 1 a 150)...")
    res = sb.table("nico_devocionais_final").select("id, dia, conteudo_md").gte("dia", 1).lte("dia", 150).order("dia").execute()
    
    if not res.data:
        print("Nenhuma devocional encontrada no banco.")
        return
        
    devocionais = res.data
    print(f"Total de {len(devocionais)} devocionais carregadas para remapeamento.")
    
    updated = 0
    for row in devocionais:
        dia = row["dia"]
        md = row["conteudo_md"]
        
        # Mapeamento do hino correspondente ao dia
        hymn_key = hymns_list[dia - 1]
        
        # Obter letra bruta e título correspondente ao hino
        letra_crua = ""
        hymn_title = ""
        
        if hymn_key == "110-a":
            # Extração especial do 110-A
            raw_text_110 = letras_data["110"]
            partes = raw_text_110.split("110-A")
            letra_crua = partes[1].strip()
            hymn_title = "110-A - Crer e observar"
        elif hymn_key == "110":
            raw_text_110 = letras_data["110"]
            partes = raw_text_110.split("110-A")
            letra_crua = partes[0].replace("110 - A vida com Jesus", "").strip()
            hymn_title = "110 - A vida com Jesus"
        else:
            raw_text = letras_data[hymn_key]
            # O título é a primeira linha
            linhas = raw_text.splitlines()
            hymn_title = linhas[0].strip()
            letra_crua = "\n".join(linhas[1:]).strip()
            
        # Obter letra formatada
        # Tentar ler do formatted_data se a chave for compatível
        simplified_key = hymn_key.replace("-", "")
        lyrics_formatted = ""
        
        if simplified_key in formatted_data:
            lyrics_formatted = formatted_data[simplified_key]["formatado"]
            hymn_title_display = formatted_data[simplified_key]["titulo"]
        else:
            # Formatar usando o AgenteFormatadorHino
            print(f"  [IA] Formatando Hino {hymn_title} para o Dia {dia}...")
            lyrics_formatted = formatter.formatar(hymn_title, letra_crua)
            hymn_title_display = hymn_title
            
        # Limpar cabeçalhos da devocional
        cleaned_md = _limpar_cabecalhos(md)
        
        # Substituir a seção 7 com o novo hino
        header_match = re.search(r'###\s*7\..*?Melodia no Lar[^\n]*\n', cleaned_md, re.IGNORECASE)
        if header_match:
            index = header_match.start()
            conteudo_antes = cleaned_md[:index]
            new_section_7 = f"### 7. Melodia no Lar\n\n[{hymn_title_display}]\n\n{lyrics_formatted}\n"
            new_md = conteudo_antes.strip() + "\n\n" + new_section_7
        else:
            new_section_7 = f"\n\n### 7. Melodia no Lar\n\n[{hymn_title_display}]\n\n{lyrics_formatted}\n"
            new_md = cleaned_md.strip() + new_section_7
            
        # Salvar no banco
        if new_md != md:
            sb.table("nico_devocionais_final").update({
                "conteudo_md": new_md
            }).eq("id", row["id"]).execute()
            updated += 1
            print(f"  -> Dia {dia:03d} atualizado com Hino: [{hymn_title_display}]")
        else:
            print(f"  -> Dia {dia:03d} já estava no padrão")
            
        time.sleep(0.2) # Evitar requisições muito aceleradas no Supabase
        
    print(f"\n✅ Remapeamento concluído com sucesso! Total de devocionais atualizadas: {updated}")

if __name__ == '__main__':
    main()
