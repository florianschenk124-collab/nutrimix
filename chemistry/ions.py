"""
Ionendefinitionen mit Atom-/Molmassen und Leitfähigkeitskoeffizienten.

Alle Konzentrationen intern in mmol/L, Umrechnung zu mg/L über Molmassen.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Ion:
    """Ein Ion mit seinen physikalisch-chemischen Eigenschaften."""
    symbol: str           # Kurzbezeichnung (z.B. "NO3", "Ca")
    display: str          # Anzeige mit Ladung (z.B. "NO₃⁻", "Ca²⁺")
    element: str          # Bezugselement für mg/L (z.B. "N" bei NO₃)
    molar_mass: float     # Molmasse des Bezugselements in g/mol
    ion_molar_mass: float # Molmasse des gesamten Ions in g/mol
    charge: int           # Ladungszahl (z.B. -1, +2)
    # Molare Leitfähigkeit bei unendlicher Verdünnung (S·cm²/mol) für EC-Schätzung
    lambda_0: float


# ═══════════════════════════════════════════════════════════════════════
# Makronährstoff-Ionen
# ═══════════════════════════════════════════════════════════════════════

NO3 = Ion(
    symbol="NO3", display="NO₃⁻", element="N",
    molar_mass=14.007, ion_molar_mass=62.004,
    charge=-1, lambda_0=71.42,
)

NH4 = Ion(
    symbol="NH4", display="NH₄⁺", element="N",
    molar_mass=14.007, ion_molar_mass=18.039,
    charge=+1, lambda_0=73.55,
)

H2PO4 = Ion(
    symbol="H2PO4", display="H₂PO₄⁻", element="P",
    molar_mass=30.974, ion_molar_mass=96.987,
    charge=-1, lambda_0=33.00,
)

K = Ion(
    symbol="K", display="K⁺", element="K",
    molar_mass=39.098, ion_molar_mass=39.098,
    charge=+1, lambda_0=73.50,
)

Ca = Ion(
    symbol="Ca", display="Ca²⁺", element="Ca",
    molar_mass=40.078, ion_molar_mass=40.078,
    charge=+2, lambda_0=119.00,
)

Mg = Ion(
    symbol="Mg", display="Mg²⁺", element="Mg",
    molar_mass=24.305, ion_molar_mass=24.305,
    charge=+2, lambda_0=106.12,
)

SO4 = Ion(
    symbol="SO4", display="SO₄²⁻", element="S",
    molar_mass=32.060, ion_molar_mass=96.060,
    charge=-2, lambda_0=160.00,
)

Cl = Ion(
    symbol="Cl", display="Cl⁻", element="Cl",
    molar_mass=35.453, ion_molar_mass=35.453,
    charge=-1, lambda_0=76.35,
)

Na = Ion(
    symbol="Na", display="Na⁺", element="Na",
    molar_mass=22.990, ion_molar_mass=22.990,
    charge=+1, lambda_0=50.10,
)

HCO3 = Ion(
    symbol="HCO3", display="HCO₃⁻", element="HCO3",
    molar_mass=61.017, ion_molar_mass=61.017,
    charge=-1, lambda_0=44.50,
)

# ═══════════════════════════════════════════════════════════════════════
# Mikronährstoff-Ionen (Bezug auf Element, nicht auf Ion-Form)
# ═══════════════════════════════════════════════════════════════════════

Fe = Ion(
    symbol="Fe", display="Fe", element="Fe",
    molar_mass=55.845, ion_molar_mass=55.845,
    charge=+3, lambda_0=68.00,
)

Mn = Ion(
    symbol="Mn", display="Mn²⁺", element="Mn",
    molar_mass=54.938, ion_molar_mass=54.938,
    charge=+2, lambda_0=107.00,
)

Zn = Ion(
    symbol="Zn", display="Zn²⁺", element="Zn",
    molar_mass=65.380, ion_molar_mass=65.380,
    charge=+2, lambda_0=105.60,
)

Cu = Ion(
    symbol="Cu", display="Cu²⁺", element="Cu",
    molar_mass=63.546, ion_molar_mass=63.546,
    charge=+2, lambda_0=107.20,
)

B = Ion(
    symbol="B", display="B", element="B",
    molar_mass=10.811, ion_molar_mass=10.811,
    charge=0, lambda_0=0.0,  # Borsäure undissoziiert → kein EC-Beitrag
)

Mo = Ion(
    symbol="Mo", display="Mo", element="Mo",
    molar_mass=95.950, ion_molar_mass=95.950,
    charge=0, lambda_0=0.0,
)


# ═══════════════════════════════════════════════════════════════════════
# Gruppierungen
# ═══════════════════════════════════════════════════════════════════════

MACRO_IONS = [NO3, NH4, H2PO4, K, Ca, Mg, SO4]
MICRO_IONS = [Fe, Mn, Zn, Cu, B, Mo]
WATER_IONS = [Ca, Mg, Na, K, Cl, SO4, HCO3, NO3, Fe]
ALL_IONS = MACRO_IONS + MICRO_IONS + [Cl, Na, HCO3]

# Lookup nach Symbol
ION_BY_SYMBOL: dict[str, Ion] = {ion.symbol: ion for ion in ALL_IONS}


# ═══════════════════════════════════════════════════════════════════════
# Hilfsfunktionen zur Umrechnung
# ═══════════════════════════════════════════════════════════════════════

def mg_to_mmol(mg_per_l: float, ion: Ion) -> float:
    """mg/L (bezogen auf Element) → mmol/L."""
    return mg_per_l / ion.molar_mass

def mmol_to_mg(mmol_per_l: float, ion: Ion) -> float:
    """mmol/L → mg/L (bezogen auf Element)."""
    return mmol_per_l * ion.molar_mass
