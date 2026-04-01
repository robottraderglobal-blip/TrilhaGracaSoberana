"""
Ryle Pipeline — Configuração Central
Carrega .env, inicializa clients de Supabase e LLM.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Carregar .env ─────────────────────────────────────────
ROOT_DIR = Path(__file__).parent
PROJECT_DIR = ROOT_DIR.parent
load_dotenv(PROJECT_DIR / ".env")

# ── Supabase ──────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# ── LLM Provider ─────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # gemini | openai | anthropic
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Modelos padrão por provider
LLM_MODELS = {
    "gemini": os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-05-06"),
    "openai": os.getenv("OPENAI_MODEL", "gpt-4o"),
    "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
    "openrouter": os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite"),
}

# ── NotebookLM (IDs dos notebooks com fontes teológicas) ──
NOTEBOOK_SPROUL = os.getenv("NOTEBOOK_SPROUL", "")
NOTEBOOK_AUGUSTUS = os.getenv("NOTEBOOK_AUGUSTUS", "")
NOTEBOOK_SPURGEON = os.getenv("NOTEBOOK_SPURGEON", "")
NOTEBOOK_LLOYDJ = os.getenv("NOTEBOOK_LLOYDJ", "")

FONTES_NOTEBOOKS = {
    "sproul": NOTEBOOK_SPROUL,
    "augustus": NOTEBOOK_AUGUSTUS,
    "spurgeon": NOTEBOOK_SPURGEON,
    "lloyd_jones": NOTEBOOK_LLOYDJ,
}

# ── Pipeline Config ───────────────────────────────────────
MAX_CICLOS_REVISAO = int(os.getenv("MAX_CICLOS_REVISAO", "3"))
SCORE_MINIMO_APROVACAO = float(os.getenv("SCORE_MINIMO_APROVACAO", "80.0"))
PALAVRAS_MIN = int(os.getenv("PALAVRAS_MIN", "800"))
PALAVRAS_MAX = int(os.getenv("PALAVRAS_MAX", "1200"))
PESQUISA_HABILITADA = os.getenv("PESQUISA_HABILITADA", "false").lower() == "true"

# ── Paths ─────────────────────────────────────────────────
PROMPTS_DIR = ROOT_DIR / "prompts"
DATA_DIR = ROOT_DIR / "data"
EXPORT_DIR = ROOT_DIR / "exports"


def get_llm_model() -> str:
    """Retorna o modelo LLM configurado para o provider atual."""
    return LLM_MODELS.get(LLM_PROVIDER, LLM_MODELS["gemini"])


def validate_config():
    """Valida que as configurações mínimas estão presentes."""
    errors = []
    if not SUPABASE_URL:
        errors.append("SUPABASE_URL não configurado")
    if not SUPABASE_ANON_KEY:
        errors.append("SUPABASE_ANON_KEY não configurado")

    if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY não configurado (LLM_PROVIDER=gemini)")
    elif LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY não configurado (LLM_PROVIDER=openai)")
    elif LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY não configurado (LLM_PROVIDER=anthropic)")
    elif LLM_PROVIDER == "openrouter" and not OPENROUTER_API_KEY:
        errors.append("OPENROUTER_API_KEY não configurado (LLM_PROVIDER=openrouter)")

    if errors:
        raise ValueError(
            "Configuração incompleta:\n" + "\n".join(f"  - {e}" for e in errors)
        )
