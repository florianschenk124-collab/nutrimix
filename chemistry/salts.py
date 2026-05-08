"""
Salz-Datenbank: Alle gängigen Düngesalze mit ihren Eigenschaften.

Erweitert mit:
- Zusätzliche Hauptelement-Salze (verschiedene N/K/Ca/Mg/P/S-Quellen)
- Handelsübliche Mikronährstoff-Premixe (Ferty 10S, Rexolin, Tenso, etc.)
- Kostenfelder (Preis pro kg)
"""

from dataclasses import dataclass, field
from chemistry.ions import Ion, ION_BY_SYMBOL
import chemistry.ions as ions


@dataclass
class Salt:
    """Ein Düngesalz mit chemischen Eigenschaften."""
    name: str
    formula: str
    molar_mass: float                # g/mol (inkl. Kristallwasser)
    solubility_20: float             # Löslichkeit bei 20°C in g/L
    tank: str                        # "A", "B", oder "AB"
    ion_contribution: dict[str, float] = field(default_factory=dict)
    is_chelate: bool = False
    fe_content_pct: float = 0.0
    is_premix: bool = False          # Mikronährstoff-Premix
    # Premix: mg Element pro g Premix (statt stöchiometrisch)
    premix_mg_per_g: dict[str, float] = field(default_factory=dict)
    notes: str = ""
    category: str = ""               # "macro", "micro", "chelate", "premix"
    cost_per_kg: float = 0.0         # EUR/kg (0 = nicht eingetragen)

    def ions_per_gram(self) -> dict[str, float]:
        if self.is_premix:
            # Premix: mg/g → mmol/g
            result = {}
            for ion_sym, mg in self.premix_mg_per_g.items():
                ion = ION_BY_SYMBOL.get(ion_sym)
                if ion:
                    result[ion_sym] = mg / ion.molar_mass
            return result
        mmol_per_g = 1000.0 / self.molar_mass
        return {
            ion_sym: mmol_per_g * stoich
            for ion_sym, stoich in self.ion_contribution.items()
        }

    def mg_ion_per_gram(self) -> dict[str, float]:
        if self.is_premix:
            return dict(self.premix_mg_per_g)
        result = {}
        for ion_sym, mmol in self.ions_per_gram().items():
            ion = ION_BY_SYMBOL[ion_sym]
            result[ion_sym] = mmol * ion.molar_mass
        return result

    def grams_for_mmol(self, target_ion: str, target_mmol: float) -> float:
        stoich = self.ion_contribution.get(target_ion, 0)
        if stoich == 0:
            raise ValueError(f"Salz {self.name} enthält kein {target_ion}")
        mmol_salt = target_mmol / stoich
        return mmol_salt * self.molar_mass / 1000.0

    def cost_per_gram(self) -> float:
        if self.cost_per_kg > 0:
            return self.cost_per_kg / 1000.0
        return 0.0


# ═══════════════════════════════════════════════════════════════════════
DEFAULT_SALTS: dict[str, Salt] = {}

def _register(salt: Salt) -> Salt:
    DEFAULT_SALTS[salt.formula] = salt
    return salt


# ═══════════════════════════════════════════════════════════════════════
# MAKRO-SALZE: STICKSTOFF-QUELLEN
# ═══════════════════════════════════════════════════════════════════════

CALCIUM_NITRATE = _register(Salt(
    name="Calciumnitrat-Tetrahydrat",
    formula="Ca(NO3)2·4H2O",
    molar_mass=236.15, solubility_20=1290.0, tank="A",
    ion_contribution={"Ca": 1.0, "NO3": 2.0},
    category="macro",
))

CALCIUM_NITRATE_ANHYDROUS = _register(Salt(
    name="Calciumnitrat (wasserfrei)",
    formula="Ca(NO3)2",
    molar_mass=164.09, solubility_20=1440.0, tank="A",
    ion_contribution={"Ca": 1.0, "NO3": 2.0},
    category="macro",
))

POTASSIUM_NITRATE = _register(Salt(
    name="Kaliumnitrat",
    formula="KNO3",
    molar_mass=101.103, solubility_20=316.0, tank="AB",
    ion_contribution={"K": 1.0, "NO3": 1.0},
    category="macro",
))

AMMONIUM_NITRATE = _register(Salt(
    name="Ammoniumnitrat",
    formula="NH4NO3",
    molar_mass=80.043, solubility_20=1183.0, tank="AB",
    ion_contribution={"NH4": 1.0, "NO3": 1.0},
    category="macro",
))

MAGNESIUM_NITRATE = _register(Salt(
    name="Magnesiumnitrat-Hexahydrat",
    formula="Mg(NO3)2·6H2O",
    molar_mass=256.41, solubility_20=420.0, tank="A",
    ion_contribution={"Mg": 1.0, "NO3": 2.0},
    category="macro",
))

UREA = _register(Salt(
    name="Harnstoff",
    formula="CO(NH2)2",
    molar_mass=60.06, solubility_20=1080.0, tank="AB",
    ion_contribution={"NH4": 2.0},  # Vereinfacht: Urea → 2 NH₄⁺ nach Umwandlung
    category="macro",
    notes="Wird mikrobiell zu NH₄⁺ umgewandelt, nicht sofort verfügbar",
))

AMMONIUM_SULFATE = _register(Salt(
    name="Ammoniumsulfat",
    formula="(NH4)2SO4",
    molar_mass=132.14, solubility_20=754.0, tank="B",
    ion_contribution={"NH4": 2.0, "SO4": 1.0},
    category="macro",
))

# ═══════════════════════════════════════════════════════════════════════
# MAKRO-SALZE: PHOSPHOR-QUELLEN
# ═══════════════════════════════════════════════════════════════════════

POTASSIUM_DIHYDROGEN_PHOSPHATE = _register(Salt(
    name="Kaliumdihydrogenphosphat",
    formula="KH2PO4",
    molar_mass=136.086, solubility_20=222.0, tank="B",
    ion_contribution={"K": 1.0, "H2PO4": 1.0},
    category="macro",
))
MONOPOTASSIUM_PHOSPHATE = POTASSIUM_DIHYDROGEN_PHOSPHATE

MAP = _register(Salt(
    name="Monoammoniumphosphat (MAP)",
    formula="NH4H2PO4",
    molar_mass=115.03, solubility_20=370.0, tank="B",
    ion_contribution={"NH4": 1.0, "H2PO4": 1.0},
    category="macro",
    notes="Liefert NH₄ + P gleichzeitig",
))

DAP = _register(Salt(
    name="Diammoniumphosphat (DAP)",
    formula="(NH4)2HPO4",
    molar_mass=132.06, solubility_20=588.0, tank="B",
    ion_contribution={"NH4": 2.0, "H2PO4": 1.0},
    category="macro",
    notes="Liefert 2× NH₄ + P, pH-hebend",
))

PHOSPHORIC_ACID = _register(Salt(
    name="Phosphorsäure (85%)",
    formula="H3PO4",
    molar_mass=98.00, solubility_20=5480.0, tank="B",
    ion_contribution={"H2PO4": 1.0},
    category="macro",
    notes="Reine P-Quelle, pH-senkend",
))

DIPOTASSIUM_PHOSPHATE = _register(Salt(
    name="Dikaliumhydrogenphosphat",
    formula="K2HPO4",
    molar_mass=174.18, solubility_20=1490.0, tank="B",
    ion_contribution={"K": 2.0, "H2PO4": 1.0},
    category="macro",
    notes="Liefert 2× K + P, pH-hebend",
))

# ═══════════════════════════════════════════════════════════════════════
# MAKRO-SALZE: KALIUM-QUELLEN
# ═══════════════════════════════════════════════════════════════════════

POTASSIUM_SULFATE = _register(Salt(
    name="Kaliumsulfat",
    formula="K2SO4",
    molar_mass=174.259, solubility_20=111.0, tank="B",
    ion_contribution={"K": 2.0, "SO4": 1.0},
    category="macro",
))

POTASSIUM_CHLORIDE = _register(Salt(
    name="Kaliumchlorid",
    formula="KCl",
    molar_mass=74.551, solubility_20=344.0, tank="B",
    ion_contribution={"K": 1.0, "Cl": 1.0},
    category="macro",
))

POTASSIUM_CARBONATE = _register(Salt(
    name="Kaliumcarbonat (Pottasche)",
    formula="K2CO3",
    molar_mass=138.21, solubility_20=1120.0, tank="B",
    ion_contribution={"K": 2.0},
    category="macro",
    notes="pH-hebend, CO₃ reagiert mit Säure",
))

POTASSIUM_HYDROXIDE = _register(Salt(
    name="Kaliumhydroxid",
    formula="KOH",
    molar_mass=56.11, solubility_20=1210.0, tank="B",
    ion_contribution={"K": 1.0},
    category="macro",
    notes="Stark basisch, pH-Korrektur",
))

# ═══════════════════════════════════════════════════════════════════════
# MAKRO-SALZE: CALCIUM-QUELLEN
# ═══════════════════════════════════════════════════════════════════════

CALCIUM_CHLORIDE = _register(Salt(
    name="Calciumchlorid-Dihydrat",
    formula="CaCl2·2H2O",
    molar_mass=147.015, solubility_20=745.0, tank="A",
    ion_contribution={"Ca": 1.0, "Cl": 2.0},
    category="macro",
))

CALCIUM_SULFATE = _register(Salt(
    name="Calciumsulfat-Dihydrat (Gips)",
    formula="CaSO4·2H2O",
    molar_mass=172.17, solubility_20=2.4, tank="A",
    ion_contribution={"Ca": 1.0, "SO4": 1.0},
    category="macro",
    notes="Sehr schlecht löslich – nur für geringe Mengen",
))

# ═══════════════════════════════════════════════════════════════════════
# MAKRO-SALZE: MAGNESIUM-QUELLEN
# ═══════════════════════════════════════════════════════════════════════

MAGNESIUM_SULFATE = _register(Salt(
    name="Magnesiumsulfat-Heptahydrat",
    formula="MgSO4·7H2O",
    molar_mass=246.475, solubility_20=356.0, tank="B",
    ion_contribution={"Mg": 1.0, "SO4": 1.0},
    category="macro",
))

MAGNESIUM_SULFATE_ANHYDROUS = _register(Salt(
    name="Magnesiumsulfat (wasserfrei)",
    formula="MgSO4",
    molar_mass=120.37, solubility_20=357.0, tank="B",
    ion_contribution={"Mg": 1.0, "SO4": 1.0},
    category="macro",
))

MAGNESIUM_CHLORIDE = _register(Salt(
    name="Magnesiumchlorid-Hexahydrat",
    formula="MgCl2·6H2O",
    molar_mass=203.30, solubility_20=543.0, tank="B",
    ion_contribution={"Mg": 1.0, "Cl": 2.0},
    category="macro",
))

# ═══════════════════════════════════════════════════════════════════════
# MAKRO-SALZE: SCHWEFEL-QUELLEN
# ═══════════════════════════════════════════════════════════════════════

SULFURIC_ACID = _register(Salt(
    name="Schwefelsäure (konz.)",
    formula="H2SO4",
    molar_mass=98.079, solubility_20=9999.0, tank="B",
    ion_contribution={"SO4": 1.0},
    category="macro",
    notes="pH-Korrektur, Vorsicht: stark ätzend!",
))

# ═══════════════════════════════════════════════════════════════════════
# SÄUREN FÜR PH-KORREKTUR
# ═══════════════════════════════════════════════════════════════════════

NITRIC_ACID = _register(Salt(
    name="Salpetersäure (65%)",
    formula="HNO3",
    molar_mass=63.01, solubility_20=9999.0, tank="A",
    ion_contribution={"NO3": 1.0},
    category="macro",
    notes="pH-Korrektur + NO₃-Quelle",
))

# ═══════════════════════════════════════════════════════════════════════
# EISEN-CHELATE
# ═══════════════════════════════════════════════════════════════════════

FE_DTPA = _register(Salt(
    name="Eisen-DTPA (11% Fe)",
    formula="Fe-DTPA",
    molar_mass=468.20, solubility_20=80.0, tank="A",
    ion_contribution={"Fe": 1.0},
    is_chelate=True, fe_content_pct=11.0,
    category="chelate",
    notes="Stabil pH 3–6.5",
))

FE_EDDHA = _register(Salt(
    name="Eisen-EDDHA (6% Fe)",
    formula="Fe-EDDHA",
    molar_mass=932.0, solubility_20=30.0, tank="A",
    ion_contribution={"Fe": 1.0},
    is_chelate=True, fe_content_pct=6.0,
    category="chelate",
    notes="Stabil pH 3–9, teurer",
))

FE_EDTA = _register(Salt(
    name="Eisen-EDTA (13% Fe)",
    formula="Fe-EDTA",
    molar_mass=367.05, solubility_20=100.0, tank="A",
    ion_contribution={"Fe": 1.0},
    is_chelate=True, fe_content_pct=13.0,
    category="chelate",
    notes="Stabil pH 3–6.0, günstig",
))

FE_HBED = _register(Salt(
    name="Eisen-HBED (9% Fe)",
    formula="Fe-HBED",
    molar_mass=622.0, solubility_20=50.0, tank="A",
    ion_contribution={"Fe": 1.0},
    is_chelate=True, fe_content_pct=9.0,
    category="chelate",
    notes="Stabil pH 3–8, neueres Chelat",
))

# ═══════════════════════════════════════════════════════════════════════
# MIKRONÄHRSTOFF-EINZELSALZE
# ═══════════════════════════════════════════════════════════════════════

MANGANESE_SULFATE = _register(Salt(
    name="Mangansulfat-Monohydrat",
    formula="MnSO4·H2O",
    molar_mass=169.016, solubility_20=520.0, tank="B",
    ion_contribution={"Mn": 1.0, "SO4": 1.0},
    category="micro",
))

MANGANESE_CHELATE = _register(Salt(
    name="Mangan-EDTA (13% Mn)",
    formula="Mn-EDTA",
    molar_mass=423.0, solubility_20=100.0, tank="B",
    ion_contribution={"Mn": 1.0},
    is_chelate=True,
    category="micro",
))

ZINC_SULFATE = _register(Salt(
    name="Zinksulfat-Heptahydrat",
    formula="ZnSO4·7H2O",
    molar_mass=287.56, solubility_20=580.0, tank="B",
    ion_contribution={"Zn": 1.0, "SO4": 1.0},
    category="micro",
))

ZINC_CHELATE = _register(Salt(
    name="Zink-EDTA (15% Zn)",
    formula="Zn-EDTA",
    molar_mass=436.0, solubility_20=100.0, tank="B",
    ion_contribution={"Zn": 1.0},
    is_chelate=True,
    category="micro",
))

COPPER_SULFATE = _register(Salt(
    name="Kupfersulfat-Pentahydrat",
    formula="CuSO4·5H2O",
    molar_mass=249.685, solubility_20=316.0, tank="B",
    ion_contribution={"Cu": 1.0, "SO4": 1.0},
    category="micro",
))

COPPER_CHELATE = _register(Salt(
    name="Kupfer-EDTA (15% Cu)",
    formula="Cu-EDTA",
    molar_mass=423.0, solubility_20=80.0, tank="B",
    ion_contribution={"Cu": 1.0},
    is_chelate=True,
    category="micro",
))

BORIC_ACID = _register(Salt(
    name="Borsäure",
    formula="H3BO3",
    molar_mass=61.833, solubility_20=50.0, tank="B",
    ion_contribution={"B": 1.0},
    category="micro",
))

BORAX = _register(Salt(
    name="Borax (Natriumborat)",
    formula="Na2B4O7·10H2O",
    molar_mass=381.37, solubility_20=62.0, tank="B",
    ion_contribution={"B": 4.0, "Na": 2.0},
    category="micro",
    notes="Alternative zu Borsäure, pH-hebend",
))

SODIUM_MOLYBDATE = _register(Salt(
    name="Natriummolybdat-Dihydrat",
    formula="Na2MoO4·2H2O",
    molar_mass=241.95, solubility_20=560.0, tank="B",
    ion_contribution={"Mo": 1.0, "Na": 2.0},
    category="micro",
))

AMMONIUM_MOLYBDATE = _register(Salt(
    name="Ammoniummolybdat",
    formula="(NH4)6Mo7O24·4H2O",
    molar_mass=1235.86, solubility_20=430.0, tank="B",
    ion_contribution={"Mo": 7.0, "NH4": 6.0},
    category="micro",
))

# ═══════════════════════════════════════════════════════════════════════
# MIKRONÄHRSTOFF-PREMIXE (handelsüblich)
#
# Bei Premixen wird NICHT stöchiometrisch gerechnet, sondern über
# die Gehaltsangabe in mg pro g Premix. Für den Solver wird der
# Premix als Ganzes dosiert (g/L).
# ═══════════════════════════════════════════════════════════════════════

FERTY_10S = _register(Salt(
    name="Ferty 10S (Planta)",
    formula="Ferty10S",
    molar_mass=0,    # nicht relevant bei Premixen
    solubility_20=200.0,
    tank="B",
    ion_contribution={},
    is_premix=True,
    premix_mg_per_g={
        "Fe": 40.0,    # 4.0%
        "Mn": 40.0,    # 4.0%
        "Zn": 15.0,    # 1.5%
        "Cu": 6.0,     # 0.6%
        "B": 15.0,     # 1.5%
        "Mo": 1.0,     # 0.1%
    },
    category="premix",
    notes="Weit verbreiteter Mikronährstoff-Mix für Hydrokultur (Planta Düngemittel)",
))

REXOLIN_ABC = _register(Salt(
    name="Rexolin ABC (Yara/Kemira)",
    formula="RexolinABC",
    molar_mass=0, solubility_20=150.0, tank="B",
    ion_contribution={},
    is_premix=True,
    premix_mg_per_g={
        "Fe": 70.0,   # 7.0% (EDTA)
        "Mn": 35.0,   # 3.5% (EDTA)
        "Zn": 7.0,    # 0.7% (EDTA)
        "Cu": 3.0,    # 0.3% (EDTA)
        "B": 10.0,    # 1.0%
        "Mo": 1.0,    # 0.1%
    },
    category="premix",
    notes="Chelat-basierter Mikromix, alle Metalle als EDTA-Chelate",
))

TENSO_COCKTAIL = _register(Salt(
    name="Tenso Cocktail (ICL/Everris)",
    formula="TensoCocktail",
    molar_mass=0, solubility_20=100.0, tank="B",
    ion_contribution={},
    is_premix=True,
    premix_mg_per_g={
        "Fe": 37.0,   # 3.7% (EDTA+EDDHA)
        "Mn": 32.0,   # 3.2% (EDTA)
        "Zn": 7.0,    # 0.7% (EDTA)
        "Cu": 4.0,    # 0.4% (EDTA)
        "B": 7.0,     # 0.7%
        "Mo": 2.0,    # 0.2%
    },
    category="premix",
    notes="Enthält Fe-EDDHA-Anteil → stabiler bei höherem pH",
))

FETRILON_COMBI = _register(Salt(
    name="Fetrilon Combi (BASF)",
    formula="FetrilonCombi",
    molar_mass=0, solubility_20=120.0, tank="B",
    ion_contribution={},
    is_premix=True,
    premix_mg_per_g={
        "Fe": 40.0,   # 4.0% (EDTA)
        "Mn": 40.0,   # 4.0% (EDTA)
        "Zn": 15.0,   # 1.5% (EDTA)
        "Cu": 5.0,    # 0.5% (EDTA)
        "B": 5.0,     # 0.5%
        "Mo": 1.0,    # 0.1%
    },
    category="premix",
    notes="BASF Mikronährstoff-Mix, ähnlich Ferty 10S",
))

LIBREL_BMX = _register(Salt(
    name="Librel BMX (BASF)",
    formula="LibrelBMX",
    molar_mass=0, solubility_20=100.0, tank="B",
    ion_contribution={},
    is_premix=True,
    premix_mg_per_g={
        "Fe": 25.0,   # 2.5% (EDTA)
        "Mn": 25.0,   # 2.5% (EDTA)
        "Zn": 25.0,   # 2.5% (EDTA)
        "Cu": 15.0,   # 1.5% (EDTA)
        "B": 5.0,     # 0.5%
        "Mo": 5.0,    # 0.5%
    },
    category="premix",
    notes="Gleichmäßige Verteilung aller Mikros, für Spezialkulturen",
))


# ═══════════════════════════════════════════════════════════════════════
# Hilfsfunktionen
# ═══════════════════════════════════════════════════════════════════════

def get_salts_for_tank(tank: str) -> list[Salt]:
    return [s for s in DEFAULT_SALTS.values() if tank in s.tank]

def get_salt_by_formula(formula: str) -> Salt | None:
    return DEFAULT_SALTS.get(formula)

def get_salt_by_name(name: str) -> Salt | None:
    name_lower = name.lower()
    for salt in DEFAULT_SALTS.values():
        if salt.name.lower() == name_lower:
            return salt
    return None

def get_salts_by_category(category: str) -> list[Salt]:
    return [s for s in DEFAULT_SALTS.values() if s.category == category]

def get_premixes() -> list[Salt]:
    return [s for s in DEFAULT_SALTS.values() if s.is_premix]
