"""
Pydantic-Modelle für Request / Response der NutrientMixer API.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════
# Ion
# ═══════════════════════════════════════════════════════════════════════

class IonOut(BaseModel):
    symbol: str
    display: str
    element: str
    molar_mass: float
    ion_molar_mass: float
    charge: int


# ═══════════════════════════════════════════════════════════════════════
# Rezepte
# ═══════════════════════════════════════════════════════════════════════

class RecipeIn(BaseModel):
    """Request: Rezept anlegen / aktualisieren."""
    name: str
    description: str = ""
    no3_n: float = 0.0
    nh4_n: float = 0.0
    p: float = 0.0
    k: float = 0.0
    ca: float = 0.0
    mg: float = 0.0
    s: float = 0.0
    fe: float = 0.0
    mn: float = 0.0
    zn: float = 0.0
    cu: float = 0.0
    b: float = 0.0
    mo: float = 0.0
    ph_min: float = 5.5
    ph_max: float = 6.5
    ec_target: float = 0.0
    suitable_plants: list[str] = []
    source: str = ""


class RecipeOut(RecipeIn):
    """Response: Rezept inkl. Metadaten."""
    is_custom: bool = False
    total_n: float = 0.0
    ions_mg: dict[str, float] = {}
    ions_mmol: dict[str, float] = {}


# ═══════════════════════════════════════════════════════════════════════
# Wasserprofile
# ═══════════════════════════════════════════════════════════════════════

class WaterProfileIn(BaseModel):
    name: str
    ca: float = 0.0
    mg: float = 0.0
    na: float = 0.0
    k: float = 0.0
    cl: float = 0.0
    so4: float = 0.0
    hco3: float = 0.0
    no3: float = 0.0
    fe: float = 0.0
    ec: float = 0.0
    ph: float = 7.0


class WaterProfileOut(WaterProfileIn):
    is_custom: bool = False


# ═══════════════════════════════════════════════════════════════════════
# Salze
# ═══════════════════════════════════════════════════════════════════════

class SaltOut(BaseModel):
    name: str
    formula: str
    molar_mass: float
    solubility_20: float
    tank: str
    ion_contribution: dict[str, float] = {}
    is_chelate: bool = False
    fe_content_pct: float = 0.0
    is_premix: bool = False
    premix_mg_per_g: dict[str, float] = {}
    notes: str = ""
    category: str = ""
    cost_per_kg: float = 0.0
    mg_ion_per_gram: dict[str, float] = {}


class SaltIn(BaseModel):
    name: str
    formula: str
    molar_mass: float
    solubility_20: float
    tank: str = "B"
    ion_contribution: dict[str, float] = {}
    notes: str = ""
    category: str = "macro"
    cost_per_kg: float = 0.0
    is_chelate: bool = False
    fe_content_pct: float = 0.0


# ═══════════════════════════════════════════════════════════════════════
# Hauptrechner (Solver)
# ═══════════════════════════════════════════════════════════════════════

class CalculateRequest(BaseModel):
    """Request an den Solver."""
    recipe_name: str
    water_profile_name: str = "Osmosewasser"
    volume_l: float = 1000.0
    concentrate_factor: float = 100.0
    fe_chelate: str = "Fe-DTPA"
    nh4_source: str = "NH4NO3"
    p_source: str = "KH2PO4"
    cl_target_mg: float = 0.0
    cl_source: str = "none"
    micro_source: str = "individual"
    dose_ratio: str = "1:1"


class SaltResultOut(BaseModel):
    salt_name: str
    salt_formula: str
    tank: str
    mmol_per_l: float
    g_per_l: float
    g_total: float
    g_concentrate: float
    cost_total: float = 0.0


class SolubilityCheckOut(BaseModel):
    salt_name: str
    formula: str
    tank: str
    g_per_l_concentrate: float
    solubility_limit: float
    saturation_pct: float
    is_ok: bool
    warning: str = ""


class RatioResultOut(BaseModel):
    name: str
    description: str
    actual: float
    target_min: float
    target_max: float
    is_ok: bool
    warning: str = ""
    unit: str = ":1"


class CalculateResponse(BaseModel):
    """Vollständiges Solver-Ergebnis."""
    # Salzmengen
    tank_a: list[SaltResultOut] = []
    tank_b: list[SaltResultOut] = []
    # Soll/Ist
    target_mg: dict[str, float] = {}
    adjusted_mg: dict[str, float] = {}
    achieved_mg: dict[str, float] = {}
    delta_mg: dict[str, float] = {}
    # Wasserabzug
    water_mg: dict[str, float] = {}
    water_warnings: list[str] = []
    # Löslichkeit
    solubility_checks: list[SolubilityCheckOut] = []
    max_concentrate_factor: float = 0.0
    tank_a_volume_l: float = 0.0
    tank_b_volume_l: float = 0.0
    # EC
    ec_simple: float = 0.0
    ec_ionic: float = 0.0
    ec_rating: str = ""
    # Verhältnisse
    ratios: list[RatioResultOut] = []
    # A/B Validierung
    ab_warnings: list[str] = []
    # Allgemein
    steps: list[str] = []
    warnings: list[str] = []
    # Kosten
    total_cost: float = 0.0
    cost_per_liter: float = 0.0
    # Dosierung
    dose_ratio_a: float = 1.0
    dose_ratio_b: float = 1.0


# ═══════════════════════════════════════════════════════════════════════
# pH-Korrektur
# ═══════════════════════════════════════════════════════════════════════

class PhCorrectionRequest(BaseModel):
    water_hco3_mg: float = 140.0
    water_ph: float = 7.4
    target_ph: float = 5.8
    volume_l: float = 1000.0
    acid_name: str = "HNO3"
    base_name: Optional[str] = None


class PhCorrectionResponse(BaseModel):
    acid_ml: float = 0.0
    acid_ml_per_l: float = 0.0
    acid_name: str = ""
    base_ml: float = 0.0
    base_ml_per_l: float = 0.0
    base_name: str = ""
    ion_changes_mg: dict[str, float] = {}
    steps: list[str] = []
    warnings: list[str] = []


# ═══════════════════════════════════════════════════════════════════════
# Verdünnung
# ═══════════════════════════════════════════════════════════════════════

class DilutionRequest(BaseModel):
    target_ec: float
    base_ec: float
    concentrate_factor: float = 100.0
    volume_l: float = 10.0
    water_ec: float = 0.0
    dose_ratio_a: float = 1.0
    dose_ratio_b: float = 1.0
    achieved_mg: dict[str, float] = {}


class DilutionResponse(BaseModel):
    dilution_factor: float = 0.0
    ml_a_per_liter: float = 0.0
    ml_b_per_liter: float = 0.0
    ml_a_total: float = 0.0
    ml_b_total: float = 0.0
    diluted_mg: dict[str, float] = {}
    achieved_ec: float = 0.0
    warnings: list[str] = []


# ═══════════════════════════════════════════════════════════════════════
# Rückwärtsrechner
# ═══════════════════════════════════════════════════════════════════════

class ReverseSaltInput(BaseModel):
    salt_formula: str
    grams: float
    tank: str = ""


class ReverseRequest(BaseModel):
    salts: list[ReverseSaltInput]
    volume_l: float = 1000.0


class ReverseResponse(BaseModel):
    ion_mg: dict[str, float] = {}
    ion_mmol: dict[str, float] = {}
    ec_estimated: float = 0.0
    ratios: list[RatioResultOut] = []
    closest_recipe: Optional[str] = None
    warnings: list[str] = []


# ═══════════════════════════════════════════════════════════════════════
# Kompatibilität
# ═══════════════════════════════════════════════════════════════════════

class CompatibilityRequest(BaseModel):
    salt_formulas: list[str]


class CompatibilityIssue(BaseModel):
    salt_a: str
    salt_b: str
    severity: str
    precipitate: str
    description: str


class CompatibilityResponse(BaseModel):
    is_compatible: bool = True
    issues: list[CompatibilityIssue] = []


# ═══════════════════════════════════════════════════════════════════════
# Wachstumsphasen
# ═══════════════════════════════════════════════════════════════════════

class GrowthPhaseOut(BaseModel):
    name: str
    week_start: int
    week_end: int
    n_factor: float = 1.0
    k_factor: float = 1.0
    ca_factor: float = 1.0
    mg_factor: float = 1.0
    p_factor: float = 1.0
    ec_target: float = 0.0
    nh4_ratio: float = 0.05
    notes: str = ""


class GrowthPlanOut(BaseModel):
    name: str
    description: str = ""
    base_recipe_name: str = ""
    phases: list[GrowthPhaseOut] = []


# ═══════════════════════════════════════════════════════════════════════
# Pflanzen
# ═══════════════════════════════════════════════════════════════════════

class PlantOut(BaseModel):
    name: str
    category: str = ""
    ec_min: float = 0.0
    ec_max: float = 0.0
    ph_min: float = 0.0
    ph_max: float = 0.0
    notes: str = ""
    keywords: list[str] = []


class PlantIn(BaseModel):
    name: str
    category: str = ""
    ec_min: float = 0.0
    ec_max: float = 0.0
    ph_min: float = 5.5
    ph_max: float = 6.5
    notes: str = ""
    keywords: list[str] = []


# ═══════════════════════════════════════════════════════════════════════
# Salzkosten
# ═══════════════════════════════════════════════════════════════════════

class SaltCostsIn(BaseModel):
    """Map: formula -> EUR/kg."""
    costs: dict[str, float]


# ═══════════════════════════════════════════════════════════════════════
# Einstellungen
# ═══════════════════════════════════════════════════════════════════════

class SettingsModel(BaseModel):
    default_unit: str = "mg/L (ppm)"
    default_concentrate_factor: int = 100
    default_volume: int = 1000
    ec_method: str = "ionic"
    fe_chelate: str = "Fe-DTPA"
    nh4_source: str = "NH4NO3"
    p_source: str = "KH2PO4"
    micro_source: str = "individual"
    dose_ratio: str = "1:1"
    language: str = "de"
