"""
Nicodemos Pipeline 100 — Configuração Central
Carrega .env do projeto raiz, inicializa configs de Supabase e LLM.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Carregar .env ─────────────────────────────────────────
ROOT_DIR = Path(__file__).parent
PROJECT_DIR = ROOT_DIR.parent
load_dotenv(PROJECT_DIR / ".env", override=True)

# ── Supabase (NICO_SUPABASE_* tem prioridade sobre SUPABASE_*) ──
SUPABASE_URL = os.getenv("NICO_SUPABASE_URL", "") or os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("NICO_SUPABASE_ANON_KEY", "") or os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("NICO_SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# ── LLM Provider ─────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # gemini | openai | anthropic | openrouter
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

# ── Pipeline Config (Nicodemos) ───────────────────────────
MAX_CICLOS_REVISAO = int(os.getenv("NICO_MAX_CICLOS_REVISAO", "2"))
SCORE_MINIMO_APROVACAO = float(os.getenv("NICO_SCORE_MINIMO", "80.0"))
PALAVRAS_MIN = int(os.getenv("NICO_PALAVRAS_MIN", "700"))
PALAVRAS_MAX = int(os.getenv("NICO_PALAVRAS_MAX", "1000"))

# ── Paths ─────────────────────────────────────────────────
PROMPTS_DIR = ROOT_DIR / "prompts"
PLANO_JSON = PROJECT_DIR / "100_devocionais" / "plano_100dias.json"
PLANO_EXPANSAO_JSON = PROJECT_DIR / "100_devocionais" / "plano_expansao_50.json"


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
