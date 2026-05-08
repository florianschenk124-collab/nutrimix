"""
Wasserprofile: Verwaltung und Verrechnung von Wasseranalysen.

Das Wasser enthält bereits Ionen, die von den Zielkonzentrationen
abgezogen werden müssen.
"""

from dataclasses import dataclass, field
from ui.locales import t, warn_fmt, salt_name


@dataclass
class WaterProfile:
    """Wasseranalyse mit Ionenkonzentrationen in mg/L."""
    name: str
    # Ionenkonzentrationen in mg/L (Elementbezug)
    ca: float = 0.0
    mg: float = 0.0
    na: float = 0.0
    k: float = 0.0
    cl: float = 0.0
    so4: float = 0.0       # als S
    hco3: float = 0.0      # als HCO₃ (Gesamtmasse, nicht Elementbezug)
    no3: float = 0.0       # als N
    fe: float = 0.0
    # Summenparameter
    ec: float = 0.0        # mS/cm
    ph: float = 7.0

    def as_mg_dict(self) -> dict[str, float]:
        """Gibt die Wasserionen als Dict zurück (gleiche Keys wie Rezept)."""
        return {
            "Ca": self.ca,
            "Mg": self.mg,
            "Na": self.na,
            "K": self.k,
            "Cl": self.cl,
            "SO4": self.so4,
            "HCO3": self.hco3,
            "NO3": self.no3,
            "Fe": self.fe,
        }


def subtract_water(
    target_mg: dict[str, float],
    water: WaterProfile,
) -> dict[str, float]:
    """
    Zieht die Wasseranalyse von den Zielkonzentrationen ab.

    Gibt die verbleibenden Soll-Konzentrationen in mg/L zurück.
    Negative Werte werden auf 0 gesetzt (Warnung wird separat behandelt).

    Returns:
        Tuple: (adjusted_targets, warnings)
    """
    water_mg = water.as_mg_dict()
    adjusted = dict(target_mg)  # Kopie
    warnings = []

    # Mapping: Rezept-Key → Wasser-Key
    ion_mapping = {
        "Ca": "Ca",
        "Mg": "Mg",
        "K": "K",
        "SO4": "SO4",
        "NO3": "NO3",
        "Fe": "Fe",
    }

    for recipe_key, water_key in ion_mapping.items():
        if recipe_key in adjusted and water_key in water_mg:
            water_val = water_mg[water_key]
            if water_val > 0:
                original = adjusted[recipe_key]
                adjusted[recipe_key] = max(0.0, original - water_val)

                if water_val > original:
                    excess = water_val - original
                    warnings.append(
                        warn_fmt("b.water_excess", recipe_key, water_val, original, excess)
                    )

    # Na und Cl als Warnung, wenn hoch
    if water.na > 30:
        warnings.append(
            warn_fmt("b.water_na", water.na)
        )
    if water.cl > 50:
        warnings.append(
            warn_fmt("b.water_cl", water.cl)
        )
    if water.hco3 > 150:
        warnings.append(
            warn_fmt("b.water_hco3", water.hco3)
        )

    return adjusted, warnings


# ═══════════════════════════════════════════════════════════════════════
# Standard-Wasserprofile
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_WATER_PROFILES: dict[str, WaterProfile] = {
    "Osmosewasser": WaterProfile(
        name="Osmosewasser",
        ec=0.0, ph=7.0,
    ),
    "Regenwasser": WaterProfile(
        name="Regenwasser",
        ca=1.0, mg=0.3, na=1.5, k=0.5,
        cl=2.0, so4=1.5, hco3=5.0, no3=0.5,
        ec=0.02, ph=5.8,
    ),
    "Leitungswasser Dresden (Beispiel)": WaterProfile(
        name="Leitungswasser Dresden (Beispiel)",
        ca=48.0, mg=8.0, na=12.0, k=2.5,
        cl=20.0, so4=35.0, hco3=140.0, no3=5.0,
        ec=0.35, ph=7.4,
    ),
    "Leitungswasser Berlin (Beispiel)": WaterProfile(
        name="Leitungswasser Berlin (Beispiel)",
        ca=100.0, mg=12.0, na=20.0, k=4.0,
        cl=35.0, so4=60.0, hco3=250.0, no3=3.0,
        ec=0.65, ph=7.5,
    ),
}
