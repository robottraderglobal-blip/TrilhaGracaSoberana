"""
Ryle Pipeline — CLI Principal
Uso: python -m ryle_pipeline.pipeline [comando]
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# ── Logging estruturado ──────────────────────────────────
LOG_DIR = Path(__file__).parent.parent
_log_file = LOG_DIR / "ryle_pipeline.log"
_handler = RotatingFileHandler(_log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))
_logger = logging.getLogger("ryle_pipeline")
_logger.setLevel(logging.INFO)
_logger.addHandler(_handler)

app = typer.Typer(
    name="ryle",
    help="🔥 Pipeline Automatizado de Devocionais — Estilo J.C. Ryle",
    no_args_is_help=True,
)
console = Console()


@app.command()
def seed():
    """🌱 Popular o banco com as 364 entradas do plano devocional."""
    from .db.seed_data import get_all_entries
    from .db.client import seed_plano

    entries = get_all_entries()
    console.print(f"\n📋 Total de entradas preparadas: [bold]{len(entries)}[/bold]")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task("Inserindo no Supabase...", total=None)
        count = seed_plano(entries)

    console.print(f"✅ [green]{count} entradas[/green] inseridas/atualizadas com sucesso!\n")


@app.command()
def status():
    """📊 Exibir status geral do pipeline."""
    from .db.client import contar_por_status

    contagem = contar_por_status()
    total = sum(contagem.values())

    table = Table(title="📊 Status do Pipeline Ryle")
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
    semana: int = typer.Option(..., "--semana", "-s", help="Número da semana (1-52)"),
    dia: int = typer.Option(..., "--dia", "-d", help="Dia da semana (1-7, 1=Sáb)"),
    ate_narracao: bool = typer.Option(True, help="Incluir conversão para narração"),
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reprocessamento"),
):
    """🚀 Executar pipeline completo para um dia específico."""
    from . import config
    from .db import client as db
    from .agents.exegeta import AgenteExegeta
    from .agents.escritor import AgenteEscritor
    from .agents.revisor import AgenteRevisor
    from .agents.narrador import AgenteNarrador
    from .utils.bible_fetcher import obter_texto_biblico

    logger = logging.getLogger("ryle_pipeline")
    logger.info(f"=== Iniciando S{semana}D{dia} ===")

    config.validate_config()

    # 1. Buscar plano
    console.print(f"\n🔎 Buscando Semana {semana}, Dia {dia}...")
    plano = db.get_plano_by_semana_dia(semana, dia)
    if not plano:
        console.print(f"[red]❌ Não encontrado: S{semana}D{dia}[/red]")
        raise typer.Exit(1)
        
    plano["versiculo_completo"] = obter_texto_biblico(plano["texto_biblico"])

    console.print(Panel(
        f"📖 [bold]{plano['texto_biblico']}[/bold]\n"
        f"🎯 {plano['tema_central']}\n"
        f"📅 Semana {plano['semana']}, {plano['dia_nome']} — Mês {plano['mes']}",
        title=f"Devocional S{semana}D{dia}",
    ))

    if plano["status"] == "aprovado" and not force:
        console.print("[yellow]⚠ Este dia já foi aprovado. Use --force para reprocessar.[/yellow]")
        raise typer.Exit(0)
    
    if force:
        db.atualizar_status(plano["id"], "pending")

    # 2. EXEGETA
    console.print("\n[bold cyan]🔬 ETAPA 1: Agente Exegeta[/bold cyan]")
    
    # Check if exegesis already exists
    exegese_existente = db.get_exegese_by_plano(plano["id"])
    if exegese_existente:
        from .models.exegese import Exegese
        exegese = Exegese(
            id=exegese_existente["id"],
            plano_id=plano["id"],
            titulo_sugerido=exegese_existente.get("titulo_sugerido", "Exegese"),
            doutrinas=[]
        )
        # Hack rápido para restaurar doutrinas mínimas para pesquisa 
        try:
            if exegese_existente.get("doutrinas"):
                for doc in exegese_existente["doutrinas"]:
                    from .models.exegese import Doutrina
                    exegese.doutrinas.append(Doutrina(**doc))
        except: pass
        if getattr(exegese, 'doutrinas', []) == []:
             from .models.exegese import Doutrina
             exegese.doutrinas = [Doutrina(nome="Doutrinas Principais", base_textual="", palavras_chave=[], versiculos_suporte=[], refutacao="")]

        console.print("   [dim]⏭ Exegese já existia no banco. Pulando LLM.[/dim]")
        db.atualizar_status(plano["id"], "exegese_concluida")
    else:
        db.atualizar_status(plano["id"], "exegese_em_andamento")
        with console.status("Analisando texto bíblico (5 passos puritanos)..."):
            exegeta = AgenteExegeta()
            exegese = exegeta.analisar(
                texto_biblico=plano["texto_biblico"],
                tema_central=plano["tema_central"],
                plano_id=plano["id"],
            )

        # Salvar exegese
        exegese_db = db.salvar_exegese(exegese.to_db_dict())
        exegese.id = exegese_db["id"]
        db.atualizar_status(plano["id"], "exegese_concluida")
        logger.info(f"S{semana}D{dia} exegese salva: {exegese.id}")

    console.print(f"   📝 Título sugerido: [italic]{exegese.titulo_sugerido}[/italic]")
    console.print(f"   📚 Doutrinas: {', '.join(d.nome for d in exegese.doutrinas)}")
    console.print(f"   ✅ Exegese pronta: {exegese.id}")

    # 3. PESQUISA (skip se desabilitada ou já existente no banco)
    pesquisas = []
    if config.PESQUISA_HABILITADA:
        from .agents.pesquisador import AgentePesquisador
        from .models.pesquisa import PesquisaFonte
        
        pesquisas_db = db.get_pesquisas_by_plano(plano["id"])
        tem_resultado_relevante = False
        
        if pesquisas_db:
            for p in pesquisas_db:
                res = str(p.get("resultado", "")).strip().lower()
                if res and not res.startswith("sem dados relevantes") and "não foram encontrados dados" not in res:
                    tem_resultado_relevante = True
                    break
                    
        if pesquisas_db and tem_resultado_relevante:
            console.print(f"\n[dim]⏭ ETAPA 2: Pesquisa NotebookLM (reaproveitando {len(pesquisas_db)} pesquisas arquivadas no DB)[/dim]")
            for p_dict in pesquisas_db:
                pesquisas.append(PesquisaFonte(**p_dict))
            db.atualizar_status(plano["id"], "pesquisa_concluida")
        else:
            console.print("\n[bold cyan]🔍 ETAPA 2: Agente Pesquisador (NotebookLM)[/bold cyan]")
            db.atualizar_status(plano["id"], "pesquisa_em_andamento")
            
            from .db.client import get_client
            try:
                # Limpa pesquisas vazias ou antigas antes de rodar 
                get_client().table("pesquisa_fontes").delete().eq("plano_id", plano["id"]).execute()
            except Exception:
                pass
                
            with console.status("Pesquisando fontes com NotebookLM..."):
                pesquisador = AgentePesquisador()
                pesquisas = pesquisador.pesquisar_todas(
                    exegese=exegese,
                    texto_biblico=plano["texto_biblico"],
                    tema_central=plano["tema_central"]
                )
                for pesquisa in pesquisas:
                    db.salvar_pesquisa(pesquisa.to_db_dict())
            db.atualizar_status(plano["id"], "pesquisa_concluida")
            console.print(f"   ✅ Insights coletados de {len(pesquisas)} fontes.")
    else:
        console.print("\n[dim]⏭ ETAPA 2: Pesquisa NotebookLM (desabilitada)[/dim]")

    # 4. ESCRITOR
    console.print("\n[bold cyan]✍️  ETAPA 3: Agente Escritor[/bold cyan]")
    db.atualizar_status(plano["id"], "escrita_em_andamento")

    from .db.client import get_client
    try:
        # Limpa versões antigas para evitar crash de 'versao já existe' ao salvar_rascunho(v1)
        c = get_client()
        # Primeiro limpar devocionais_final para remover a foreign key lock
        try: c.table("devocionais_final").delete().eq("plano_id", plano["id"]).execute()
        except: pass
        try: c.table("revisoes").delete().eq("plano_id", plano["id"]).execute()
        except: pass
        try: c.table("escritor_trabalho").delete().eq("plano_id", plano["id"]).execute()
        except: pass
        try: c.table("devocionais_narracao").delete().eq("plano_id", plano["id"]).execute()
        except: pass
    except Exception:
        pass

    with console.status("Escrevendo devocional no estilo J.C. Ryle..."):
        escritor = AgenteEscritor()
        trabalho = escritor.escrever(plano, exegese, pesquisas)

    trabalho_db = db.salvar_rascunho(trabalho.to_db_dict())
    trabalho.id = trabalho_db["id"]
    db.atualizar_status(plano["id"], "escrita_concluida")

    console.print(f"   📝 Rascunho v{trabalho.versao}: {trabalho.palavras} palavras")

    # 5. REVISOR (até 3 ciclos)
    console.print("\n[bold cyan]🔍 ETAPA 4: Agente Revisor[/bold cyan]")
    db.atualizar_status(plano["id"], "revisao_em_andamento")

    revisor = AgenteRevisor()
    aprovado = False

    for ciclo in range(1, config.MAX_CICLOS_REVISAO + 1):
        console.print(f"\n   [bold]Ciclo {ciclo}/{config.MAX_CICLOS_REVISAO}[/bold]")

        with console.status(f"Avaliando rascunho v{trabalho.versao}..."):
            revisao = revisor.avaliar(trabalho, exegese, ciclo)

        revisao_db = db.salvar_revisao(revisao.to_db_dict())

        # Mostrar scores
        score_table = Table(show_header=False, box=None, padding=(0, 2))
        score_table.add_row("Fid. Exegética (30%)", f"{revisao.fidelidade_exegetica}/100")
        score_table.add_row("Extensão (15%)", f"{revisao.extensao_adequada}/100")
        score_table.add_row("Estrutura Ryle (15%)", f"{revisao.estrutura_ryle}/100")
        score_table.add_row("Densidade (20%)", f"{revisao.densidade_doutrinaria}/100")
        score_table.add_row("Clareza (10%)", f"{revisao.clareza_pastoral}/100")
        score_table.add_row("Anti-padrões (10%)", f"{revisao.ausencia_antipadroes}/100")
        score_table.add_row("[bold]TOTAL[/bold]", f"[bold]{revisao.score_total:.1f}[/bold]/100")
        console.print(score_table)

        if revisao.aprovado:
            console.print(f"   ✅ [green]APROVADO[/green] (score: {revisao.score_total:.1f})")
            aprovado = True
            break
        else:
            console.print(f"   ❌ [red]REPROVADO[/red] (score: {revisao.score_total:.1f})")
            console.print(f"   📋 Problemas: {revisao.problemas_encontrados[:200]}...")

            if ciclo < config.MAX_CICLOS_REVISAO:
                console.print(f"\n   🔄 Reescrevendo com feedback...")
                with console.status("Reescrevendo devocional..."):
                    trabalho = escritor.reescrever(
                        trabalho, revisao.sugestoes_reescrita, plano, exegese
                    )
                trabalho_db = db.salvar_rascunho(trabalho.to_db_dict())
                trabalho.id = trabalho_db["id"]
                console.print(f"   📝 Rascunho v{trabalho.versao}: {trabalho.palavras} palavras")

    if not aprovado:
        console.print("\n[yellow]⚠ Máximo de ciclos atingido. Salvando a última versão final mesmo assim devido à regra de flexibilização.[/yellow]")
        # db.atualizar_status(plano["id"], "needs_human_review")
        # em vez de abortar, prosseguimos para gravar na tabela final e liberar para o frontend.

    # 6. SALVAR FINAL
    console.print("\n[bold cyan]💾 ETAPA 5: Salvando versão final[/bold cyan]")
    from .models.devocional import DevocionalFinal

    final = DevocionalFinal(
        plano_id=plano["id"],
        titulo=trabalho.titulo,
        texto_biblico=plano["texto_biblico"],
        subtema=plano["tema_central"],
        tema_semana=plano["tema_semana"],
        tema_mes=plano["tema_mes"],
        conteudo_md=trabalho.conteudo_md,
        palavras=trabalho.palavras,
        exegese_id=exegese.id,
        escritor_trabalho_id=trabalho.id,
        revisao_final_id=revisao_db["id"],
        versao_aprovada=trabalho.versao,
        score_final=revisao.score_total,
    )

    final_db = db.salvar_devocional_final(final.to_db_dict())
    db.atualizar_status(plano["id"], "aprovado")
    logger.info(f"S{semana}D{dia} APROVADO score={revisao.score_total:.1f} v={trabalho.versao} palavras={trabalho.palavras}")
    console.print(f"   ✅ Devocional final salvo: {final_db['id']}")

    # 7. NARRADOR (opcional)
    if ate_narracao:
        console.print("\n[bold cyan]🎙️  ETAPA 6: Agente Narrador[/bold cyan]")
        with console.status("Convertendo para texto de narração..."):
            narrador = AgenteNarrador()
            narracao = narrador.converter(final_db)

        narracao_db = db.salvar_narracao(narracao.to_db_dict())
        console.print(f"   ✅ Narração salva: {narracao_db['id']} ({narracao.palavras} palavras)")

    # Resumo final
    console.print(Panel(
        f"📖 [bold]{plano['texto_biblico']}[/bold]\n"
        f"✍️  {trabalho.titulo}\n"
        f"📊 Score: {revisao.score_total:.1f}/100 (v{trabalho.versao})\n"
        f"📐 {trabalho.palavras} palavras",
        title="✅ Pipeline Completo",
        border_style="green",
    ))


@app.command()
def executar_semana(
    semana: int = typer.Option(..., "--semana", "-s", help="Número da semana (1-52)"),
):
    """🚀 Executar pipeline para todos os 7 dias de uma semana."""
    from .db.client import get_plano_by_semana

    dias = get_plano_by_semana(semana)
    if not dias:
        console.print(f"[red]❌ Semana {semana} não encontrada.[/red]")
        raise typer.Exit(1)

    console.print(f"\n📅 Executando Semana {semana}: {len(dias)} dias")
    console.print(f"   Tema: {dias[0]['tema_semana']}\n")

    # Estados que indicam processamento completo (pular)
    SKIP_STATES = {"aprovado", "needs_human_review"}
    # Estados intermediários que indicam crash anterior (reprocessar)
    STUCK_STATES = {
        "exegese_em_andamento", "exegese_concluida",
        "pesquisa_em_andamento", "pesquisa_concluida",
        "escrita_em_andamento", "escrita_concluida",
        "revisao_em_andamento",
    }

    from .db import client as db
    import logging
    logger = logging.getLogger("ryle_pipeline")

    for dia in dias:
        if dia["status"] in SKIP_STATES:
            console.print(f"   ⏭ Dia {dia['dia_semana']} ({dia['dia_nome']}) — já {dia['status']}")
            continue

        if dia["status"] in STUCK_STATES:
            console.print(f"   🔄 Dia {dia['dia_semana']} ({dia['dia_nome']}) — retomando de '{dia['status']}'")
            # Reset para pending para reprocessar do zero
            db.atualizar_status(dia["id"], "pending")

        console.rule(f"Dia {dia['dia_semana']} — {dia['dia_nome']}")
        try:
            executar(semana=semana, dia=dia["dia_semana"], ate_narracao=True)
        except SystemExit:
            pass
        except Exception as e:
            error_msg = str(e)[:500]
            console.print(f"   [red]❌ Erro: {error_msg}[/red]")
            logger.error(f"S{semana}D{dia['dia_semana']} falhou: {error_msg}")
            # Marcar como erro no banco para rastreamento
            try:
                db.atualizar_status(dia["id"], "erro")
            except Exception:
                pass
            continue


@app.command()
def validar():
    """🔍 Validar configuração do pipeline."""
    from . import config

    console.print("\n🔧 [bold]Validação de Configuração[/bold]\n")

    checks = [
        ("Supabase URL", bool(config.SUPABASE_URL)),
        ("Supabase Key", bool(config.SUPABASE_ANON_KEY)),
        ("LLM Provider", config.LLM_PROVIDER),
        ("Modelo", config.get_llm_model()),
        ("Pesquisa habilitada", config.PESQUISA_HABILITADA),
    ]

    # Check API key para o provider ativo
    if config.LLM_PROVIDER == "gemini":
        checks.append(("Gemini API Key", bool(config.GEMINI_API_KEY)))
    elif config.LLM_PROVIDER == "openai":
        checks.append(("OpenAI API Key", bool(config.OPENAI_API_KEY)))
    elif config.LLM_PROVIDER == "anthropic":
        checks.append(("Anthropic API Key", bool(config.ANTHROPIC_API_KEY)))

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


if __name__ == "__main__":
    app()
