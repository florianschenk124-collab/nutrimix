"""
Rückwärtsrechner: Aus Salzeinwaagen → Ionenkonzentrationen.

"Ich habe diese Salze eingewogen, was kommt dabei raus?"
"""

from dataclasses import dataclass, field
from chemistry.salts import DEFAULT_SALTS, Salt
from chemistry.ions import ION_BY_SYMBOL, mmol_to_mg
from chemistry.ec_estimator import estimate_ec
from chemistry.ratios import check_ratios, RatioResult
from ui.locales import t, warn_fmt, salt_name


@dataclass
class SaltInput:
    """Ein Salz mit der eingewogenen Menge."""
    salt: Salt
    grams: float       # Einwaage in Gramm
    tank: str = ""     # "A" oder "B" (optional)


@dataclass
class ReverseResult:
    """Ergebnis einer Rückwärtsberechnung."""
    volume_l: float
    ion_mmol: dict[str, float] = field(default_factory=dict)
    ion_mg: dict[str, float] = field(default_factory=dict)
    ec_estimated: float = 0.0
    ratios: list[RatioResult] = field(default_factory=list)
    salt_inputs: list[SaltInput] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)


def reverse_calculate(
    salt_inputs: list[SaltInput],
    volume_l: float,
) -> ReverseResult:
    """
    Berechnet Ionenkonzentrationen aus Salzeinwaagen.

    Args:
        salt_inputs: Liste von (Salt, Gramm)-Paaren
        volume_l: Volumen der Endlösung in Litern

    Returns:
        ReverseResult mit allen berechneten Konzentrationen
    """
    result = ReverseResult(volume_l=volume_l)
    result.salt_inputs = salt_inputs

    # Alle Ionen sammeln
    ion_mmol: dict[str, float] = {}

    for si in salt_inputs:
        salt = si.salt
        g = si.grams

        if g <= 0:
            continue

        g_per_l = g / volume_l

        if salt.is_premix:
            # Premix: mg/g × g/L = mg/L → mmol/L
            for ion_sym, mg_per_g in salt.premix_mg_per_g.items():
                mg_per_l = g_per_l * mg_per_g
                ion = ION_BY_SYMBOL.get(ion_sym)
                if ion:
                    mmol = mg_per_l / ion.molar_mass
                    ion_mmol[ion_sym] = ion_mmol.get(ion_sym, 0) + mmol
            result.steps.append(
                f"{salt.name}: {g:.2f} g → {g_per_l:.4f} g/L (Premix)")
        else:
            # Normal: mmol Salz = g / M × 1000, dann × Stöchiometrie
            mmol_salt_per_l = g_per_l / salt.molar_mass * 1000.0

            delivered = []
            for ion_sym, stoich in salt.ion_contribution.items():
                mmol_ion = mmol_salt_per_l * stoich
                ion_mmol[ion_sym] = ion_mmol.get(ion_sym, 0) + mmol_ion
                ion = ION_BY_SYMBOL.get(ion_sym)
                if ion:
                    mg = mmol_ion * ion.molar_mass
                    delivered.append(f"{ion.display}: {mg:.2f} mg/L")

            result.steps.append(
                f"{salt.name}: {g:.2f} g → {g_per_l:.4f} g/L "
                f"({mmol_salt_per_l:.3f} mmol/L) → {', '.join(delivered)}")

    # In mg/L umrechnen
    ion_mg: dict[str, float] = {}
    for ion_sym, mmol in ion_mmol.items():
        ion = ION_BY_SYMBOL.get(ion_sym)
        if ion:
            ion_mg[ion_sym] = mmol * ion.molar_mass

    result.ion_mmol = ion_mmol
    result.ion_mg = ion_mg

    # EC schätzen
    result.ec_estimated = estimate_ec(ion_mg)
    result.steps.append(f"\nGeschätzte EC: {result.ec_estimated:.2f} mS/cm")

    # Ratios
    result.ratios = check_ratios(ion_mg)

    # Warnungen
    ca = ion_mg.get("Ca", 0)
    p = ion_mg.get("H2PO4", 0)
    if ca > 50 and p > 20:
        result.warnings.append(t("b.warn_ca_p_precip"))

    if result.ec_estimated > 3.5:
        result.warnings.append(warn_fmt("b.rev_ec_high", result.ec_estimated))
    elif result.ec_estimated < 0.5:
        result.warnings.append(warn_fmt("b.rev_ec_low", result.ec_estimated))

    return result


def find_matching_recipe(reverse_result: ReverseResult) -> list[tuple[str, float]]:
    """
    Findet das ähnlichste Standardrezept zur berechneten Lösung.

    Returns: Liste von (Rezeptname, Ähnlichkeit in %) sortiert nach Ähnlichkeit
    """
    from chemistry.recipes import DEFAULT_RECIPES

    matches = []
    calc_mg = reverse_result.ion_mg

    for name, recipe in DEFAULT_RECIPES.items():
        target_mg = recipe.as_mg_dict()

        # Euklidische Distanz über Hauptionen (normiert)
        total_diff = 0.0
        total_target = 0.0
        for sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4"]:
            t = target_mg.get(sym, 0)
            c = calc_mg.get(sym, 0)
            if t > 0:
                diff = abs(t - c) / t
                total_diff += diff
                total_target += 1.0

        if total_target > 0:
            similarity = max(0, (1.0 - total_diff / total_target)) * 100
            matches.append((name, similarity))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches
