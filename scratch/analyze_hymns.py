import sys
import io
import re
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Lista de hinos passada pelo usuário (copiada exatamente)
raw_input = """
2,3,4,6,9,10,11,13,14,1617 18 19 21 22 25 26 27 28 32 33  37  39 40  42 43 47 49 51 52 54 57 61 62 63 64 67 68 71 74 78 86 88 89 92 93 94  97 99 102 104 105 106 107 108  109 110 110-a 111 112 113 114 115 116 117 120 121 127 128 129 130 131 132 134 135 136 137 138 144 145 146 147 148 150 151 153 155 156 157 159 161 162 163 164 165  169   172 176 178 179 180 183 184 185 186 187 191 192 193 194 198 199 201 202 205 209 210 211 213 218 221 222 225 226 227 230 231 232 237 239 240 241 243 245 249 250 251 253 254 260 266 267 268 269 270 272 274 282 283 274 285 286 287 288 289 292 296 297 298 299 300 303 304 306 307 308 311 312 313 315 316 318 319 320 321 334 335 336 339 340 341 350 351 352 354 359 362 367 368 373 374 379 382 392 395 396 397
"""

# Função para extrair números e padrões como '110-a'
def parse_hymns(text):
    # Tratar '1617' especificamente
    text = text.replace("1617", "16, 17")
    
    # Encontrar todos os tokens separados por espaços, vírgulas, etc.
    tokens = re.split(r'[\s,]+', text.strip())
    hymns = []
    for token in tokens:
        if not token:
            continue
        # Tratar '110-a' ou apenas dígitos
        if re.match(r'^\d+$', token) or re.match(r'^\d+-[a-zA-Z]$', token):
            hymns.append(token.lower())
    return hymns

hymns_list = parse_hymns(raw_input)

# Remover duplicados mantendo a ordem de aparição para análise
unique_hymns = []
seen = set()
for h in hymns_list:
    if h not in seen:
        seen.add(h)
        unique_hymns.append(h)

print(f"Total de hinos passados: {len(hymns_list)}")
print(f"Total de hinos únicos: {len(unique_hymns)}")
print("Hinos únicos detectados:")
print(", ".join(unique_hymns))

# Cruzamento com o novo_cantico_formatado.json para ver se todos os hinos listados existem na nossa base oficial
formatted_path = r"c:\Users\ryzen\Downloads\Antigravity\TrilhaGracaSoberana\nicodemos_pipeline_100\utils\novo_cantico_formatado.json"
try:
    with open(formatted_path, "r", encoding="utf-8") as f:
        nc_data = json.load(f)
except Exception as e:
    print(f"Erro ao abrir novo_cantico_formatado.json: {e}")
    nc_data = {}

missing = []
for h in unique_hymns:
    # Tratar '110-a' -> '110a' para ver no JSON
    simplified_h = h.replace("-", "")
    # Tentar chaves "110a" ou "110-a" ou "2" etc.
    if simplified_h not in nc_data and h not in nc_data:
        missing.append(h)

print(f"\nHinos ausentes do novo_cantico_formatado.json: {len(missing)}")
if missing:
    print(" -> " + ", ".join(missing))
else:
    print(" -> Todos os hinos listados estão presentes no banco de dados pré-formatado!")
