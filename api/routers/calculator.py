"""
API-Router: Hauptrechner (Solver).

Kombiniert alle Berechnungsschritte in einem Endpoint:
Wasserabzug → Solver → Löslichkeit → EC → Ratios → A/B-Validierung.

Einzelne Schritte sind auch separat aufrufbar.
"""

from fastapi import APIRouter, HTTPException
from api.models import (
    CalculateRequest, CalculateResponse,
    SaltResultOut, SolubilityCheckOut, RatioResultOut,
)
from database.data_manager import load_all_recipes, load_all_water_profiles
from chemistry.solver import solve, SolverResult
from chemistry.water import subtract_water
from chemistry.concentrate import calculate_concentrate, suggest_max_concentrate_factor
from chemistry.ec_estimator import estimate_ec, ec_rating
from chemistry.ratios import check_ratios
from chemistry.ab_split import validate_ab_split


router = APIRouter(prefix="/api/calculate", tags=["Rechner"])


def _salt_result_to_out(sr) -> SaltResultOut:
    return SaltResultOut(
        salt_name=sr.salt.name,
        salt_formula=sr.salt.formula,
        tank=sr.tank,
        mmol_per_l=round(sr.mmol_per_l, 6),
        g_per_l=round(sr.g_per_l, 6),
        g_total=round(sr.g_total, 4),
        g_concentrate=round(sr.g_concentrate, 4),
        cost_total=round(sr.cost_total, 4),
    )


def _ratio_to_out(r) -> RatioResultOut:
    return RatioResultOut(
        name=r.name, description=r.description,
        actual=round(r.actual, 4),
        target_min=r.target_min, target_max=r.target_max,
        is_ok=r.is_ok, warning=r.warning, unit=r.unit,
    )


@router.post("", response_model=CalculateResponse)
def calculate(req: CalculateRequest):
    """
    Vollständige Berechnung: Rezept + Wasser → Salzmengen, EC, Ratios.

    Dies ist der Haupt-Endpoint, der alle Schritte kombiniert.
    """
    # Rezept laden
    recipes = load_all_recipes()
    recipe = recipes.get(req.recipe_name)
    if not recipe:
        raise HTTPException(404, f"Rezept '{req.recipe_name}' nicht gefunden")

    # Wasserprofil laden
    profiles = load_all_water_profiles()
    water = profiles.get(req.water_profile_name)
    if not water:
        raise HTTPException(404, f"Wasserprofil '{req.water_profile_name}' nicht gefunden")

    target_mg = recipe.as_mg_dict()
    water_mg_dict = water.as_mg_dict()

    # ── Schritt 1: Wasserabzug ──
    adjusted_mg, water_warnings = subtract_water(target_mg, water)

    # ── Schritt 2: Solver ──
    result: SolverResult = solve(
        adjusted_mg,
        volume_l=req.volume_l,
        concentrate_factor=req.concentrate_factor,
        fe_chelate=req.fe_chelate,
        nh4_source=req.nh4_source,
        p_source=req.p_source,
        cl_target_mg=req.cl_target_mg,
        cl_source=req.cl_source,
        micro_source=req.micro_source,
        dose_ratio=req.dose_ratio,
    )

    # ── Schritt 3: Löslichkeit ──
    conc_result = calculate_concentrate(result, req.volume_l, req.concentrate_factor)
    max_factor = suggest_max_concentrate_factor(result, req.volume_l)

    sol_checks = [
        SolubilityCheckOut(
            salt_name=c.salt_name, formula=c.formula, tank=c.tank,
            g_per_l_concentrate=round(c.g_per_l_concentrate, 2),
            solubility_limit=round(c.solubility_limit, 1),
            saturation_pct=round(c.saturation_pct, 1),
            is_ok=c.is_ok, warning=c.warning,
        )
        for c in conc_result.checks
    ]

    # ── Schritt 4: EC ──
    # Ist-Werte + Wasserionen für realistische EC
    total_mg = dict(result.achieved_mg)
    for ion_sym in ["Ca", "Mg", "K", "SO4", "NO3"]:
        if ion_sym in water_mg_dict and ion_sym in total_mg:
            total_mg[ion_sym] += water_mg_dict[ion_sym]

    ec_simple = estimate_ec(result.achieved_mg, method="simple")
    ec_ionic = estimate_ec(result.achieved_mg, method="ionic")
    ec_rate = ec_rating(ec_ionic, recipe.ec_target)

    # ── Schritt 5: Verhältnisse ──
    ratio_results = check_ratios(total_mg)
    ratios_out = [_ratio_to_out(r) for r in ratio_results]

    # ── Schritt 6: A/B-Validierung ──
    ab_warns = validate_ab_split(
        [sr.salt for sr in result.tank_a],
        [sr.salt for sr in result.tank_b],
    )

    # ── Response bauen ──
    return CalculateResponse(
        tank_a=[_salt_result_to_out(sr) for sr in result.tank_a],
        tank_b=[_salt_result_to_out(sr) for sr in result.tank_b],
        target_mg={k: round(v, 2) for k, v in target_mg.items()},
        adjusted_mg={k: round(v, 2) for k, v in adjusted_mg.items()},
        achieved_mg={k: round(v, 2) for k, v in result.achieved_mg.items()},
        delta_mg={k: round(v, 2) for k, v in result.delta_mg.items()},
        water_mg={k: round(v, 2) for k, v in water_mg_dict.items()},
        water_warnings=water_warnings,
        solubility_checks=sol_checks,
        max_concentrate_factor=round(max_factor, 0),
        tank_a_volume_l=round(conc_result.tank_a_volume_l, 2),
        tank_b_volume_l=round(conc_result.tank_b_volume_l, 2),
        ec_simple=round(ec_simple, 2),
        ec_ionic=round(ec_ionic, 2),
        ec_rating=ec_rate,
        ratios=ratios_out,
        ab_warnings=ab_warns,
        steps=result.steps,
        warnings=result.warnings + conc_result.warnings,
        total_cost=round(result.total_cost, 4),
        cost_per_liter=round(result.cost_per_liter(), 6),
        dose_ratio_a=result.dose_ratio_a,
        dose_ratio_b=result.dose_ratio_b,
    )


# ── Einzel-Endpoints für gezielte Berechnungen ──────────────────

@router.post("/ec")
def calc_ec(ion_mg: dict[str, float], method: str = "ionic") -> dict:
    """EC-Wert aus Ionenkonzentrationen schätzen."""
    ec = estimate_ec(ion_mg, method=method)
    return {"ec": round(ec, 3), "method": method}


@router.post("/ratios", response_model=list[RatioResultOut])
def calc_ratios(ion_mg: dict[str, float]) -> list[RatioResultOut]:
    """Nährstoff-Verhältnisse prüfen."""
    results = check_ratios(ion_mg)
    return [_ratio_to_out(r) for r in results]
