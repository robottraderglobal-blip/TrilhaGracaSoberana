"""Ryle Pipeline — Supabase Client Wrapper."""
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


# ── Helpers: plano_devocional ─────────────────────────────


def get_plano_by_semana(semana: int) -> list[dict]:
    """Retorna os 7 dias de uma semana específica."""
    return (
        get_client()
        .table("plano_devocional")
        .select("*")
        .eq("semana", semana)
        .order("dia_semana")
        .execute()
        .data
    )


def get_plano_by_semana_dia(semana: int, dia: int) -> dict | None:
    """Retorna um dia específico."""
    result = (
        get_client()
        .table("plano_devocional")
        .select("*")
        .eq("semana", semana)
        .eq("dia_semana", dia)
        .maybe_single()
        .execute()
    )
    return result.data if result else None


def get_plano_by_id(plano_id: str) -> dict | None:
    result = (
        get_client()
        .table("plano_devocional")
        .select("*")
        .eq("id", plano_id)
        .maybe_single()
        .execute()
    )
    return result.data if result else None


def get_pendentes(limit: int = 50) -> list[dict]:
    """Retorna dias com status 'pending'."""
    return (
        get_client()
        .table("plano_devocional")
        .select("*")
        .eq("status", "pending")
        .order("semana")
        .order("dia_semana")
        .limit(limit)
        .execute()
        .data
    )


def atualizar_status(plano_id: str, novo_status: str):
    """Atualiza o status de um dia no plano."""
    get_client().table("plano_devocional").update(
        {"status": novo_status}
    ).eq("id", plano_id).execute()


def contar_por_status() -> dict[str, int]:
    """Retorna contagem de dias por status."""
    result = get_client().table("plano_devocional").select("status").execute()
    contagem: dict[str, int] = {}
    for row in result.data:
        s = row["status"]
        contagem[s] = contagem.get(s, 0) + 1
    return contagem


# ── Helpers: exegeses ─────────────────────────────────────


def salvar_exegese(data: dict) -> dict:
    return get_client().table("exegeses").insert(data).execute().data[0]


def get_exegese_by_plano(plano_id: str) -> dict | None:
    result = (
        get_client()
        .table("exegeses")
        .select("*")
        .eq("plano_id", plano_id)
        .maybe_single()
        .execute()
    )
    return result.data if result else None


# ── Helpers: pesquisa_fontes ──────────────────────────────


def salvar_pesquisa(data: dict) -> dict:
    return get_client().table("pesquisa_fontes").insert(data).execute().data[0]


def get_pesquisas_by_plano(plano_id: str) -> list[dict]:
    return (
        get_client()
        .table("pesquisa_fontes")
        .select("*")
        .eq("plano_id", plano_id)
        .execute()
        .data
    )


# ── Helpers: escritor_trabalho ────────────────────────────


def salvar_rascunho(data: dict) -> dict:
    return get_client().table("escritor_trabalho").insert(data).execute().data[0]


def get_ultimo_rascunho(plano_id: str) -> dict | None:
    result = (
        get_client()
        .table("escritor_trabalho")
        .select("*")
        .eq("plano_id", plano_id)
        .order("versao", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    return result.data if result else None


# ── Helpers: revisoes ─────────────────────────────────────


def salvar_revisao(data: dict) -> dict:
    return get_client().table("revisoes").insert(data).execute().data[0]


# ── Helpers: devocionais_final ────────────────────────────


def salvar_devocional_final(data: dict) -> dict:
    return get_client().table("devocionais_final").insert(data).execute().data[0]


def get_devocional_final(plano_id: str) -> dict | None:
    result = (
        get_client()
        .table("devocionais_final")
        .select("*")
        .eq("plano_id", plano_id)
        .maybe_single()
        .execute()
    )
    return result.data if result else None


# ── Helpers: devocionais_narracao ─────────────────────────


def salvar_narracao(data: dict) -> dict:
    return get_client().table("devocionais_narracao").insert(data).execute().data[0]


# ── Bulk: seed ────────────────────────────────────────────


def seed_plano(entries: list[dict]) -> int:
    """Insere múltiplas entradas no plano_devocional. Retorna contagem."""
    result = get_client().table("plano_devocional").upsert(
        entries, on_conflict="semana,dia_semana"
    ).execute()
    return len(result.data)
