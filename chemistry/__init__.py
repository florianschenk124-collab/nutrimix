"""
Chemistry-Modul: Nährlösungs-Berechnungen.

Hauptfunktionen:
- solve(): Salzmengen berechnen
- subtract_water(): Wasseranalyse abziehen
- calculate_concentrate(): Stammlösung + Löslichkeitsprüfung
- estimate_ec(): EC-Wert schätzen
"""

from chemistry.solver import solve, SolverResult, SaltResult, format_result_text
from chemistry.water import subtract_water, WaterProfile, DEFAULT_WATER_PROFILES
from chemistry.concentrate import calculate_concentrate, suggest_max_concentrate_factor
from chemistry.ec_estimator import estimate_ec, ec_rating
from chemistry.recipes import NutrientRecipe, DEFAULT_RECIPES, get_recipe, get_recipe_names
from chemistry.salts import DEFAULT_SALTS, Salt, get_premixes, get_salts_by_category
from chemistry.ab_split import validate_ab_split
from chemistry.ratios import check_ratios, format_ratio_summary, RatioResult
from chemistry.ions import mg_to_mmol, mmol_to_mg, ION_BY_SYMBOL

__all__ = [
    "solve", "SolverResult", "SaltResult", "format_result_text",
    "subtract_water", "WaterProfile", "DEFAULT_WATER_PROFILES",
    "calculate_concentrate", "suggest_max_concentrate_factor",
    "estimate_ec", "ec_rating",
    "NutrientRecipe", "DEFAULT_RECIPES", "get_recipe", "get_recipe_names",
    "DEFAULT_SALTS", "Salt",
    "validate_ab_split",
    "check_ratios", "format_ratio_summary", "RatioResult",
    "mg_to_mmol", "mmol_to_mg", "ION_BY_SYMBOL",
]
