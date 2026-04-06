"""
Nicodemos Pipeline 100 — Seed Data
Converte plano_100dias.json para formato de seed no Supabase.
Usa ARA.json para versículos oficiais.
"""
import json
from pathlib import Path
from .. import config
from ..utils import get_verse_or_fallback


def get_all_entries() -> list[dict]:
    """Lê plano_100dias.json e converte para formato de seed com texto ARA oficial."""
    plano_path = config.PLANO_JSON
    if not plano_path.exists():
        raise FileNotFoundError(f"Plano não encontrado: {plano_path}")

    plano_raw = json.loads(plano_path.read_text(encoding="utf-8"))
    entries = []

    for week_data in plano_raw:
        semana = week_data["week"]
        for day_data in week_data["days"]:
            dia = day_data["day"]
            dia_semana = ((dia - 1) % 7) + 1
            ref = day_data["ref"]

            # Buscar versículo oficial da ARA, com fallback para o texto do plano
            versiculo = get_verse_or_fallback(ref, day_data["t"])

            entries.append({
                "semana": semana,
                "dia": dia,
                "dia_semana": dia_semana,
                "ref": ref,
                "versiculo": versiculo,
                "status": "pending",
            })

    return entries
