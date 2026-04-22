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


def aplicar_correcoes(texto: str) -> tuple[str, list[Correcao]]:
    """Aplica todas as regras de correção ao texto. Retorna (texto_corrigido, lista_de_correções)."""
    correcoes: list[Correcao] = []
    original = texto

    # ── 1. Vocativos com "Você," no início de frase ──────
    # "Você, preste atenção..." → "Preste atenção..."
    padrao_voce_inicio = re.compile(r'(?:^|\n)Você, (\w)', re.MULTILINE)
    for m in padrao_voce_inicio.finditer(texto):
        correcoes.append(Correcao("vocativo", f"Você, {m.group(1)}", m.group(1).upper(), "início de frase"))
    texto = padrao_voce_inicio.sub(lambda m: m.group(0).replace(f"Você, {m.group(1)}", m.group(1).upper()), texto)

    # "Você, esta não é" → "Esta não é"
    texto, n = re.subn(r'Você, esta ', 'Esta ', texto)
    if n: correcoes.append(Correcao("vocativo", "Você, esta", "Esta", f"{n}x"))

    # "Você, como ovelha de Cristo," → "Como ovelha de Cristo, você"
    def fix_voce_como(m):
        correcoes.append(Correcao("vocativo", m.group(0).strip(), f"Como {m.group(1)}, você"))
        return f"Como {m.group(1)}, você"
    texto = re.sub(r'Você, como ([^,]+),', fix_voce_como, texto)

    # ── 2. "Meu amigo" → "Querido leitor" ou remoção ────
    # "Meu amigo," no início de parágrafo
    texto, n = re.subn(r'(?:^|\n)Meu amigo, ', lambda m: m.group(0).replace("Meu amigo, ", "Querido leitor, "), texto)
    if n: correcoes.append(Correcao("vocativo", "Meu amigo,", "Querido leitor,", f"{n}x"))

    # "meu amigo" no meio de frase (entre pontuação)
    texto, n = re.subn(r', meu amigo,', ',', texto)
    if n: correcoes.append(Correcao("vocativo", ", meu amigo,", ",", f"removido {n}x"))

    # "meu amigo" após ponto
    texto, n = re.subn(r'(?<=\. )Meu amigo, ', '', texto)
    if n: correcoes.append(Correcao("vocativo", "Meu amigo, (após ponto)", "", f"removido {n}x"))

    # ── 3. "Leitor, preste" → "Preste" ──────────────────
    texto, n = re.subn(r'(?:^|\n)Leitor, ([Pp])reste', lambda m: m.group(0).replace(f"Leitor, {m.group(1)}reste", f"{m.group(1).upper()}reste"), texto)
    if n: correcoes.append(Correcao("vocativo", "Leitor, preste", "Preste", f"{n}x"))

    # ── 4. Demonstrativos: "nessas palavras acima" → "nestas palavras" ──
    texto, n = re.subn(r'nessas palavras acima', 'nestas palavras', texto, flags=re.IGNORECASE)
    if n: correcoes.append(Correcao("demonstrativo", "nessas palavras acima", "nestas palavras", f"{n}x"))

    texto, n = re.subn(r'nessas palavras', 'nestas palavras', texto, flags=re.IGNORECASE)
    if n: correcoes.append(Correcao("demonstrativo", "nessas palavras", "nestas palavras", f"{n}x"))

    # "nesse texto" quando se refere ao texto corrente
    texto, n = re.subn(r'nesse texto poderoso', 'neste texto poderoso', texto, flags=re.IGNORECASE)
    if n: correcoes.append(Correcao("demonstrativo", "nesse texto poderoso", "neste texto poderoso", f"{n}x"))

    # ── 5. Perguntas de eco: "Felizes são... Você [verbo]?" ──
    padrao_eco = re.compile(r'(Felizes são aqueles que [^!]+!) Você \w+[\w\s]*\?')
    for m in padrao_eco.finditer(texto):
        correcoes.append(Correcao("pergunta-eco", m.group(0)[-40:], m.group(1)[-40:]))
    texto = padrao_eco.sub(r'\1', texto)

    # "Você confia assim?" / "Você encontra tal consolo?" / "Você desfruta assim?"
    for eco in ["Você confia assim?", "Você encontra tal consolo?", "Você desfruta assim?",
                "Você ouve?", "Você vive?", "Você faz parte?", "Você crê?",
                "Você se entrega?", "Você busca isso?"]:
        if eco in texto:
            texto = texto.replace(f" {eco}", "")
            texto = texto.replace(eco, "")
            correcoes.append(Correcao("pergunta-eco", eco, "(removido)"))

    # ── 6. "Venha depressa!" → remoção ───────────────────
    texto, n = re.subn(r' ?Venha depressa[.!]?', '', texto)
    if n: correcoes.append(Correcao("estilo", "Venha depressa!", "(removido)", f"{n}x"))

    # ── 7. Artigos antes de possessivos (casos seguros) ──
    # "Ali está seu refúgio" → "Ali está o seu refúgio"
    for caso in [("Ali está seu", "Ali está o seu"), 
                 ("Ali está sua", "Ali está a sua")]:
        texto, n = re.subn(re.escape(caso[0]), caso[1], texto)
        if n: correcoes.append(Correcao("artigo", caso[0], caso[1], f"{n}x"))

    # ── 8. Limpeza final ─────────────────────────────────
    # Espaços duplos
    texto = re.sub(r'  +', ' ', texto)
    # Linhas em branco consecutivas (mais de 2)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    # Espaço antes de pontuação
    texto = re.sub(r' +([.,;:!?])', r'\1', texto)

    return texto.strip(), correcoes


# ═══════════════════════════════════════════════════════════
# Funções de Banco
# ═══════════════════════════════════════════════════════════

def buscar_semana(semana: int, dia: int | None = None) -> list[dict]:
    """Busca devocionais de uma semana (ou dia específico) do Supabase."""
    query = sb.table("plano_devocional").select("id, semana, dia_semana, texto_biblico, tema_central")
    query = query.eq("semana", semana).eq("status", "aprovado").order("dia_semana")
    if dia:
        query = query.eq("dia_semana", dia)
    planos = query.execute().data

    resultado = []
    for p in planos:
        dev = sb.table("devocionais_final").select(
            "id, titulo, conteudo_md, palavras"
        ).eq("plano_id", p["id"]).execute().data

        if dev:
            resultado.append({
                **p,
                "dev_id": dev[0]["id"],
                "titulo": dev[0]["titulo"],
                "conteudo_md": dev[0]["conteudo_md"],
                "palavras_antes": dev[0]["palavras"],
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
    parser.add_argument("--semana", "-s", type=int, required=True, help="Número da semana (1-52)")
    parser.add_argument("--dia", "-d", type=int, default=None, help="Dia específico (1-7). Se omitido, revisa toda a semana.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra correções sem salvar no banco.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostra detalhes de cada correção.")
    parser.add_argument("--log", type=str, default=None, help="Arquivo de log JSON para o relatório.")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  REVISOR DE PORTUGUÊS — Semana {args.semana}")
    if args.dia:
        print(f"  Dia: {args.dia}")
    if args.dry_run:
        print(f"  ⚠ MODO DRY-RUN (sem salvar no banco)")
    print(f"{'='*60}\n")

    devocionais = buscar_semana(args.semana, args.dia)
    if not devocionais:
        print(f"❌ Nenhuma devocional encontrada para Semana {args.semana}" + 
              (f", Dia {args.dia}" if args.dia else ""))
        sys.exit(1)

    print(f"📋 {len(devocionais)} devocional(is) encontrada(s)\n")

    relatorio = []
    total_correcoes = 0

    for dev in devocionais:
        print(f"── Dia {dev['dia_semana']}: {dev['titulo']} ──")
        print(f"   Ref: {dev['texto_biblico']}")
        print(f"   Palavras (antes): {dev['palavras_antes']}")

        texto_revisado, correcoes = aplicar_correcoes(dev["conteudo_md"])
        palavras_depois = len(texto_revisado.split())

        if not correcoes:
            print(f"   ✅ Sem correções necessárias\n")
            relatorio.append({
                "semana": args.semana,
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
            "semana": args.semana,
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
            "semana": args.semana,
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
