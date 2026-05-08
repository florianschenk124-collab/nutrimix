"""
API-Router: Werkzeuge (pH, Verdünnung, Rückwärtsrechner, Mischbarkeit).
"""

from fastapi import APIRouter, HTTPException
from api.models import (
    PhCorrectionRequest, PhCorrectionResponse,
    DilutionRequest, DilutionResponse,
    ReverseRequest, ReverseResponse,
    CompatibilityRequest, CompatibilityResponse, CompatibilityIssue,
    RatioResultOut,
)
from chemistry.salts import DEFAULT_SALTS
from chemistry.ph_correction import (
    calculate_ph_correction, ACIDS, BASES,
)
from chemistry.reverse_solver import reverse_calculate, SaltInput
from chemistry.compatibility import check_pair, build_matrix, get_key_salts


router = APIRouter(prefix="/api/tools", tags=["Werkzeuge"])


# ═══════════════════════════════════════════════════════════════════════
# pH-Korrektur
# ═══════════════════════════════════════════════════════════════════════

@router.get("/ph/acids")
def list_acids():
    """Verfügbare Säuren mit Keys."""
    return [
        {
            "key": key,
            "name": a.name,
            "formula": a.formula,
            "concentration_pct": a.concentration_pct,
        }
        for key, a in ACIDS.items()
    ]


@router.get("/ph/bases")
def list_bases():
    """Verfügbare Basen mit Keys."""
    return [
        {
            "key": key,
            "name": b.name,
            "formula": b.formula,
            "concentration_pct": b.concentration_pct,
        }
        for key, b in BASES.items()
    ]


@router.post("/ph", response_model=PhCorrectionResponse)
def calc_ph_correction(req: PhCorrectionRequest):
    """pH-Korrektur berechnen."""
    if req.acid_name not in ACIDS:
        raise HTTPException(400, f"Säure '{req.acid_name}' nicht bekannt. "
                            f"Verfügbar: {list(ACIDS.keys())}")

    result = calculate_ph_correction(
        hco3_mg=req.water_hco3_mg,
        target_ph=req.target_ph,
        water_ph=req.water_ph,
        volume_l=req.volume_l,
        acid_key=req.acid_name,
        base_key=req.base_name or "KOH",
    )
    return PhCorrectionResponse(
        acid_ml=round(result.ml_per_volume, 2) if result.direction == "down" else 0.0,
        acid_ml_per_l=round(result.ml_per_liter, 4) if result.direction == "down" else 0.0,
        acid_name=result.acid_or_base.name if result.direction == "down" else "",
        base_ml=round(result.ml_per_volume, 2) if result.direction == "up" else 0.0,
        base_ml_per_l=round(result.ml_per_liter, 4) if result.direction == "up" else 0.0,
        base_name=result.acid_or_base.name if result.direction == "up" else "",
        ion_changes_mg={k: round(v, 2) for k, v in result.ion_additions.items()},
        steps=result.steps,
        warnings=result.warnings,
    )


# ═══════════════════════════════════════════════════════════════════════
# Verdünnung (vereinfacht auf EC-Basis)
# ═══════════════════════════════════════════════════════════════════════

@router.post("/dilution", response_model=DilutionResponse)
def calc_dilution(req: DilutionRequest):
    """
    Vereinfachte Verdünnungsberechnung auf EC-Basis.

    Für die volle Berechnung (mit ionenspezifischer Verdünnung) erst
    /api/calculate aufrufen und dessen Ergebnis verwenden.
    """
    from chemistry.ec_estimator import estimate_ec

    if req.base_ec <= 0:
        raise HTTPException(400, "base_ec muss > 0 sein")

    effective_target = req.target_ec - req.water_ec
    if effective_target <= 0:
        effective_target = 0.1

    dilution_factor = min(1.0, effective_target / req.base_ec)

    ratio_sum = req.dose_ratio_a + req.dose_ratio_b
    if ratio_sum <= 0:
        ratio_sum = 2.0

    base_ml = 1000.0 / req.concentrate_factor * dilution_factor
    ml_a = base_ml * (req.dose_ratio_a / ratio_sum) * 2
    ml_b = base_ml * (req.dose_ratio_b / ratio_sum) * 2

    diluted_mg = {k: v * dilution_factor for k, v in req.achieved_mg.items()}
    achieved_ec = estimate_ec(diluted_mg) if diluted_mg else req.base_ec * dilution_factor

    return DilutionResponse(
        dilution_factor=round(dilution_factor, 4),
        ml_a_per_liter=round(ml_a, 2),
        ml_b_per_liter=round(ml_b, 2),
        ml_a_total=round(ml_a * req.volume_l, 1),
        ml_b_total=round(ml_b * req.volume_l, 1),
        diluted_mg={k: round(v, 2) for k, v in diluted_mg.items()},
        achieved_ec=round(achieved_ec, 2),
        warnings=[],
    )


# ═══════════════════════════════════════════════════════════════════════
# Rückwärtsrechner
# ═══════════════════════════════════════════════════════════════════════

@router.post("/reverse", response_model=ReverseResponse)
def calc_reverse(req: ReverseRequest):
    """Rückwärtsrechner: Salzeinwaagen -> Ionenkonzentrationen."""
    salt_inputs = []
    for entry in req.salts:
        salt = DEFAULT_SALTS.get(entry.salt_formula)
        if not salt:
            raise HTTPException(404, f"Salz '{entry.salt_formula}' nicht gefunden")
        salt_inputs.append(SaltInput(salt=salt, grams=entry.grams, tank=entry.tank))

    result = reverse_calculate(salt_inputs, req.volume_l)

    closest = None
    try:
        from chemistry.reverse_solver import find_matching_recipe
        matches = find_matching_recipe(result)
        if matches:
            closest = matches[0][0]
    except Exception:
        pass

    return ReverseResponse(
        ion_mg={k: round(v, 2) for k, v in result.ion_mg.items()},
        ion_mmol={k: round(v, 4) for k, v in result.ion_mmol.items()},
        ec_estimated=round(result.ec_estimated, 2),
        ratios=[
            RatioResultOut(
                name=r.name, description=r.description,
                actual=round(r.actual, 4),
                target_min=r.target_min, target_max=r.target_max,
                is_ok=r.is_ok, warning=r.warning, unit=r.unit,
            )
            for r in result.ratios
        ],
        closest_recipe=closest,
        warnings=result.warnings,
    )


# ═══════════════════════════════════════════════════════════════════════
# Mischbarkeit
# ═══════════════════════════════════════════════════════════════════════

@router.post("/compatibility", response_model=CompatibilityResponse)
def calc_compatibility(req: CompatibilityRequest):
    """Mischbarkeitsprüfung für eine Liste von Salzen (paarweise)."""
    salts = []
    for formula in req.salt_formulas:
        s = DEFAULT_SALTS.get(formula)
        if not s:
            raise HTTPException(404, f"Salz '{formula}' nicht gefunden")
        salts.append(s)

    issues = []
    for i in range(len(salts)):
        for j in range(i + 1, len(salts)):
            result = check_pair(salts[i], salts[j])
            if not result.compatible:
                issues.append(CompatibilityIssue(
                    salt_a=salts[i].name,
                    salt_b=salts[j].name,
                    severity=result.severity,
                    precipitate=result.precipitate,
                    description=result.reason,
                ))

    return CompatibilityResponse(
        is_compatible=len(issues) == 0,
        issues=issues,
    )


@router.get("/compatibility/matrix")
def get_compatibility_matrix():
    """Vollständige Mischbarkeitsmatrix der Hauptsalze."""
    salts = get_key_salts()
    matrix = build_matrix(salts)

    salt_names = [s.name for s in salts]
    salt_formulas = [s.formula for s in salts]

    checks = []
    for i, row in enumerate(matrix):
        for j, check in enumerate(row):
            if j > i:
                checks.append({
                    "salt_a": salt_names[i],
                    "salt_b": salt_names[j],
                    "formula_a": salt_formulas[i],
                    "formula_b": salt_formulas[j],
                    "compatible": check.compatible,
                    "severity": check.severity,
                    "reason": check.reason,
                    "precipitate": check.precipitate,
                })
    return {
        "salts": [{"name": n, "formula": f} for n, f in zip(salt_names, salt_formulas)],
        "checks": checks,
    }
