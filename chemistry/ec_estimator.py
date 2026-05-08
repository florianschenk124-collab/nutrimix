"""
EC-Schätzung (Electrical Conductivity) aus Ionenkonzentrationen.

Zwei Methoden:
1. Einfache Summation (TDS-basiert)
2. Ionenspezifisch über molare Grenzleitfähigkeiten (genauer)
"""

from chemistry.ions import ION_BY_SYMBOL, Ion, mg_to_mmol, MACRO_IONS
from ui.locales import t, warn_fmt, salt_name


def estimate_ec_simple(ion_mg: dict[str, float]) -> float:
    """
    Einfache EC-Schätzung über Summe der Ionenkonzentrationen.

    Faustregel: EC (mS/cm) ≈ TDS (mg/L) / 640
    TDS ≈ Summe der gelösten Salze

    Args:
        ion_mg: Ionenkonzentrationen in mg/L (Elementbezug)

    Returns:
        Geschätzter EC-Wert in mS/cm.
    """
    total_mg = sum(ion_mg.values())
    return total_mg / 640.0


def estimate_ec_ionic(ion_mg: dict[str, float]) -> float:
    """
    Ionenspezifische EC-Schätzung über molare Grenzleitfähigkeiten.

    EC = Σ (cᵢ · |zᵢ| · λ₀ᵢ) / 1000

    wobei:
    - cᵢ = Konzentration in mmol/L
    - zᵢ = Ladungszahl
    - λ₀ᵢ = molare Grenzleitfähigkeit bei unendl. Verdünnung (S·cm²/mol)

    Die Division durch 1000 konvertiert zu mS/cm.

    Anmerkung: Dies ist eine Näherung. Reale EC-Werte sind durch
    Ionenwechselwirkungen (~10-20%) niedriger als die berechneten.

    Args:
        ion_mg: Ionenkonzentrationen in mg/L (Elementbezug)

    Returns:
        Geschätzter EC-Wert in mS/cm.
    """
    ec = 0.0
    activity_correction = 0.85  # Korrekturfaktor für Ionenwechselwirkungen

    for ion_sym, mg_val in ion_mg.items():
        if mg_val <= 0 or ion_sym not in ION_BY_SYMBOL:
            continue

        ion = ION_BY_SYMBOL[ion_sym]

        if ion.lambda_0 <= 0:
            continue  # Undissoziierte Spezies (B, Mo)

        mmol = mg_to_mmol(mg_val, ion)

        # EC-Beitrag: mmol/L × λ₀(molar, S·cm²/mol) / 1000 → mS/cm
        # λ₀ sind molare Leitfähigkeiten (pro Mol Ion, nicht pro Äquivalent)
        # Die Ladung steckt bereits implizit in λ₀
        ec += mmol * ion.lambda_0 / 1000.0

    ec_ms = ec * activity_correction

    return ec_ms


def estimate_ec(
    ion_mg: dict[str, float],
    method: str = "ionic",
) -> float:
    """
    EC-Schätzung mit wählbarer Methode.

    Args:
        ion_mg: Ionenkonzentrationen in mg/L
        method: "simple" oder "ionic"

    Returns:
        EC in mS/cm
    """
    if method == "simple":
        return estimate_ec_simple(ion_mg)
    else:
        return estimate_ec_ionic(ion_mg)


def ec_rating(ec: float, target_ec: float = 0.0) -> str:
    """
    Bewertet einen EC-Wert und gibt eine Einschätzung.

    Returns:
        Bewertung als String mit Emoji.
    """
    if target_ec > 0:
        ratio = ec / target_ec
        if 0.8 <= ratio <= 1.2:
            return f"✅ {ec:.2f} mS/cm (Ziel: {target_ec:.1f})"
        elif ratio < 0.8:
            return f"⚠️ {ec:.2f} mS/cm (unter Ziel {target_ec:.1f})"
        else:
            return f"⚠️ {ec:.2f} mS/cm (über Ziel {target_ec:.1f})"

    # Allgemeine Bewertung
    if ec < 0.5:
        return warn_fmt("b.ec_very_low", f"{ec:.2f}")
    elif ec < 1.5:
        return warn_fmt("b.ec_low", f"{ec:.2f}")
    elif ec < 2.5:
        return warn_fmt("b.ec_medium", f"{ec:.2f}")
    elif ec < 3.5:
        return warn_fmt("b.ec_high", f"{ec:.2f}")
    else:
        return warn_fmt("b.ec_very_high", f"{ec:.2f}")
