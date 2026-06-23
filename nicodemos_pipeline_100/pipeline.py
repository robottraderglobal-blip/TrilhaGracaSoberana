"""
Nicodemos Pipeline 100 — CLI Principal
Uso: python -m nicodemos_pipeline_100.pipeline [comando]
"""
import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# ── Logging estruturado ──────────────────────────────────
LOG_DIR = Path(__file__).parent.parent
_log_file = LOG_DIR / "nicodemos_pipeline.log"
_handler = RotatingFileHandler(_log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))
_logger = logging.getLogger("nicodemos_pipeline")
_logger.setLevel(logging.INFO)
_logger.addHandler(_handler)

app = typer.Typer(
    name="nicodemos",
    help="📖 Pipeline Automatizado de Devocionais — Estilo Augustus Nicodemus (100 dias de Culto Doméstico)",
    no_args_is_help=True,
)
console = Console()


@app.command()
def seed():
    """🌱 Popular o banco com as 100 entradas do plano de culto doméstico."""
    from .db.seed_data import get_all_entries
    from .db.client import seed_plano

    entries = get_all_entries()
    console.print(f"\n📋 Total de entradas preparadas: [bold]{len(entries)}[/bold]")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task("Inserindo no Supabase...", total=None)
        count = seed_plano(entries)

    console.print(f"✅ [green]{count} entradas[/green] inseridas/atualizadas com sucesso!\n")


@app.command()
def seed_expansao():
    """🌱 Popular o banco com os 50 versículos da expansão bíblica (dias 101-150)."""
    from . import config
    from .db.client import seed_plano
    from .utils import get_verse_or_fallback
    import json

    plano_path = config.PLANO_EXPANSAO_JSON
    if not plano_path.exists():
        console.print(f"[red]❌ Arquivo não encontrado: {plano_path}[/red]")
        raise typer.Exit(1)

    plano_raw = json.loads(plano_path.read_text(encoding="utf-8"))
    entries = []

    for week_data in plano_raw:
        semana = week_data["week"]
        for day_data in week_data["days"]:
            dia = day_data["day"]
            dia_semana = ((dia - 1) % 7) + 1
            ref = day_data["ref"]
            versiculo = get_verse_or_fallback(ref, day_data["t"])

            entries.append({
                "semana": semana,
                "dia": dia,
                "dia_semana": dia_semana,
                "ref": ref,
                "versiculo": versiculo,
                "status": "pending",
            })

    console.print(f"\n📋 Total de entradas da expansão: [bold]{len(entries)}[/bold]")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task("Inserindo expansão no Supabase...", total=None)
        count = seed_plano(entries)

    console.print(f"✅ [green]{count} entradas[/green] inseridas/atualizadas com sucesso!\n")

@app.command()
def status():
    """📊 Exibir status geral do pipeline."""
    from .db.client import contar_por_status

    contagem = contar_por_status()
    total = sum(contagem.values())

    table = Table(title="📊 Status — Nicodemos Pipeline 100")
    table.add_column("Status", style="bold")
    table.add_column("Quantidade", justify="right")
    table.add_column("Porcentagem", justify="right")

    for s, c in sorted(contagem.items()):
        pct = f"{c / total * 100:.1f}%" if total else "0%"
        color = "green" if s == "aprovado" else "yellow" if "andamento" in s else "dim"
        table.add_row(f"[{color}]{s}[/{color}]", str(c), pct)

    table.add_row("[bold]TOTAL[/bold]", f"[bold]{total}[/bold]", "100%")
    console.print(table)


@app.command()
def executar(
    dia: int = typer.Option(..., "--dia", "-d", help="Número do dia (1-100)"),
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reprocessamento"),
):
    """🚀 Executar pipeline completo para um dia específico."""
    from . import config
    from .db import client as db
    from .agents.escritor import AgenteEscritor
    from .agents.revisor import AgenteRevisor

    logger = logging.getLogger("nicodemos_pipeline")
    logger.info(f"=== Iniciando Dia {dia} ===")

    config.validate_config()

    # 1. Buscar plano
    console.print(f"\n🔎 Buscando Dia {dia}...")
    plano = db.get_plano_by_dia(dia)
    if not plano:
        console.print(f"[red]❌ Dia {dia} não encontrado. Execute 'seed' primeiro.[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        f"📖 [bold]{plano['ref']}[/bold]\n"
        f"📜 {plano['versiculo'][:100]}...\n"
        f"📅 Semana {plano['semana']}, Dia {plano['dia']}",
        title=f"Devocional — Dia {dia}",
    ))

    if plano["status"] == "aprovado" and not force:
        console.print("[yellow]⚠ Este dia já foi aprovado. Use --force para reprocessar.[/yellow]")
        raise typer.Exit(0)

    if force:
        db.limpar_dados_dia(plano["id"])
        db.atualizar_status(plano["id"], "pending")

    # 2. ESCRITOR
    console.print("\n[bold cyan]✍️  ETAPA 1: Agente Escritor (Augustus Nicodemos)[/bold cyan]")
    db.atualizar_status(plano["id"], "escrita_em_andamento")

    with console.status("Escrevendo devocional no estilo Augustus Nicodemos..."):
        escritor = AgenteEscritor()
        trabalho = escritor.escrever(plano)

    trabalho_db = db.salvar_rascunho(trabalho.to_db_dict())
    trabalho.id = trabalho_db["id"]
    db.atualizar_status(plano["id"], "escrita_concluida")

    console.print(f"   📝 Rascunho v{trabalho.versao}: {trabalho.palavras} palavras")

    # 3. REVISOR (até 2 ciclos)
    console.print("\n[bold cyan]🔍 ETAPA 2: Agente Revisor[/bold cyan]")
    db.atualizar_status(plano["id"], "revisao_em_andamento")

    revisor = AgenteRevisor()
    aprovado = False
    revisao = None

    for ciclo in range(1, config.MAX_CICLOS_REVISAO + 1):
        console.print(f"\n   [bold]Ciclo {ciclo}/{config.MAX_CICLOS_REVISAO}[/bold]")

        with console.status(f"Avaliando rascunho v{trabalho.versao}..."):
            revisao = revisor.avaliar(trabalho, plano, ciclo)

        revisao_db = db.salvar_revisao(revisao.to_db_dict())

        # Mostrar scores
        score_table = Table(show_header=False, box=None, padding=(0, 2))
        score_table.add_row("Conf. Estrutural (20%)", f"{revisao.conformidade_estrutural}/100")
        score_table.add_row("Estilo Nicodemos (25%)", f"{revisao.estilo_nicodemos}/100")
        score_table.add_row("Conf. Teológica (25%)", f"{revisao.conformidade_teologica}/100")
        score_table.add_row("Qual. Literária (15%)", f"{revisao.qualidade_literaria}/100")
        score_table.add_row("Extensão (15%)", f"{revisao.extensao_adequada}/100")
        score_table.add_row("[bold]TOTAL[/bold]", f"[bold]{revisao.score_total:.1f}[/bold]/100")
        console.print(score_table)

        if revisao.aprovado:
            console.print(f"   ✅ [green]APROVADO[/green] (score: {revisao.score_total:.1f})")
            aprovado = True

            # Usar texto corrigido pelo revisor se disponível
            texto_final = revisor.extrair_texto_final(revisao, trabalho.conteudo_md)
            if texto_final != trabalho.conteudo_md:
                console.print("   📝 Usando texto com correções inline do revisor")
                trabalho.conteudo_md = texto_final
                trabalho.palavras = trabalho.contar_palavras()

            break
        else:
            console.print(f"   ❌ [red]REPROVADO[/red] (score: {revisao.score_total:.1f})")
            console.print(f"   📋 Problemas: {revisao.problemas_encontrados[:200]}...")

            if ciclo < config.MAX_CICLOS_REVISAO:
                console.print(f"\n   🔄 Reescrevendo com feedback...")
                with console.status("Reescrevendo devocional..."):
                    trabalho = escritor.reescrever(trabalho, revisao.sugestoes_reescrita, plano)
                trabalho_db = db.salvar_rascunho(trabalho.to_db_dict())
                trabalho.id = trabalho_db["id"]
                console.print(f"   📝 Rascunho v{trabalho.versao}: {trabalho.palavras} palavras")

    if not aprovado:
        console.print("\n[yellow]⚠ Máximo de ciclos atingido. Salvando última versão.[/yellow]")

    # 4. SALVAR FINAL
    console.print("\n[bold cyan]💾 ETAPA 3: Salvando versão final[/bold cyan]")
    from .models.devocional import DevocionalFinal

    # Garantir cabeçalhos limpos (sem emojis/parênteses) e hino correto
    trabalho.conteudo_md = _limpar_cabecalhos(trabalho.conteudo_md)
    trabalho.conteudo_md = _assegurar_hino_correto(trabalho.conteudo_md, plano["dia"])

    # Extrair pergunta de reflexão do texto e remover do markdown
    pergunta, conteudo_limpo = _extrair_pergunta_e_limpar_markdown(trabalho.conteudo_md)

    try:
        final = DevocionalFinal(
            plano_id=plano["id"],
            ref=plano["ref"],
            versiculo=plano["versiculo"],
            conteudo_md=conteudo_limpo,
            pergunta_reflexao=pergunta,
            palavras=trabalho.palavras,
            semana=plano["semana"],
            dia=plano["dia"],
            escritor_trabalho_id=trabalho.id,
            revisao_final_id=revisao_db["id"] if revisao else "",
            versao_aprovada=trabalho.versao,
            score_final=float(revisao.score_total) if revisao else 0.0,
        )

        final_db = db.salvar_devocional_final(final.to_db_dict())
        db.atualizar_status(plano["id"], "aprovado")
        logger.info(f"Dia {dia} APROVADO score={revisao.score_total:.1f} v={trabalho.versao} palavras={trabalho.palavras}")
        console.print(f"   ✅ Devocional final salva: {final_db['id']}")
    except Exception as e:
        import traceback
        logger.error(f"Erro ao salvar final: {traceback.format_exc()}")
        console.print(f"[red]❌ Erro ao salvar: {e}[/red]")
        raise

    # Resumo final
    score_str = f"{revisao.score_total:.1f}" if revisao else "0"
    panel_content = (
        f"📖 [bold]{plano['ref']}[/bold]\n"
        f"📊 Score: {score_str}/100 (v{trabalho.versao})\n"
        f"📐 {trabalho.palavras} palavras"
    )

    if pergunta:
        panel_content += f"\n❓ {pergunta[:80]}..."

    console.print(Panel(
        panel_content,
        title="✅ Pipeline Completo",
        border_style="green",
    ))


@app.command()
def executar_semana(
    semana: int = typer.Option(..., "--semana", "-s", help="Número da semana (1-15)"),
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reprocessamento de todos os dias da semana"),
):
    """🚀 Executar pipeline para todos os dias de uma semana."""
    from .db.client import get_plano_by_semana
    from .db import client as db

    dias = get_plano_by_semana(semana)
    if not dias:
        console.print(f"[red]❌ Semana {semana} não encontrada.[/red]")
        raise typer.Exit(1)

    console.print(f"\n📅 Executando Semana {semana}: {len(dias)} dias\n")

    SKIP_STATES = set() if force else {"aprovado"}
    STUCK_STATES = {"escrita_em_andamento", "escrita_concluida", "revisao_em_andamento"}

    logger = logging.getLogger("nicodemos_pipeline")

    for dia_data in dias:
        if dia_data["status"] in SKIP_STATES:
            console.print(f"   ⏭ Dia {dia_data['dia']} — já {dia_data['status']}")
            continue

        if force or dia_data["status"] in STUCK_STATES:
            console.print(f"   🔄 Dia {dia_data['dia']} — limpando dados anteriores e iniciando...")
            db.limpar_dados_dia(dia_data["id"])
            db.atualizar_status(dia_data["id"], "pending")

        console.rule(f"Dia {dia_data['dia']} — {dia_data['ref']}")
        try:
            executar(dia=dia_data["dia"], force=force)
        except SystemExit:
            pass
        except Exception as e:
            error_msg = str(e)[:500]
            console.print(f"   [red]❌ Erro: {error_msg}[/red]")
            logger.error(f"Dia {dia_data['dia']} falhou: {error_msg}")
            try:
                db.atualizar_status(dia_data["id"], "erro")
            except Exception:
                pass
            continue



@app.command()
def validar():
    """🔍 Validar configuração do pipeline."""
    from . import config

    console.print("\n🔧 [bold]Validação — Nicodemos Pipeline 100[/bold]\n")

    checks = [
        ("Supabase URL", bool(config.SUPABASE_URL)),
        ("Supabase Key", bool(config.SUPABASE_ANON_KEY)),
        ("LLM Provider", config.LLM_PROVIDER),
        ("Modelo", config.get_llm_model()),
        ("Palavras Min", config.PALAVRAS_MIN),
        ("Palavras Max", config.PALAVRAS_MAX),
        ("Max Ciclos Revisão", config.MAX_CICLOS_REVISAO),
        ("Plano JSON", config.PLANO_JSON.exists()),
    ]

    if config.LLM_PROVIDER == "gemini":
        checks.append(("Gemini API Key", bool(config.GEMINI_API_KEY)))
    elif config.LLM_PROVIDER == "openai":
        checks.append(("OpenAI API Key", bool(config.OPENAI_API_KEY)))
    elif config.LLM_PROVIDER == "anthropic":
        checks.append(("Anthropic API Key", bool(config.ANTHROPIC_API_KEY)))
    elif config.LLM_PROVIDER == "openrouter":
        checks.append(("OpenRouter API Key", bool(config.OPENROUTER_API_KEY)))

    for label, value in checks:
        if isinstance(value, bool):
            icon = "✅" if value else "❌"
            console.print(f"   {icon} {label}: {'OK' if value else 'NÃO CONFIGURADO'}")
        else:
            console.print(f"   ✅ {label}: {value}")

    console.print()

    try:
        config.validate_config()
        console.print("[green]✅ Configuração válida![/green]\n")
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]\n")


def _limpar_cabecalhos(conteudo_md: str) -> str:
    """Remove emojis e textos entre parênteses dos cabeçalhos de seção."""
    # Remove emojis comuns dos cabeçalhos ### N.
    conteudo_md = re.sub(
        r'(###\s*\d+\.)\s*[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]+\s*',
        r'\1 ',
        conteudo_md,
    )
    # Remove textos entre parênteses nos cabeçalhos (ex: "(Breve Explicação)")
    conteudo_md = re.sub(
        r'(###\s*\d+\.\s*[^(\n]+?)\s*\([^)]*\)\s*$',
        r'\1',
        conteudo_md,
        flags=re.MULTILINE,
    )
    return conteudo_md


def _assegurar_hino_correto(conteudo_md: str, dia: int) -> str:
    """Garante que a seção 7 da devocional contém as letras oficiais exatas e o hino correto.
    
    Lê a ordem de hinos do hinos_usuario.json e busca a letra e formatação
    de forma estruturada a partir das letras do hinário Novo Cântico.
    """
    import json
    from pathlib import Path
    
    # 1. Carregar hinos do usuário
    utils_dir = Path(__file__).parent / "utils"
    hinos_path = utils_dir / "hinos_usuario.json"
    letras_path = utils_dir / "novo_cantico_letras.json"
    formatted_path = utils_dir / "novo_cantico_formatado.json"
    
    hymn_key = str(dia)
    if hinos_path.exists():
        try:
            with open(hinos_path, "r", encoding="utf-8") as f:
                hinos = json.load(f)
                if dia <= len(hinos):
                    hymn_key = hinos[dia - 1]
        except Exception:
            pass
            
    # 2. Obter letra e título do hino
    letra_crua = ""
    hymn_title = f"Hino {hymn_key}"
    
    if letras_path.exists():
        try:
            with open(letras_path, "r", encoding="utf-8") as f:
                letras_data = json.load(f)
                
            if hymn_key == "110-a" and "110" in letras_data:
                partes = letras_data["110"].split("110-A")
                letra_crua = partes[1].strip()
                hymn_title = "110-A - Crer e observar"
            elif hymn_key == "110" and "110" in letras_data:
                partes = letras_data["110"].split("110-A")
                letra_crua = partes[0].replace("110 - A vida com Jesus", "").strip()
                hymn_title = "110 - A vida com Jesus"
            elif hymn_key in letras_data:
                raw_text = letras_data[hymn_key]
                linhas = raw_text.splitlines()
                hymn_title = linhas[0].strip()
                letra_crua = "\n".join(linhas[1:]).strip()
        except Exception:
            pass
            
    # 3. Obter a versão formatada
    lyrics_formatted = ""
    hymn_title_display = hymn_title
    
    # Tentar pegar pré-formatado
    simplified_key = hymn_key.replace("-", "")
    if formatted_path.exists():
        try:
            with open(formatted_path, "r", encoding="utf-8") as f:
                formatted_data = json.load(f)
            if simplified_key in formatted_data:
                lyrics_formatted = formatted_data[simplified_key]["formatado"]
                hymn_title_display = formatted_data[simplified_key]["titulo"]
        except Exception:
            pass
            
    # Se não estiver no pré-formatado, chamar o AgenteFormatadorHino
    if not lyrics_formatted and letra_crua:
        try:
            from .agents.hymn_formatter import AgenteFormatadorHino
            formatter = AgenteFormatadorHino()
            lyrics_formatted = formatter.formatar(hymn_title, letra_crua)
        except Exception:
            lyrics_formatted = letra_crua
            
    if not lyrics_formatted:
        lyrics_formatted = letra_crua
        
    header_match = re.search(r'###\s*7\..*?Melodia no Lar[^\n]*\n', conteudo_md, re.IGNORECASE)
    if header_match:
        index = header_match.start()
        conteudo_antes = conteudo_md[:index]
        section_7 = f"### 7. Melodia no Lar\n\n[{hymn_title_display}]\n\n{lyrics_formatted}\n"
        return conteudo_antes.strip() + "\n\n" + section_7
    else:
        section_7 = f"\n\n### 7. Melodia no Lar\n\n[{hymn_title_display}]\n\n{lyrics_formatted}\n"
        return conteudo_md.strip() + section_7


def _extrair_pergunta_e_limpar_markdown(texto: str) -> tuple[str, str]:
    """Extrai a pergunta de reflexão e a remove do markdown da devocional."""
    # Buscar padrão "**Pergunta para reflexão:**" ou "**Pergunta:**"
    match = re.search(
        r'(?:\n\s*)*\*\*Pergunta[^:]*:\*\*\s*(.+?)(?:\n\n|\Z)',
        texto,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        pergunta = match.group(1).strip()
        # Limpar formatação markdown da pergunta isolada
        pergunta = pergunta.strip('*_ ')
        # Retirar esse bloco inteiro do markdown principal
        texto_limpo = texto.replace(match.group(0), '').strip()
        return pergunta, texto_limpo
    return "", texto.strip()


if __name__ == "__main__":
    app()
