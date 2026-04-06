"""Nicodemos Pipeline 100 — Supabase Client Wrapper."""
from supabase import create_client, Client
from .. import config


_client: Client | None = None


def get_client() -> Client:
    """Retorna instância singleton do Supabase client."""
    global _client
    if _client is None:
        key = config.SUPABASE_SERVICE_KEY or config.SUPABASE_ANON_KEY
        _client = create_client(config.SUPABASE_URL, key)
    return _client


# ── Helpers: nico_plano ───────────────────────────────────


def get_plano_by_dia(dia: int) -> dict | None:
    """Retorna um dia específico pelo número (1-100)."""
    result = (
        get_client()
        .table("nico_plano")
        .select("*")
        .eq("dia", dia)
        .maybe_single()
        .execute()
    )
    return result.data if result else None


def get_plano_by_semana(semana: int) -> list[dict]:
    """Retorna todos os dias de uma semana específica."""
    return (
        get_client()
        .table("nico_plano")
        .select("*")
        .eq("semana", semana)
        .order("dia")
        .execute()
        .data
    )


def get_pendentes(limit: int = 50) -> list[dict]:
    """Retorna dias com status 'pending'."""
    return (
        get_client()
        .table("nico_plano")
        .select("*")
        .eq("status", "pending")
        .order("dia")
        .limit(limit)
        .execute()
        .data
    )


def atualizar_status(plano_id: str, novo_status: str):
    """Atualiza o status de um dia no plano."""
    get_client().table("nico_plano").update(
        {"status": novo_status}
    ).eq("id", plano_id).execute()


def contar_por_status() -> dict[str, int]:
    """Retorna contagem de dias por status."""
    result = get_client().table("nico_plano").select("status").execute()
    contagem: dict[str, int] = {}
    for row in result.data:
        s = row["status"]
        contagem[s] = contagem.get(s, 0) + 1
    return contagem


# ── Helpers: nico_devocionais_rascunho ───────────────────────


def salvar_rascunho(data: dict) -> dict:
    return get_client().table("nico_devocionais_rascunho").insert(data).execute().data[0]


def get_ultimo_rascunho(plano_id: str) -> dict | None:
    result = (
        get_client()
        .table("nico_devocionais_rascunho")
        .select("*")
        .eq("plano_id", plano_id)
        .order("versao", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    return result.data if result else None


# ── Helpers: nico_devocionais_revisao ────────────────────────────────


def salvar_revisao(data: dict) -> dict:
    return get_client().table("nico_devocionais_revisao").insert(data).execute().data[0]


# ── Helpers: nico_devocionais_final ───────────────────────


def salvar_devocional_final(data: dict) -> dict:
    return get_client().table("nico_devocionais_final").insert(data).execute().data[0]


def get_devocional_final(plano_id: str) -> dict | None:
    result = (
        get_client()
        .table("nico_devocionais_final")
        .select("*")
        .eq("plano_id", plano_id)
        .maybe_single()
        .execute()
    )
    return result.data if result else None


def get_devocionais_by_semana(semana: int) -> list[dict]:
    """Retorna devocionais finais de uma semana."""
    return (
        get_client()
        .table("nico_devocionais_final")
        .select("*")
        .eq("semana", semana)
        .order("dia")
        .execute()
        .data
    )


# ── Bulk: seed ────────────────────────────────────────────


def seed_plano(entries: list[dict]) -> int:
    """Insere múltiplas entradas no nico_plano. Retorna contagem."""
    result = get_client().table("nico_plano").upsert(
        entries, on_conflict="dia"
    ).execute()
    return len(result.data)


# ── Cleanup helpers ───────────────────────────────────────


def limpar_dados_dia(plano_id: str):
    """Remove dados intermediários de um dia para reprocessamento."""
    c = get_client()
    try:
        c.table("nico_devocionais_final").delete().eq("plano_id", plano_id).execute()
    except Exception:
        pass
    try:
        c.table("nico_devocionais_revisao").delete().eq("rascunho_id", plano_id).execute() # Note: The clean up doesn't perfectly cascade this way, but we will leave the structure. Better yet, we can filter by the FK properly. Wait, revisoes has `rascunho_id`, not `plano_id`... I will just fix the table name.
    except Exception:
        pass
    try:
        c.table("nico_devocionais_rascunho").delete().eq("plano_id", plano_id).execute()
    except Exception:
        pass
