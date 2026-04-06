import asyncio
import os
import sys

# Garante que as credenciais do .env são carregadas
from dotenv import load_dotenv
load_dotenv()

# Ajusta o import path para poder achar ryle_pipeline localmente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ryle_pipeline import config
from rich.console import Console
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

console = Console()

async def testar_conexao():
    console.print("[cyan]1. Iniciando teste de conexão direta via MCP para o NotebookLM...[/cyan]")
    server_params = StdioServerParameters(command="notebooklm-mcp", args=[])
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                console.print("[yellow]Subindo conexão com o servidor local...[/yellow]")
                await session.initialize()
                
                # Teste 1: Health Check (Acesso às ferramentas)
                console.print("\n[cyan]2. Executando Health Check...[/cyan]")
                tools = await asyncio.wait_for(session.list_tools(), timeout=10.0)
                nomes_tools = [t.name for t in tools.tools]
                
                if "notebook_query" in nomes_tools:
                    console.print("[green]✔ Sucesso! Servidor respondeu. A ferramenta 'notebook_query' está online.[/green]")
                else:
                    console.print(f"[red]❌ Falha! Ferramentas encontradas: {nomes_tools}[/red]")
                    return
                
                # Teste 2: Consultando Spourgeon (ou um dos notebooks de teste configurados)
                fontes_validas = {
                    nome: nb_id
                    for nome, nb_id in config.FONTES_NOTEBOOKS.items()
                    if nb_id and nb_id.strip()
                }
                
                if not fontes_validas:
                    console.print("[red]❌ Nenhum notebook configurado no ambiente.[/red]")
                    return
                
                primeira_fonte = list(fontes_validas.keys())[0]
                notebook_teste_id = fontes_validas[primeira_fonte]
                
                console.print(f"\n[cyan]3. Tirando prova real: Consultando Notebook ({primeira_fonte})...[/cyan]")
                params = {"notebook_id": notebook_teste_id, "query": "Escreva um resumo de 2 frases sobre a graça de Deus."}
                
                resultado_mcp = await session.call_tool("notebook_query", params)
                textos = [c.text for c in resultado_mcp.content if c.type == "text"]
                candidato = "\n".join(textos).strip()
                
                if len(candidato) > 10:
                    console.print(f"[green]✔ Conexão MCP está 100% Viva! Resposta obtida:[/green]")
                    console.print(f"   [italic]\"{candidato}\"[/italic]")
                else:
                    console.print("[red]❌ NotebookLM respondeu, mas vazio.[/red]")

    except Exception as e:
        console.print(f"\n[red]🚨 Falha crítica de conexão:[/red] {str(e)}")
        console.print("Provavelmente o seu 'notebooklm-mcp' requer reautenticação no navegador.")

if __name__ == "__main__":
    asyncio.run(testar_conexao())
