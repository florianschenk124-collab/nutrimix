"""
Standard-Rezepte für Nährlösungen.

Alle Konzentrationen als Ziel-Ionenkonzentrationen in mg/L (Elementbezug).
Intern wird zu mmol/L konvertiert für Berechnungen.
"""

from dataclasses import dataclass, field


@dataclass
class NutrientRecipe:
    """Ein Nährlösungs-Rezept mit Ziel-Ionenkonzentrationen."""
    name: str
    description: str
    # Makronährstoffe in mg/L (Elementbezug)
    # NO3-N und NH4-N getrennt angegeben
    no3_n: float = 0.0    # Nitrat-Stickstoff (mg/L als N)
    nh4_n: float = 0.0    # Ammonium-Stickstoff (mg/L als N)
    p: float = 0.0        # Phosphor (mg/L als P)
    k: float = 0.0        # Kalium (mg/L als K)
    ca: float = 0.0       # Calcium (mg/L als Ca)
    mg: float = 0.0       # Magnesium (mg/L als Mg)
    s: float = 0.0        # Schwefel (mg/L als S)
    # Mikronährstoffe in mg/L (Elementbezug)
    fe: float = 0.0       # Eisen
    mn: float = 0.0       # Mangan
    zn: float = 0.0       # Zink
    cu: float = 0.0       # Kupfer
    b: float = 0.0        # Bor
    mo: float = 0.0       # Molybdän
    # Metadaten
    ph_min: float = 5.5
    ph_max: float = 6.5
    ec_target: float = 0.0   # Ziel-EC in mS/cm (0 = nicht definiert)
    suitable_plants: list[str] = field(default_factory=list)
    source: str = ""          # Literaturquelle
    is_custom: bool = False

    @property
    def total_n(self) -> float:
        """Gesamt-Stickstoff in mg/L."""
        return self.no3_n + self.nh4_n

    def as_mg_dict(self) -> dict[str, float]:
        """Gibt alle Ionenkonzentrationen als Dict in mg/L zurück."""
        return {
            "NO3": self.no3_n,
            "NH4": self.nh4_n,
            "H2PO4": self.p,
            "K": self.k,
            "Ca": self.ca,
            "Mg": self.mg,
            "SO4": self.s,
            "Fe": self.fe,
            "Mn": self.mn,
            "Zn": self.zn,
            "Cu": self.cu,
            "B": self.b,
            "Mo": self.mo,
        }

    def as_mmol_dict(self) -> dict[str, float]:
        """Konvertiert zu mmol/L (Elementbezug → mmol)."""
        from chemistry.ions import ION_BY_SYMBOL, mg_to_mmol
        result = {}
        for ion_sym, mg_val in self.as_mg_dict().items():
            ion = ION_BY_SYMBOL[ion_sym]
            result[ion_sym] = mg_to_mmol(mg_val, ion)
        return result


# ═══════════════════════════════════════════════════════════════════════
# Standard-Rezepte
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_RECIPES: dict[str, NutrientRecipe] = {}

def _register(recipe: NutrientRecipe) -> NutrientRecipe:
    DEFAULT_RECIPES[recipe.name] = recipe
    return recipe


# ─── Hoagland & Arnon (1950) ─────────────────────────────────────────

_register(NutrientRecipe(
    name="Hoagland & Arnon",
    description="Klassisches Universalrezept (volle Stärke)",
    no3_n=196.0, nh4_n=14.0,
    p=31.0, k=235.0, ca=200.0, mg=48.0, s=64.0,
    fe=2.5, mn=0.5, zn=0.05, cu=0.02, b=0.5, mo=0.01,
    ph_min=5.5, ph_max=6.5, ec_target=2.0,
    suitable_plants=["Universell", "Tomate", "Paprika", "Gurke", "Salat"],
    source="Hoagland & Arnon, 1950",
))

# ─── Modified Hoagland (½ Stärke) ───────────────────────────────────

_register(NutrientRecipe(
    name="Modified Hoagland (½)",
    description="Halbe Konzentration – für empfindliche Kulturen",
    no3_n=98.0, nh4_n=7.0,
    p=15.5, k=117.5, ca=100.0, mg=24.0, s=32.0,
    fe=1.25, mn=0.25, zn=0.025, cu=0.01, b=0.25, mo=0.005,
    ph_min=5.5, ph_max=6.5, ec_target=1.0,
    suitable_plants=["Salat", "Kräuter", "Jungpflanzen", "Erdbeere"],
    source="nach Hoagland & Arnon, modifiziert",
))

# ─── Steiner Universal ──────────────────────────────────────────────

_register(NutrientRecipe(
    name="Steiner Universal",
    description="Ausgewogenes Ionenverhältnis nach Steiner (1961)",
    no3_n=168.0, nh4_n=0.0,
    p=39.0, k=273.0, ca=180.0, mg=48.0, s=336.0,
    fe=2.8, mn=0.55, zn=0.33, cu=0.05, b=0.28, mo=0.05,
    ph_min=5.5, ph_max=6.5, ec_target=2.2,
    suitable_plants=["Universell", "Tomate", "Paprika"],
    source="Steiner, 1961",
))

# ─── Cooper (NFT) ───────────────────────────────────────────────────

_register(NutrientRecipe(
    name="Cooper (NFT)",
    description="Optimiert für Nutrient Film Technique",
    no3_n=168.0, nh4_n=0.0,
    p=41.0, k=300.0, ca=170.0, mg=50.0, s=68.0,
    fe=12.0, mn=2.0, zn=0.1, cu=0.1, b=0.3, mo=0.2,
    ph_min=5.5, ph_max=6.5, ec_target=2.0,
    suitable_plants=["Salat", "Kräuter", "NFT-Systeme"],
    source="Cooper, 1979",
))

# ─── Sonneveld Tomate ───────────────────────────────────────────────

_register(NutrientRecipe(
    name="Sonneveld – Tomate",
    description="Spezialrezept für Tomatenkultur nach Sonneveld",
    no3_n=168.0, nh4_n=18.0,
    p=39.0, k=312.0, ca=180.0, mg=36.0, s=120.0,
    fe=0.84, mn=0.55, zn=0.33, cu=0.05, b=0.28, mo=0.05,
    ph_min=5.5, ph_max=6.0, ec_target=2.5,
    suitable_plants=["Tomate"],
    source="Sonneveld & Straver, 1994",
))

# ─── Sonneveld Gurke ────────────────────────────────────────────────

_register(NutrientRecipe(
    name="Sonneveld – Gurke",
    description="Spezialrezept für Gurkenkultur nach Sonneveld",
    no3_n=182.0, nh4_n=14.0,
    p=31.0, k=312.0, ca=160.0, mg=24.0, s=48.0,
    fe=0.84, mn=0.55, zn=0.33, cu=0.05, b=0.28, mo=0.05,
    ph_min=5.5, ph_max=6.0, ec_target=2.0,
    suitable_plants=["Gurke"],
    source="Sonneveld & Straver, 1994",
))

# ─── Sonneveld Paprika ──────────────────────────────────────────────

_register(NutrientRecipe(
    name="Sonneveld – Paprika",
    description="Spezialrezept für Paprikakultur nach Sonneveld",
    no3_n=168.0, nh4_n=14.0,
    p=31.0, k=273.0, ca=170.0, mg=28.0, s=80.0,
    fe=0.84, mn=0.55, zn=0.33, cu=0.05, b=0.28, mo=0.05,
    ph_min=5.5, ph_max=6.0, ec_target=2.2,
    suitable_plants=["Paprika", "Chili"],
    source="Sonneveld & Straver, 1994",
))

# ─── Sonneveld Salat ────────────────────────────────────────────────

_register(NutrientRecipe(
    name="Sonneveld – Salat",
    description="Niedrige Konzentration für Blattgemüse",
    no3_n=154.0, nh4_n=14.0,
    p=31.0, k=210.0, ca=150.0, mg=24.0, s=48.0,
    fe=0.84, mn=0.55, zn=0.33, cu=0.05, b=0.28, mo=0.05,
    ph_min=5.5, ph_max=6.5, ec_target=1.2,
    suitable_plants=["Salat", "Spinat", "Blattgemüse"],
    source="Sonneveld & Straver, 1994",
))

# ─── Hewitt Long Ashton ─────────────────────────────────────────────

_register(NutrientRecipe(
    name="Hewitt (Long Ashton)",
    description="Forschungsrezept, University of Bristol",
    no3_n=168.0, nh4_n=0.0,
    p=41.0, k=156.0, ca=160.0, mg=36.0, s=48.0,
    fe=5.6, mn=1.1, zn=0.065, cu=0.064, b=0.5, mo=0.048,
    ph_min=5.5, ph_max=6.5, ec_target=1.8,
    suitable_plants=["Forschung", "Universell"],
    source="Hewitt, 1966",
))


# ═══════════════════════════════════════════════════════════════════════
# Hilfsfunktionen
# ═══════════════════════════════════════════════════════════════════════

def get_recipe_names() -> list[str]:
    """Gibt alle Rezeptnamen zurück."""
    return list(DEFAULT_RECIPES.keys())

def get_recipe(name: str) -> NutrientRecipe | None:
    """Sucht ein Rezept nach Name."""
    return DEFAULT_RECIPES.get(name)

def get_recipes_for_plant(plant: str) -> list[NutrientRecipe]:
    """Gibt alle Rezepte zurück, die für eine Pflanze geeignet sind."""
    plant_lower = plant.lower()
    return [
        r for r in DEFAULT_RECIPES.values()
        if any(plant_lower in p.lower() for p in r.suitable_plants)
    ]
