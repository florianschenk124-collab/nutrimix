"""
Verdünnungsrechner: Stammlösung → Gebrauchslösung.

Berechnet:
- Dosiermengen A/B für Ziel-EC
- Verdünnte Ionenkonzentrationen
- EC nach Verdünnung
"""

from dataclasses import dataclass, field
from chemistry.solver import SolverResult
from chemistry.ec_estimator import estimate_ec
from chemistry.ions import ION_BY_SYMBOL
from ui.locales import t, warn_fmt, salt_name


@dataclass
class DilutionResult:
    """Ergebnis einer Verdünnungsberechnung."""
    target_ec: float            # Ziel-EC in mS/cm
    base_ec: float              # EC der vollen Nährlösung
    dilution_factor: float      # Verdünnungsfaktor (0–1)
    ml_a_per_liter: float       # mL Tank A pro Liter Endlösung
    ml_b_per_liter: float       # mL Tank B pro Liter Endlösung
    ml_a_total: float           # mL Tank A für Gesamtvolumen
    ml_b_total: float           # mL Tank B für Gesamtvolumen
    diluted_mg: dict[str, float]  # Ionenkonzentrationen nach Verdünnung
    achieved_ec: float          # EC nach Verdünnung
    volume_l: float
    concentrate_factor: float
    dose_ratio_a: float
    dose_ratio_b: float
    steps: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def calculate_dilution(
    solver_result: SolverResult,
    target_ec: float,
    volume_l: float,
    concentrate_factor: float = 100.0,
    dose_ratio_a: float = 1.0,
    dose_ratio_b: float = 1.0,
    water_ec: float = 0.0,
) -> DilutionResult:
    """
    Berechnet Dosiermengen für eine verdünnte Nährlösung.

    Args:
        solver_result: Ergebnis einer Solver-Berechnung (volle Konzentration)
        target_ec: Ziel-EC der Gebrauchslösung in mS/cm
        volume_l: Volumen der Gebrauchslösung in Litern
        concentrate_factor: Konzentrationsfaktor der Stammlösung
        dose_ratio_a: Dosierverhältnis A
        dose_ratio_b: Dosierverhältnis B
        water_ec: EC des Ausgangswassers (wird abgezogen)
    """
    steps = []
    warnings = []

    # EC der vollen Nährlösung
    base_ec = estimate_ec(solver_result.achieved_mg)
    steps.append(f"EC der vollen Nährlösung: {base_ec:.2f} mS/cm")
    steps.append(f"Ziel-EC: {target_ec:.2f} mS/cm")

    if water_ec > 0:
        steps.append(warn_fmt("b.dil_water_ec", f"{water_ec:.2f}"))
        effective_target = target_ec - water_ec
        if effective_target <= 0:
            warnings.append(t("b.dil_water_higher"))
            effective_target = 0.1
        steps.append(warn_fmt("b.dil_effective", f"{effective_target:.2f}"))
    else:
        effective_target = target_ec

    # Verdünnungsfaktor
    if base_ec > 0:
        dilution_factor = min(1.0, effective_target / base_ec)
    else:
        dilution_factor = 1.0
        warnings.append(t("b.dil_base_zero"))

    steps.append(warn_fmt("b.dil_factor", f"{dilution_factor:.4f}", f"{dilution_factor*100:.1f}"))

    # Dosiermengen pro Liter
    # Bei Konzentratfaktor 100: 1 L Stammlösung → 100 L Endlösung
    # → 10 mL/L bei voller Konzentration
    # Aufgeteilt nach Dosierverhältnis A:B
    total_ratio = dose_ratio_a + dose_ratio_b
    base_ml_per_l = 1000.0 / concentrate_factor  # mL Stammlösung pro Liter bei 100%

    ml_a_base = base_ml_per_l * (dose_ratio_a / total_ratio)
    ml_b_base = base_ml_per_l * (dose_ratio_b / total_ratio)

    ml_a_per_l = ml_a_base * dilution_factor
    ml_b_per_l = ml_b_base * dilution_factor

    steps.append(t("b.dil_dosing"))
    steps.append(f"  Tank A: {ml_a_per_l:.2f} mL/L")
    steps.append(f"  Tank B: {ml_b_per_l:.2f} mL/L")
    steps.append(f"  {t('b.total')}: {ml_a_per_l + ml_b_per_l:.2f} mL/L")

    ml_a_total = ml_a_per_l * volume_l
    ml_b_total = ml_b_per_l * volume_l

    steps.append(f"{t('dil.for_volume')} {volume_l:.0f} L:")
    steps.append(f"  Tank A: {ml_a_total:.1f} mL")
    steps.append(f"  Tank B: {ml_b_total:.1f} mL")

    # Verdünnte Konzentrationen
    diluted_mg = {}
    for sym, mg in solver_result.achieved_mg.items():
        diluted_mg[sym] = mg * dilution_factor

    achieved_ec = estimate_ec(diluted_mg)
    steps.append(f"{t('b.calc_ec')}: {achieved_ec:.2f} mS/cm")

    if dilution_factor < 0.3:
        warnings.append(t("b.dil_strong"))
    if dilution_factor > 0.95:
        warnings.append(t("b.dil_minimal"))

    return DilutionResult(
        target_ec=target_ec, base_ec=base_ec,
        dilution_factor=dilution_factor,
        ml_a_per_liter=ml_a_per_l, ml_b_per_liter=ml_b_per_l,
        ml_a_total=ml_a_total, ml_b_total=ml_b_total,
        diluted_mg=diluted_mg, achieved_ec=achieved_ec,
        volume_l=volume_l, concentrate_factor=concentrate_factor,
        dose_ratio_a=dose_ratio_a, dose_ratio_b=dose_ratio_b,
        steps=steps, warnings=warnings,
    )


def ec_dilution_table(
    solver_result: SolverResult,
    concentrate_factor: float = 100.0,
    dose_ratio_a: float = 1.0,
    dose_ratio_b: float = 1.0,
    ec_steps: list[float] | None = None,
) -> list[dict]:
    """
    Erstellt eine Verdünnungstabelle für verschiedene EC-Werte.

    Returns: Liste von dicts mit ec, factor, ml_a, ml_b
    """
    if ec_steps is None:
        base_ec = estimate_ec(solver_result.achieved_mg)
        ec_steps = [round(x * 0.2, 1) for x in range(2, int(base_ec / 0.2) + 2)]
        ec_steps = [e for e in ec_steps if e <= base_ec * 1.05]

    table = []
    for ec in ec_steps:
        res = calculate_dilution(
            solver_result, ec, 1.0, concentrate_factor,
            dose_ratio_a, dose_ratio_b,
        )
        table.append({
            "ec": ec,
            "factor": res.dilution_factor,
            "ml_a": res.ml_a_per_liter,
            "ml_b": res.ml_b_per_liter,
            "ml_total": res.ml_a_per_liter + res.ml_b_per_liter,
        })
    return table
