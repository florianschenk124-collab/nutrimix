"""
Tank A/B Aufteilung.

Regel: Ca²⁺-haltige Salze und Fe-Chelate in Tank A,
Sulfate, Phosphate und Mikronährstoffe in Tank B.

Grund: Ca²⁺ bildet mit SO₄²⁻ und HPO₄²⁻ schwerlösliche
Niederschläge (CaSO₄, Ca₃(PO₄)₂).
"""

from ui.locales import t
from chemistry.salts import Salt


# Regeln für Tank-Zuordnung
TANK_A_RULES = {
    "Ca": True,      # Alles mit Calcium → A
    "Fe": True,      # Eisen-Chelate → A (Stabilität)
}

TANK_B_RULES = {
    "SO4": True,     # Sulfate → B
    "H2PO4": True,   # Phosphate → B
    "Mn": True,      # Mikronährstoffe → B
    "Zn": True,
    "Cu": True,
    "B": True,
    "Mo": True,
}


def assign_tank(salt: Salt) -> str:
    """
    Weist einem Salz den Tank zu (A oder B).

    Priorität:
    1. Explizite Zuweisung am Salz (wenn "A" oder "B")
    2. Regelbasiert nach Ioneninhalt
    3. Default: B

    Args:
        salt: Das Salz

    Returns:
        "A" oder "B"
    """
    # Wenn das Salz eine feste Zuweisung hat
    if salt.tank in ("A", "B"):
        return salt.tank

    # Regelbasiert: Calcium-haltig → A
    for ion_sym in salt.ion_contribution:
        if ion_sym in TANK_A_RULES:
            return "A"

    # Regelbasiert: Sulfat/Phosphat/Mikro → B
    for ion_sym in salt.ion_contribution:
        if ion_sym in TANK_B_RULES:
            return "B"

    return "B"  # Default


def validate_ab_split(tank_a_salts: list[Salt], tank_b_salts: list[Salt]) -> list[str]:
    """
    Prüft, ob die A/B-Trennung korrekt ist.

    Hauptregel: Ca²⁺ und SO₄²⁻/PO₄³⁻ dürfen nicht im gleichen Tank sein.

    Returns:
        Liste von Warnungen (leer wenn alles OK).
    """
    warnings = []

    # Ionen in Tank A sammeln
    a_ions = set()
    for salt in tank_a_salts:
        a_ions.update(salt.ion_contribution.keys())

    # Ionen in Tank B sammeln
    b_ions = set()
    for salt in tank_b_salts:
        b_ions.update(salt.ion_contribution.keys())

    # Prüfung: Ca + SO4 im gleichen Tank?
    if "Ca" in a_ions and "SO4" in a_ions:
        warnings.append(
            f"⚠️ Tank A: Ca²⁺ + SO₄²⁻ → {t('b.warn_caso4')}"
        )
    if "Ca" in b_ions and "SO4" in b_ions:
        warnings.append(
            f"⚠️ Tank B: Ca²⁺ + SO₄²⁻ → {t('b.warn_caso4')}"
        )

    # Prüfung: Ca + PO4 im gleichen Tank?
    if "Ca" in a_ions and "H2PO4" in a_ions:
        warnings.append(
            f"⚠️ Tank A: Ca²⁺ + PO₄³⁻ → {t('b.warn_ca3po4')}"
        )
    if "Ca" in b_ions and "H2PO4" in b_ions:
        warnings.append(
            f"⚠️ Tank B: Ca²⁺ + PO₄³⁻ → {t('b.warn_ca3po4')}"
        )

    return warnings


def get_ab_summary(tank_a_salts: list[Salt], tank_b_salts: list[Salt]) -> dict:
    """
    Erstellt eine Zusammenfassung der A/B-Aufteilung.

    Returns:
        Dict mit "tank_a" und "tank_b" Listen der Salznamen.
    """
    return {
        "tank_a": [s.name for s in tank_a_salts],
        "tank_b": [s.name for s in tank_b_salts],
        "tank_a_count": len(tank_a_salts),
        "tank_b_count": len(tank_b_salts),
    }
