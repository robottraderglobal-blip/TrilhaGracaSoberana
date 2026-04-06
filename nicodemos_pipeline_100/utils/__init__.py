"""
Nicodemos Pipeline 100 — Utilitário de lookup na Bíblia ARA.
Carrega ARA.json e busca versículos por referência.
"""
import json
import re
from pathlib import Path
from functools import lru_cache

ARA_PATH = Path(__file__).parent.parent.parent / "ryle_pipeline" / "utils" / "ARA.json"

# Mapeamento de nomes de livros para abreviações da ARA.json
_BOOK_MAP = {
    # Antigo Testamento
    "gênesis": "Gn", "genesis": "Gn", "gn": "Gn",
    "êxodo": "Êx", "exodo": "Êx", "ex": "Êx", "êx": "Êx",
    "levítico": "Lv", "levitico": "Lv", "lv": "Lv",
    "números": "Nm", "numeros": "Nm", "nm": "Nm",
    "deuteronômio": "Dt", "deuteronomio": "Dt", "dt": "Dt",
    "josué": "Js", "josue": "Js", "js": "Js",
    "juízes": "Jz", "juizes": "Jz", "jz": "Jz",
    "rute": "Rt", "rt": "Rt",
    "1 samuel": "1Sm", "1samuel": "1Sm", "1sm": "1Sm", "1 sm": "1Sm",
    "2 samuel": "2Sm", "2samuel": "2Sm", "2sm": "2Sm", "2 sm": "2Sm",
    "1 reis": "1Rs", "1reis": "1Rs", "1rs": "1Rs", "1 rs": "1Rs",
    "2 reis": "2Rs", "2reis": "2Rs", "2rs": "2Rs", "2 rs": "2Rs",
    "1 crônicas": "1Cr", "1 cronicas": "1Cr", "1cronicas": "1Cr", "1cr": "1Cr", "1 cr": "1Cr",
    "2 crônicas": "2Cr", "2 cronicas": "2Cr", "2cronicas": "2Cr", "2cr": "2Cr", "2 cr": "2Cr",
    "esdras": "Ed", "ed": "Ed",
    "neemias": "Ne", "ne": "Ne",
    "ester": "Et", "et": "Et",
    "jó": "Jó", "jo": "Jó", "jó": "Jó",
    "salmos": "Sl", "salmo": "Sl", "sl": "Sl",
    "provérbios": "Pv", "proverbios": "Pv", "pv": "Pv",
    "eclesiastes": "Ec", "ec": "Ec",
    "cânticos": "Ct", "canticos": "Ct", "cantares": "Ct", "ct": "Ct",
    "isaías": "Is", "isaias": "Is", "is": "Is",
    "jeremias": "Jr", "jr": "Jr",
    "lamentações": "Lm", "lamentacoes": "Lm", "lm": "Lm",
    "ezequiel": "Ez", "ez": "Ez",
    "daniel": "Dn", "dn": "Dn",
    "oséias": "Os", "oseias": "Os", "os": "Os",
    "joel": "Jl", "jl": "Jl",
    "amós": "Am", "amos": "Am", "am": "Am",
    "obadias": "Ob", "ob": "Ob",
    "jonas": "Jn", "jn": "Jn",
    "miquéias": "Mq", "miqueias": "Mq", "mq": "Mq",
    "naum": "Na", "na": "Na",
    "habacuque": "Hc", "hc": "Hc",
    "sofonias": "Sf", "sf": "Sf",
    "ageu": "Ag", "ag": "Ag",
    "zacarias": "Zc", "zc": "Zc",
    "malaquias": "Ml", "ml": "Ml",
    # Novo Testamento
    "mateus": "Mt", "mt": "Mt",
    "marcos": "Mc", "mc": "Mc",
    "lucas": "Lc", "lc": "Lc",
    "joão": "Jo", "joao": "Jo",
    "atos": "At", "at": "At",
    "romanos": "Rm", "rm": "Rm",
    "1 coríntios": "1Co", "1 corintios": "1Co", "1corintios": "1Co", "1co": "1Co", "1 co": "1Co",
    "2 coríntios": "2Co", "2 corintios": "2Co", "2corintios": "2Co", "2co": "2Co", "2 co": "2Co",
    "gálatas": "Gl", "galatas": "Gl", "gl": "Gl",
    "efésios": "Ef", "efesios": "Ef", "ef": "Ef",
    "filipenses": "Fp", "fp": "Fp",
    "colossenses": "Cl", "cl": "Cl",
    "1 tessalonicenses": "1Ts", "1tessalonicenses": "1Ts", "1ts": "1Ts", "1 ts": "1Ts",
    "2 tessalonicenses": "2Ts", "2tessalonicenses": "2Ts", "2ts": "2Ts", "2 ts": "2Ts",
    "1 timóteo": "1Tm", "1 timoteo": "1Tm", "1timoteo": "1Tm", "1tm": "1Tm", "1 tm": "1Tm",
    "2 timóteo": "2Tm", "2 timoteo": "2Tm", "2timoteo": "2Tm", "2tm": "2Tm", "2 tm": "2Tm",
    "tito": "Tt", "tt": "Tt",
    "filemom": "Fm", "filemon": "Fm", "fm": "Fm",
    "hebreus": "Hb", "hb": "Hb",
    "tiago": "Tg", "tg": "Tg",
    "1 pedro": "1Pe", "1pedro": "1Pe", "1pe": "1Pe", "1 pe": "1Pe",
    "2 pedro": "2Pe", "2pedro": "2Pe", "2pe": "2Pe", "2 pe": "2Pe",
    "1 joão": "1Jo", "1 joao": "1Jo", "1joao": "1Jo", "1jo": "1Jo", "1 jo": "1Jo",
    "2 joão": "2Jo", "2 joao": "2Jo", "2joao": "2Jo", "2jo": "2Jo", "2 jo": "2Jo",
    "3 joão": "3Jo", "3 joao": "3Jo", "3joao": "3Jo", "3jo": "3Jo", "3 jo": "3Jo",
    "judas": "Jd", "jd": "Jd",
    "apocalipse": "Ap", "ap": "Ap",
}


@lru_cache(maxsize=1)
def _load_ara() -> list[dict]:
    """Carrega ARA.json uma única vez."""
    return json.loads(ARA_PATH.read_text(encoding="utf-8"))


def _find_book(name: str) -> dict | None:
    """Encontra um livro pelo nome ou abreviação."""
    normalized = name.strip().lower()
    abbrev = _BOOK_MAP.get(normalized)
    if not abbrev:
        return None

    for book in _load_ara():
        if book["abbrev"] == abbrev:
            return book
    return None


def parse_ref(ref: str) -> tuple[str, int, int]:
    """
    Parseia uma referência bíblica.
    Ex: "Salmos 100.4" -> ("Salmos", 100, 4)
        "1 João 3.16" -> ("1 João", 3, 16)
        "Gênesis 1.1" -> ("Gênesis", 1, 1)
    """
    # Regex que captura: livro (pode começar com número), capítulo.versículo
    match = re.match(r'^(\d?\s*\w+(?:\s+\w+)?)\s+(\d+)[.:](\d+)$', ref.strip())
    if not match:
        raise ValueError(f"Referência inválida: {ref}")
    return match.group(1).strip(), int(match.group(2)), int(match.group(3))


def get_verse(ref: str) -> str | None:
    """
    Busca o texto de um versículo pela referência.
    Ex: get_verse("Salmos 100.4") -> "Entrai por suas portas..."
    """
    try:
        book_name, chapter, verse = parse_ref(ref)
    except ValueError:
        return None

    book = _find_book(book_name)
    if not book:
        return None

    try:
        # chapters é 0-indexed, verses é 0-indexed
        return book["chapters"][chapter - 1][verse - 1]
    except (IndexError, KeyError):
        return None


def get_verse_or_fallback(ref: str, fallback: str) -> str:
    """Busca versículo da ARA, retorna fallback se não encontrar."""
    verse = get_verse(ref)
    return verse if verse else fallback
