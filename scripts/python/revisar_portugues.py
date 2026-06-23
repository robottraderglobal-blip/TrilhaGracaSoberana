#!/usr/bin/env python3
"""
Agente Revisor de Português — Devocionais Publicadas
=====================================================
Busca devocionais de uma semana no Supabase, aplica correções automáticas
de português (vocativos, demonstrativos, pontuação, estilo) e atualiza
o banco com a versão revisada.

Uso:
    python scripts/python/revisar_portugues.py --semana 15
    python scripts/python/revisar_portugues.py --semana 15 --dia 3
    python scripts/python/revisar_portugues.py --semana 15 --dry-run
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Carregar .env ──────────────────────────────────────────
ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

from supabase import create_client
from ryle_pipeline.utils.bible_fetcher import obter_texto_biblico

# Fix Windows console encoding for emoji/unicode
import io
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY precisam estar no .env")
    sys.exit(1)

sb = create_client(SUPABASE_URL, SUPABASE_KEY)


# ═══════════════════════════════════════════════════════════
# Regras de Correção Automática
# ═══════════════════════════════════════════════════════════

class Correcao:
    """Registro de uma correção aplicada."""
    def __init__(self, tipo: str, antes: str, depois: str, contexto: str = ""):
        self.tipo = tipo
        self.antes = antes
        self.depois = depois
        self.contexto = contexto

    def __repr__(self):
        return f"[{self.tipo}] '{self.antes}' → '{self.depois}'"


# Helper to separate header and body
def separar_cabecalho_e_corpo(conteudo_md: str, referencia: str) -> tuple[list[str], list[str]]:
    paragraphs = [p.strip() for p in conteudo_md.split("\n\n") if p.strip()]
    header_paragraphs = []
    body_paragraphs = []
    in_header = True
    for i, p in enumerate(paragraphs):
        if not in_header:
            body_paragraphs.append(p)
            continue
            
        is_blockquote = p.startswith(">")
        contains_ref = (referencia.lower() in p.lower()) if referencia else False
        contains_ara = ("ara)" in p.lower()) or ("(ara)" in p.lower())
        
        if i == 0:
            header_paragraphs.append(p)
        elif i == 1 and (is_blockquote or contains_ref or contains_ara or (p.startswith("*") and p.endswith("*"))):
            header_paragraphs.append(p)
        elif i == 2 and (is_blockquote or contains_ref or contains_ara):
            header_paragraphs.append(p)
        else:
            in_header = False
            body_paragraphs.append(p)
            
    return header_paragraphs, body_paragraphs


def aplicar_correcoes(texto: str, texto_biblico: str = None) -> tuple[str, list[Correcao]]:
    """Aplica todas as regras de correção ao texto. Retorna (texto_corrigido, lista_de_correções)."""
    correcoes: list[Correcao] = []
    original = texto

    # Separar cabeçalho e corpo se a referência for fornecida
    if texto_biblico:
        headers, body_paras = separar_cabecalho_e_corpo(texto, texto_biblico)
        
        # Obter texto oficial da ARA
        try:
            ara_text = obter_texto_biblico(texto_biblico)
        except Exception as e:
            ara_text = None
            
        if ara_text:
            cabecalho_novo = f"> *\"{ara_text.strip()}\"*\n>\n> — **{texto_biblico} (ARA)**"
            
            # Comparação simplificada para ver se mudou significativamente
            cabecalho_antigo_raw = "\n\n".join(headers)
            clean_antigo = re.sub(r'[^a-zA-Z0-9áéíóúâêôãõç]', '', cabecalho_antigo_raw).lower()
            clean_novo = re.sub(r'[^a-zA-Z0-9áéíóúâêôãõç]', '', cabecalho_novo).lower()
            
            if clean_antigo != clean_novo:
                resumo_antigo = cabecalho_antigo_raw.replace("\n", " ")[:60]
                resumo_novo = cabecalho_novo.replace("\n", " ")[:60]
                correcoes.append(Correcao("versículo-ara", f"Antigo: {resumo_antigo}...", f"ARA: {resumo_novo}..."))
            
            header_text = cabecalho_novo
        else:
            # Garante apenas que as linhas existentes comecem com '>'
            headers_formatados = []
            for h in headers:
                linhas_h = []
                for line in h.splitlines():
                    line = line.strip()
                    if line and not line.startswith(">"):
                        line = f"> {line}"
                    elif not line:
                        line = ">"
                    linhas_h.append(line)
                headers_formatados.append("\n".join(linhas_h))
            header_text = "\n\n".join(headers_formatados)
    else:
        # Fallback sem referência
        paragraphs = [p.strip() for p in texto.split("\n\n") if p.strip()]
        header_text = "\n\n".join(paragraphs[:2]) if len(paragraphs) >= 2 else texto
        body_paras = paragraphs[2:] if len(paragraphs) >= 2 else []

    # Limpar parágrafos do corpo
    body_paras_cleaned = []
    for p in body_paras:
        p_clean = p.strip()
        
        # 1. Remover divisores horizontais --- ou *** ou ___
        if re.match(r'^[-*_]{3,}$', p_clean):
            correcoes.append(Correcao("formatação", p_clean, "(linha divisória removida)"))
            continue
            
        # 2. Corrigir pontos desnecessários em negrito e ruídos
        p_clean, n1 = re.subn(r'\*\*\s*\*\*', '', p_clean)
        if n1:
            correcoes.append(Correcao("formatação", "** **", "(removido)", f"{n1}x"))
            
        p_clean, n2 = re.subn(r'\*\*\s*([.,;!?])\s*\*\*', r'\1', p_clean)
        if n2:
            correcoes.append(Correcao("formatação", "**[pontuação]**", "pontuação pura", f"{n2}x"))
            
        body_paras_cleaned.append(p_clean)

    body_text = "\n\n".join(body_paras_cleaned)

    # ── 1. Vocativos com "Você," no início de frase ──────
    padrao_voce_inicio = re.compile(r'(?:^|\n)Você, (\w)', re.MULTILINE)
    for m in padrao_voce_inicio.finditer(body_text):
        correcoes.append(Correcao("vocativo", f"Você, {m.group(1)}", m.group(1).upper(), "início de frase"))
    body_text = padrao_voce_inicio.sub(lambda m: m.group(0).replace(f"Você, {m.group(1)}", m.group(1).upper()), body_text)

    # "Você, esta não é" → "Esta não é"
    body_text, n = re.subn(r'Você, esta ', 'Esta ', body_text)
    if n: correcoes.append(Correcao("vocativo", "Você, esta", "Esta", f"{n}x"))

    # "Você, como ovelha de Cristo," → "Como ovelha de Cristo, você"
    def fix_voce_como(m):
        correcoes.append(Correcao("vocativo", m.group(0).strip(), f"Como {m.group(1)}, você"))
        return f"Como {m.group(1)}, você"
    body_text = re.sub(r'Você, como ([^,]+),', fix_voce_como, body_text)

    # ── 2. "Meu amigo" → "Querido leitor" ou remoção ────
    body_text, n = re.subn(r'(?:^|\n)Meu amigo, ', lambda m: m.group(0).replace("Meu amigo, ", "Querido leitor, "), body_text)
    if n: correcoes.append(Correcao("vocativo", "Meu amigo,", "Querido leitor,", f"{n}x"))

    body_text, n = re.subn(r', meu amigo,', ',', body_text)
    if n: correcoes.append(Correcao("vocativo", ", meu amigo,", ",", f"removido {n}x"))

    body_text, n = re.subn(r'(?<=\. )Meu amigo, ', '', body_text)
    if n: correcoes.append(Correcao("vocativo", "Meu amigo, (após ponto)", "", f"removido {n}x"))

    # ── 3. "Leitor, preste" → "Preste" ──────────────────
    body_text, n = re.subn(r'(?:^|\n)Leitor, ([Pp])reste', lambda m: m.group(0).replace(f"Leitor, {m.group(1)}reste", f"{m.group(1).upper()}reste"), body_text)
    if n: correcoes.append(Correcao("vocativo", "Leitor, preste", "Preste", f"{n}x"))

    # ── 4. Demonstrativos: "nessas palavras acima" → "nestas palavras" ──
    body_text, n = re.subn(r'nessas palavras acima', 'nestas palavras', body_text, flags=re.IGNORECASE)
    if n: correcoes.append(Correcao("demonstrativo", "nessas palavras acima", "nestas palavras", f"{n}x"))

    body_text, n = re.subn(r'nessas palavras', 'nestas palavras', body_text, flags=re.IGNORECASE)
    if n: correcoes.append(Correcao("demonstrativo", "nessas palavras", "nestas palavras", f"{n}x"))

    body_text, n = re.subn(r'nesse texto poderoso', 'neste texto poderoso', body_text, flags=re.IGNORECASE)
    if n: correcoes.append(Correcao("demonstrativo", "nesse texto poderoso", "neste texto poderoso", f"{n}x"))

    # ── 5. Perguntas de eco: "Felizes são... Você [verbo]?" ──
    padrao_eco = re.compile(r'(Felizes são aqueles que [^!]+!) Você \w+[\w\s]*\?')
    for m in padrao_eco.finditer(body_text):
        correcoes.append(Correcao("pergunta-eco", m.group(0)[-40:], m.group(1)[-40:]))
    body_text = padrao_eco.sub(r'\1', body_text)

    for eco in ["Você confia assim?", "Você encontra tal consolo?", "Você desfruta assim?",
                "Você ouve?", "Você vive?", "Você faz parte?", "Você crê?",
                "Você se entrega?", "Você busca isso?"]:
        if eco in body_text:
            body_text = body_text.replace(f" {eco}", "")
            body_text = body_text.replace(eco, "")
            correcoes.append(Correcao("pergunta-eco", eco, "(removido)"))

    # ── 6. "Venha depressa!" → remoção ───────────────────
    body_text, n = re.subn(r' ?Venha depressa[.!]?', '', body_text)
    if n: correcoes.append(Correcao("estilo", "Venha depressa!", "(removido)", f"{n}x"))

    # ── 7. Artigos antes de possessivos (casos seguros) ──
    for caso in [("Ali está seu", "Ali está o seu"), 
                 ("Ali está sua", "Ali está a sua")]:
        body_text, n = re.subn(re.escape(caso[0]), caso[1], body_text)
        if n: correcoes.append(Correcao("artigo", caso[0], caso[1], f"{n}x"))

    # ── 8. Limpeza final ─────────────────────────────────
    body_text = re.sub(r'  +', ' ', body_text)
    body_text = re.sub(r'\n{3,}', '\n\n', body_text)
    body_text = re.sub(r' +([.,;:!?])', r'\1', body_text)

    texto_final = f"{header_text}\n\n{body_text}"
    return texto_final.strip(), correcoes


# ═══════════════════════════════════════════════════════════
# Funções de Banco
# ═══════════════════════════════════════════════════════════

def buscar_semana(semana: int | None = None, dia: int | None = None) -> list[dict]:
    """Busca devocionais de uma semana (ou dia específico) do Supabase. Se semana for None, busca todas."""
    query = sb.table("plano_devocional").select("id, semana, dia_semana, texto_biblico, tema_central")
    query = query.eq("status", "aprovado")
    if semana is not None:
        query = query.eq("semana", semana)
    if dia is not None:
        query = query.eq("dia_semana", dia)
    query = query.order("semana").order("dia_semana")
    planos = query.execute().data

    # Fetch all devocionais_final in one batch
    p_ids = [p["id"] for p in planos]
    if not p_ids:
        return []
        
    devs_data = sb.table("devocionais_final").select(
        "id, plano_id, titulo, conteudo_md, palavras"
    ).in_("plano_id", p_ids).execute().data
    
    devs_by_plano = {d["plano_id"]: d for d in devs_data}

    resultado = []
    for p in planos:
        dev = devs_by_plano.get(p["id"])
        if dev:
            resultado.append({
                **p,
                "dev_id": dev["id"],
                "titulo": dev["titulo"],
                "conteudo_md": dev["conteudo_md"],
                "palavras_antes": dev["palavras"],
            })
    return resultado


def atualizar_devocional(dev_id: str, conteudo: str, palavras: int):
    """Atualiza o conteúdo revisado no Supabase."""
    sb.table("devocionais_final").update({
        "conteudo_md": conteudo,
        "palavras": palavras,
    }).eq("id", dev_id).execute()


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Revisor de Português — Devocionais Publicadas")
    parser.add_argument("--semana", "-s", type=int, default=None, help="Número da semana (1-52). Se omitido, revisa todas.")
    parser.add_argument("--dia", "-d", type=int, default=None, help="Dia específico (1-7). Se omitido, revisa toda a semana.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra correções sem salvar no banco.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostra detalhes de cada correção.")
    parser.add_argument("--log", type=str, default=None, help="Arquivo de log JSON para o relatório.")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    if args.semana is not None:
        print(f"  REVISOR DE PORTUGUÊS — Semana {args.semana}")
    else:
        print(f"  REVISOR DE PORTUGUÊS — Todas as Semanas")
    if args.dia:
        print(f"  Dia: {args.dia}")
    if args.dry_run:
        print(f"  ⚠ MODO DRY-RUN (sem salvar no banco)")
    print(f"{'='*60}\n")

    devocionais = buscar_semana(args.semana, args.dia)
    if not devocionais:
        semana_str = f"Semana {args.semana}" if args.semana is not None else "Todas as Semanas"
        print(f"❌ Nenhuma devocional encontrada para {semana_str}" + 
              (f", Dia {args.dia}" if args.dia else ""))
        sys.exit(1)

    print(f"📋 {len(devocionais)} devocional(is) encontrada(s)\n")

    relatorio = []
    total_correcoes = 0

    for dev in devocionais:
        print(f"── Sem {dev['semana']} Dia {dev['dia_semana']}: {dev['titulo']} ──")
        print(f"   Ref: {dev['texto_biblico']}")
        print(f"   Palavras (antes): {dev['palavras_antes']}")

        texto_revisado, correcoes = aplicar_correcoes(dev["conteudo_md"], dev["texto_biblico"])
        palavras_depois = len(texto_revisado.split())

        if not correcoes:
            print(f"   ✅ Sem correções necessárias\n")
            relatorio.append({
                "semana": dev["semana"],
                "dia": dev["dia_semana"],
                "titulo": dev["titulo"],
                "correcoes": 0,
                "status": "limpo",
            })
            continue

        print(f"   🔧 {len(correcoes)} correção(ões):")
        for c in correcoes:
            if args.verbose:
                print(f"      [{c.tipo}] '{c.antes}' → '{c.depois}' {c.contexto}")
            else:
                print(f"      [{c.tipo}] {c}")

        print(f"   Palavras (depois): {palavras_depois}")

        if not args.dry_run:
            atualizar_devocional(dev["dev_id"], texto_revisado, palavras_depois)
            print(f"   ✅ Atualizado no Supabase")
        else:
            print(f"   ⏭ Dry-run — não salvo")

        print()
        total_correcoes += len(correcoes)

        relatorio.append({
            "semana": dev["semana"],
            "dia": dev["dia_semana"],
            "titulo": dev["titulo"],
            "correcoes": len(correcoes),
            "palavras_antes": dev["palavras_antes"],
            "palavras_depois": palavras_depois,
            "detalhes": [repr(c) for c in correcoes],
            "status": "corrigido" if not args.dry_run else "dry-run",
        })

    # Salvar log se solicitado
    if args.log:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "semana": args.semana if args.semana is not None else "todas",
            "dia": args.dia,
            "total_devocionais": len(devocionais),
            "total_correcoes": total_correcoes,
            "dry_run": args.dry_run,
            "resultados": relatorio,
        }
        Path(args.log).write_text(json.dumps(log_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"📄 Log salvo em: {args.log}")

    print(f"\n{'='*60}")
    print(f"  RESUMO: {total_correcoes} correção(ões) em {len(devocionais)} devocional(is)")
    if args.dry_run:
        print(f"  ⚠ Nada foi salvo (dry-run). Rode sem --dry-run para aplicar.")
    else:
        print(f"  ✅ Todas as correções aplicadas no Supabase.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
