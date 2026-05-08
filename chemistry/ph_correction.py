"""
pH-Korrektur-Rechner: Berechnet Säure-/Basenbedarf zur pH-Einstellung.

Basiert auf der Neutralisation von Hydrogencarbonat (HCO₃⁻) im Rohwasser.
HCO₃⁻ + H⁺ → CO₂ + H₂O

Säuren: HNO₃ (liefert NO₃⁻), H₃PO₄ (liefert H₂PO₄⁻), H₂SO₄ (liefert SO₄²⁻)
Basen:  KOH (liefert K⁺), K₂CO₃ (liefert K⁺)
"""

from dataclasses import dataclass, field
from chemistry.ions import ION_BY_SYMBOL, mg_to_mmol, mmol_to_mg
from ui.locales import t, warn_fmt, salt_name


@dataclass
class AcidBase:
    """Eine Säure oder Base zur pH-Korrektur."""
    name: str
    formula: str
    molar_mass: float
    concentration_pct: float   # Handelskonzentration in %
    density: float             # Dichte der Handelslösung in g/mL
    h_equivalents: int         # H⁺-Äquivalente pro mol (Säure: positiv, Base: negativ)
    ion_contribution: dict[str, float] = field(default_factory=dict)
    notes: str = ""

    def ml_per_mmol_h(self) -> float:
        """mL Handelslösung pro mmol H⁺ (bzw. OH⁻ bei Basen)."""
        # g rein pro mL Lösung
        g_per_ml = self.density * self.concentration_pct / 100.0
        # mmol pro mL
        mmol_per_ml = g_per_ml / self.molar_mass * 1000.0 * abs(self.h_equivalents)
        return 1.0 / mmol_per_ml if mmol_per_ml > 0 else 0.0


# Standard-Säuren und -Basen
ACIDS = {
    "HNO3_65": AcidBase(
        name=t("b.acid.hno3_65"), formula="HNO₃", molar_mass=63.01,
        concentration_pct=65.0, density=1.39, h_equivalents=1,
        ion_contribution={"NO3": 1.0},
        notes="Liefert NO₃, senkt pH",
    ),
    "HNO3_38": AcidBase(
        name=t("b.acid.hno3_38"), formula="HNO₃", molar_mass=63.01,
        concentration_pct=38.0, density=1.23, h_equivalents=1,
        ion_contribution={"NO3": 1.0},
    ),
    "H3PO4_85": AcidBase(
        name=t("b.acid.h3po4"), formula="H₃PO₄", molar_mass=98.00,
        concentration_pct=85.0, density=1.685, h_equivalents=1,
        ion_contribution={"H2PO4": 1.0},
        notes="Liefert P, senkt pH. Nur 1. Dissoziationsstufe relevant",
    ),
    "H2SO4_96": AcidBase(
        name=t("b.acid.h2so4_96"), formula="H₂SO₄", molar_mass=98.079,
        concentration_pct=96.0, density=1.84, h_equivalents=2,
        ion_contribution={"SO4": 1.0},
        notes="Liefert SO₄, senkt pH stark. Vorsicht: stark ätzend!",
    ),
    "H2SO4_37": AcidBase(
        name=t("b.acid.h2so4_37"), formula="H₂SO₄", molar_mass=98.079,
        concentration_pct=37.0, density=1.28, h_equivalents=2,
        ion_contribution={"SO4": 1.0},
    ),
}

BASES = {
    "KOH": AcidBase(
        name=t("b.base.koh"), formula="KOH", molar_mass=56.11,
        concentration_pct=100.0, density=2.12, h_equivalents=-1,
        ion_contribution={"K": 1.0},
        notes="Liefert K⁺, hebt pH",
    ),
    "K2CO3": AcidBase(
        name=t("b.base.k2co3"), formula="K₂CO₃", molar_mass=138.21,
        concentration_pct=100.0, density=2.43, h_equivalents=-2,
        ion_contribution={"K": 2.0},
        notes="Liefert 2× K⁺, hebt pH. 1 mol neutralisiert 2 mol H⁺",
    ),
    "NaOH": AcidBase(
        name=t("b.base.naoh"), formula="NaOH", molar_mass=40.00,
        concentration_pct=100.0, density=2.13, h_equivalents=-1,
        ion_contribution={"Na": 1.0},
        notes=t("b.base.naoh_note"),
    ),
}


@dataclass
class PhCorrectionResult:
    """Ergebnis einer pH-Korrektur-Berechnung."""
    acid_or_base: AcidBase
    direction: str                  # "down" oder "up"
    hco3_initial_mg: float          # HCO₃ im Rohwasser (mg/L)
    hco3_target_mg: float           # HCO₃ nach Korrektur
    h_mmol_needed: float            # mmol H⁺ (oder OH⁻) pro Liter
    ml_per_liter: float             # mL Säure/Base pro Liter Endlösung
    ml_per_volume: float            # mL für Gesamtvolumen
    g_per_liter: float              # g (bei Feststoffen)
    g_per_volume: float
    ion_additions: dict[str, float] # Zusätzliche Ionen (mg/L)
    warnings: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)


def calculate_ph_correction(
    hco3_mg: float,
    target_ph: float,
    water_ph: float,
    volume_l: float,
    acid_key: str = "HNO3_65",
    base_key: str = "KOH",
) -> PhCorrectionResult:
    """
    Berechnet den Säure-/Basenbedarf zur pH-Korrektur.

    Prinzip: HCO₃⁻ puffert den pH. Um den pH zu senken, muss HCO₃⁻
    neutralisiert werden. Ziel: ~0.5–1.0 mmol/L Rest-HCO₃⁻ (ca. 30–60 mg/L)
    für pH-Stabilität.

    Args:
        hco3_mg: HCO₃⁻ im Rohwasser in mg/L
        target_ph: Ziel-pH der Nährlösung
        water_ph: pH des Rohwassers
        volume_l: Volumen in Litern
        acid_key: Schlüssel aus ACIDS dict
        base_key: Schlüssel aus BASES dict
    """
    warnings = []
    steps = []

    hco3_ion = ION_BY_SYMBOL.get("HCO3")
    if not hco3_ion:
        # Fallback Molmasse HCO₃⁻
        hco3_mm = 61.02
    else:
        hco3_mm = hco3_ion.molar_mass

    hco3_mmol = hco3_mg / hco3_mm
    steps.append(warn_fmt("b.ph_hco3_in_water", hco3_mg, hco3_mmol))

    if target_ph < water_ph:
        # ── pH SENKEN ──
        # Ziel-Rest-HCO₃: genug für pH-Pufferung
        # Bei pH 5.5 → fast alles HCO₃ neutralisiert, ~0.5 mmol/L Rest
        # Bei pH 6.0 → ~1.0 mmol/L Rest
        # Bei pH 6.5 → ~1.5 mmol/L Rest
        if target_ph <= 5.5:
            target_hco3_mmol = 0.3
        elif target_ph <= 6.0:
            target_hco3_mmol = 0.8
        elif target_ph <= 6.5:
            target_hco3_mmol = 1.2
        else:
            target_hco3_mmol = 1.5

        target_hco3_mg = target_hco3_mmol * hco3_mm

        h_needed = max(0, hco3_mmol - target_hco3_mmol)
        steps.append(f"Ziel-Rest-HCO₃: {target_hco3_mmol:.1f} mmol/L ({target_hco3_mg:.0f} mg/L)")
        steps.append(f"Zu neutralisieren: {h_needed:.2f} mmol/L HCO₃⁻")

        acid = ACIDS.get(acid_key)
        if not acid:
            acid = ACIDS["HNO3_65"]

        ml_per_mmol = acid.ml_per_mmol_h()
        ml_per_l = h_needed * ml_per_mmol
        ml_total = ml_per_l * volume_l

        # Bei Feststoffen: g statt mL
        if acid.concentration_pct >= 99:
            g_per_l = h_needed * acid.molar_mass / (1000.0 * abs(acid.h_equivalents))
            g_total = g_per_l * volume_l
        else:
            g_per_l = ml_per_l * acid.density
            g_total = g_per_l * volume_l

        steps.append(f"{t('b.ph_acid_label')} {acid.name}")
        steps.append(warn_fmt("b.ph_need_ml", ml_per_l, ml_total, volume_l))

        # Ionen-Beitrag
        ion_adds = {}
        for ion_sym, stoich in acid.ion_contribution.items():
            ion = ION_BY_SYMBOL.get(ion_sym)
            if ion:
                mmol_ion = h_needed * stoich / abs(acid.h_equivalents)
                mg_ion = mmol_ion * ion.molar_mass
                ion_adds[ion_sym] = mg_ion
                steps.append(f"  → {t('b.delivers')} {ion.display}: {mg_ion:.1f} mg/L ({mmol_ion:.2f} mmol/L)")

        if h_needed <= 0:
            warnings.append(t("b.ph_no_hco3"))
        if h_needed > 5:
            warnings.append(warn_fmt("b.ph_high_acid", h_needed))

        return PhCorrectionResult(
            acid_or_base=acid, direction="down",
            hco3_initial_mg=hco3_mg, hco3_target_mg=target_hco3_mg,
            h_mmol_needed=h_needed,
            ml_per_liter=ml_per_l, ml_per_volume=ml_total,
            g_per_liter=g_per_l, g_per_volume=g_total,
            ion_additions=ion_adds, warnings=warnings, steps=steps,
        )
    else:
        # ── pH HEBEN ──
        base = BASES.get(base_key)
        if not base:
            base = BASES["KOH"]

        # Grobe Schätzung: 0.5–2 mmol/L OH⁻ typisch
        oh_needed = (target_ph - water_ph) * 0.8  # Vereinfachung
        oh_needed = max(0.1, min(oh_needed, 5.0))

        steps.append(f"pH heben von {water_ph:.1f} auf {target_ph:.1f}")
        steps.append(warn_fmt("b.ph_oh_estimate", oh_needed))

        if base.concentration_pct >= 99:
            g_per_l = oh_needed * base.molar_mass / (1000.0 * abs(base.h_equivalents))
            g_total = g_per_l * volume_l
            ml_per_l = g_per_l / base.density
            ml_total = ml_per_l * volume_l
        else:
            ml_per_mmol = base.ml_per_mmol_h()
            ml_per_l = oh_needed * ml_per_mmol
            ml_total = ml_per_l * volume_l
            g_per_l = ml_per_l * base.density
            g_total = g_per_l * volume_l

        steps.append(f"Base: {base.name}")
        steps.append(warn_fmt("b.ph_need_g", g_per_l, g_total, volume_l))

        ion_adds = {}
        for ion_sym, stoich in base.ion_contribution.items():
            ion = ION_BY_SYMBOL.get(ion_sym)
            if ion:
                mmol_ion = oh_needed * stoich / abs(base.h_equivalents)
                mg_ion = mmol_ion * ion.molar_mass
                ion_adds[ion_sym] = mg_ion
                steps.append(f"  → {t('b.delivers')} {ion.display}: {mg_ion:.1f} mg/L")

        warnings.append("pH-Hebung ist eine Schätzung – Titration empfohlen!")

        return PhCorrectionResult(
            acid_or_base=base, direction="up",
            hco3_initial_mg=hco3_mg, hco3_target_mg=hco3_mg,
            h_mmol_needed=oh_needed,
            ml_per_liter=ml_per_l, ml_per_volume=ml_total,
            g_per_liter=g_per_l, g_per_volume=g_total,
            ion_additions=ion_adds, warnings=warnings, steps=steps,
        )
