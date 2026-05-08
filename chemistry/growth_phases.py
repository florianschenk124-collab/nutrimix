"""
Wachstumsphasen & Rezept-Phasen: Datenmodell für stadienabhängige Nährlösungen.

Basiert auf Literatur (Sonneveld & Voogt, de Kreij et al.) und Praxiserfahrung.
Enthält Standardphasen für gängige Kulturen und Interpolation zwischen Phasen.
"""

from dataclasses import dataclass, field


@dataclass
class GrowthPhase:
    """Eine Wachstumsphase mit Nährstoff-Modifikatoren."""
    name: str
    week_start: int             # Startwoche (ab Pflanzung)
    week_end: int               # Endwoche
    # Modifikatoren relativ zum Basisrezept (1.0 = unverändert)
    n_factor: float = 1.0       # Stickstoff-Faktor
    k_factor: float = 1.0       # Kalium-Faktor
    ca_factor: float = 1.0      # Calcium-Faktor
    mg_factor: float = 1.0      # Magnesium-Faktor
    p_factor: float = 1.0       # Phosphor-Faktor
    ec_target: float = 0.0      # EC-Ziel (0 = vom Basisrezept)
    nh4_ratio: float = 0.05     # NH₄:Gesamt-N Verhältnis (5% default)
    notes: str = ""


@dataclass
class GrowthPlan:
    """Ein vollständiger Wachstumsplan für eine Kultur."""
    name: str
    crop: str
    base_recipe_name: str       # Name des Basisrezepts
    total_weeks: int
    phases: list[GrowthPhase] = field(default_factory=list)
    description: str = ""
    source: str = ""
    is_custom: bool = False


def interpolate_week(plan: GrowthPlan, week: int) -> dict[str, float]:
    """
    Berechnet die Modifikatoren für eine bestimmte Woche.

    Zwischen zwei Phasen wird linear interpoliert.

    Returns: dict mit factor-Keys (n_factor, k_factor, etc.)
    """
    if not plan.phases:
        return {"n_factor": 1.0, "k_factor": 1.0, "ca_factor": 1.0,
                "mg_factor": 1.0, "p_factor": 1.0, "ec_target": 0, "nh4_ratio": 0.05}

    # Phase finden in der die Woche liegt
    for phase in plan.phases:
        if phase.week_start <= week <= phase.week_end:
            return _phase_to_dict(phase)

    # Zwischen zwei Phasen → interpolieren
    prev = None
    for phase in plan.phases:
        if week < phase.week_start:
            if prev is None:
                return _phase_to_dict(phase)
            # Interpolation zwischen prev und phase
            total = phase.week_start - prev.week_end
            if total <= 0:
                return _phase_to_dict(phase)
            progress = (week - prev.week_end) / total
            return _interpolate(prev, phase, progress)
        prev = phase

    # Nach letzter Phase
    return _phase_to_dict(plan.phases[-1])


def _phase_to_dict(phase: GrowthPhase) -> dict[str, float]:
    return {
        "n_factor": phase.n_factor, "k_factor": phase.k_factor,
        "ca_factor": phase.ca_factor, "mg_factor": phase.mg_factor,
        "p_factor": phase.p_factor, "ec_target": phase.ec_target,
        "nh4_ratio": phase.nh4_ratio,
    }


def _interpolate(a: GrowthPhase, b: GrowthPhase, t: float) -> dict[str, float]:
    """Linear interpolation between two phases. t in [0, 1]."""
    t = max(0.0, min(1.0, t))
    da = _phase_to_dict(a)
    db = _phase_to_dict(b)
    return {k: da[k] + (db[k] - da[k]) * t for k in da}


def apply_phase_to_recipe(recipe_mg: dict[str, float], factors: dict[str, float]) -> dict[str, float]:
    """
    Wendet Phasen-Modifikatoren auf ein Basisrezept an.

    Args:
        recipe_mg: Basisrezept als mg/L-dict
        factors: Modifikatoren aus interpolate_week()

    Returns: Angepasstes Rezept als mg/L-dict
    """
    adjusted = dict(recipe_mg)

    # N-Anpassung (NO₃ und NH₄ gemeinsam skalieren)
    nf = factors.get("n_factor", 1.0)
    adjusted["NO3"] = adjusted.get("NO3", 0) * nf
    adjusted["NH4"] = adjusted.get("NH4", 0) * nf

    # NH₄-Ratio anpassen
    nh4_ratio = factors.get("nh4_ratio", 0.05)
    total_n_mmol = adjusted.get("NO3", 0) / 62.0 + adjusted.get("NH4", 0) / 18.04
    if total_n_mmol > 0:
        nh4_mmol = total_n_mmol * nh4_ratio
        no3_mmol = total_n_mmol * (1 - nh4_ratio)
        adjusted["NO3"] = no3_mmol * 62.0
        adjusted["NH4"] = nh4_mmol * 18.04

    adjusted["K"] = adjusted.get("K", 0) * factors.get("k_factor", 1.0)
    adjusted["Ca"] = adjusted.get("Ca", 0) * factors.get("ca_factor", 1.0)
    adjusted["Mg"] = adjusted.get("Mg", 0) * factors.get("mg_factor", 1.0)
    adjusted["H2PO4"] = adjusted.get("H2PO4", 0) * factors.get("p_factor", 1.0)

    return adjusted


# ═══════════════════════════════════════════════════════════════════════
# STANDARD-WACHSTUMSPLÄNE (Literaturbasiert)
#
# Quellen: Sonneveld & Voogt (2009), de Kreij et al. (1997),
#          Proefstation Naaldwijk
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_GROWTH_PLANS: dict[str, GrowthPlan] = {}

# ── Tomate ──
DEFAULT_GROWTH_PLANS["Tomate – Standard"] = GrowthPlan(
    name="Tomate – Standard",
    crop="Tomate",
    base_recipe_name="Tomate (Hoagland modifiziert)",
    total_weeks=24,
    description="Klassischer 4-Phasen-Plan für Stabtomaten im Gewächshaus",
    source="Sonneveld & Voogt (2009), angepasst",
    phases=[
        GrowthPhase("Keimling/Jungpflanze", 0, 3,
                     n_factor=0.7, k_factor=0.6, ca_factor=0.9,
                     ec_target=1.5, nh4_ratio=0.08,
                     notes="Niedriger EC, mehr NH₄ für Wurzelwachstum"),
        GrowthPhase("Vegetativ", 4, 8,
                     n_factor=1.0, k_factor=0.8, ca_factor=1.0,
                     ec_target=2.2, nh4_ratio=0.05,
                     notes="N:K ≈ 2:1, starkes Blattwachstum"),
        GrowthPhase("Blüte/Fruchtansatz", 9, 14,
                     n_factor=0.9, k_factor=1.2, ca_factor=1.1,
                     ec_target=2.5, nh4_ratio=0.04,
                     notes="K steigt, Ca für Blütenendfäule-Prävention"),
        GrowthPhase("Fruchtreife/Ernte", 15, 24,
                     n_factor=0.8, k_factor=1.4, ca_factor=1.1,
                     ec_target=2.8, nh4_ratio=0.03,
                     notes="N:K ≈ 1:1.5, maximale Fruchtqualität"),
    ],
)

# ── Paprika ──
DEFAULT_GROWTH_PLANS["Paprika – Standard"] = GrowthPlan(
    name="Paprika – Standard",
    crop="Paprika",
    base_recipe_name="Paprika",
    total_weeks=20,
    description="Standard-Plan für Blockpaprika",
    source="de Kreij et al. (1997), angepasst",
    phases=[
        GrowthPhase("Jungpflanze", 0, 4,
                     n_factor=0.8, k_factor=0.7, ec_target=1.8, nh4_ratio=0.06,
                     notes="Moderate EC, langsamer Aufbau"),
        GrowthPhase("Vegetativ", 5, 9,
                     n_factor=1.0, k_factor=0.9, ec_target=2.2, nh4_ratio=0.05,
                     notes="Gleichmäßiges Wachstum"),
        GrowthPhase("Generativ", 10, 15,
                     n_factor=0.9, k_factor=1.2, ca_factor=1.1, ec_target=2.5,
                     notes="K-Betonung für Fruchtentwicklung"),
        GrowthPhase("Ernte", 16, 20,
                     n_factor=0.85, k_factor=1.3, ec_target=2.5,
                     notes="Stabile Versorgung während Dauerente"),
    ],
)

# ── Gurke ──
DEFAULT_GROWTH_PLANS["Gurke – Standard"] = GrowthPlan(
    name="Gurke – Standard",
    crop="Gurke",
    base_recipe_name="Gurke",
    total_weeks=16,
    description="Standard-Plan für Salatgurke im Gewächshaus",
    source="Proefstation Naaldwijk, angepasst",
    phases=[
        GrowthPhase("Jungpflanze", 0, 2,
                     n_factor=0.7, k_factor=0.6, ec_target=1.2, nh4_ratio=0.06,
                     notes="Gurke reagiert empfindlich auf hohe EC"),
        GrowthPhase("Vegetativ", 3, 6,
                     n_factor=1.0, k_factor=0.8, ec_target=1.8,
                     notes="Starkes Blattwachstum, moderate EC"),
        GrowthPhase("Fruchtbildung", 7, 12,
                     n_factor=0.9, k_factor=1.1, ca_factor=1.05, ec_target=2.0,
                     notes="K leicht erhöht für Fruchtqualität"),
        GrowthPhase("Dauernte", 13, 16,
                     n_factor=0.85, k_factor=1.2, ec_target=2.0,
                     notes="Gleichmäßig weiter, EC nicht zu hoch"),
    ],
)

# ── Salat ──
DEFAULT_GROWTH_PLANS["Salat – Standard"] = GrowthPlan(
    name="Salat – Standard",
    crop="Salat",
    base_recipe_name="Salat (Resh)",
    total_weeks=6,
    description="Kurze Kultur: Kopfsalat im NFT/DWC",
    source="Resh (2013), angepasst",
    phases=[
        GrowthPhase("Keimling", 0, 1,
                     n_factor=0.6, k_factor=0.5, ec_target=0.8,
                     notes="Sehr niedrige EC, empfindliche Jungpflanzen"),
        GrowthPhase("Wachstum", 2, 4,
                     n_factor=1.0, k_factor=0.9, ca_factor=1.1, ec_target=1.2,
                     notes="Ca betont gegen Tipburn"),
        GrowthPhase("Ernte", 5, 6,
                     n_factor=0.9, k_factor=1.0, ec_target=1.0,
                     notes="EC leicht senken für milden Geschmack"),
    ],
)

# ── Erdbeere ──
DEFAULT_GROWTH_PLANS["Erdbeere – Standard"] = GrowthPlan(
    name="Erdbeere – Standard",
    crop="Erdbeere",
    base_recipe_name="Hoagland & Arnon",
    total_weeks=20,
    description="Erdbeere in Substratkultur (Rinne/Container)",
    source="Praxiserfahrung NL/BE",
    phases=[
        GrowthPhase("Pflanzung", 0, 3,
                     n_factor=0.7, k_factor=0.6, ec_target=1.0,
                     notes="Sanfter Start, Fe-Chelat besonders wichtig"),
        GrowthPhase("Vegetativ", 4, 8,
                     n_factor=1.0, k_factor=0.8, ec_target=1.5,
                     notes="Blattrosette aufbauen"),
        GrowthPhase("Blüte", 9, 12,
                     n_factor=0.85, k_factor=1.2, ca_factor=1.1, ec_target=1.6,
                     notes="K und Ca für Fruchtansatz"),
        GrowthPhase("Fruchtreife", 13, 20,
                     n_factor=0.8, k_factor=1.4, ec_target=1.8,
                     notes="Hoher K für Geschmack und Farbe, EC moderat"),
    ],
)


def generate_weekly_schedule(plan: GrowthPlan, base_recipe_mg: dict[str, float]) -> list[dict]:
    """
    Generiert einen wöchentlichen Zeitplan mit angepassten Rezepten.

    Returns: Liste von dicts pro Woche mit:
        week, phase_name, factors, adjusted_recipe_mg, ec_target
    """
    schedule = []
    for week in range(plan.total_weeks + 1):
        factors = interpolate_week(plan, week)

        # Phase-Name finden
        phase_name = "Übergang"
        for phase in plan.phases:
            if phase.week_start <= week <= phase.week_end:
                phase_name = phase.name
                break

        adjusted = apply_phase_to_recipe(base_recipe_mg, factors)

        schedule.append({
            "week": week,
            "phase_name": phase_name,
            "factors": factors,
            "adjusted_mg": adjusted,
            "ec_target": factors.get("ec_target", 0),
        })

    return schedule
