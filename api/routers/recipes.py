"""
API-Router: Rezepte (Standard + benutzerdefiniert).
"""

from fastapi import APIRouter, HTTPException
from api.models import RecipeIn, RecipeOut
from chemistry.recipes import NutrientRecipe
from database.data_manager import (
    load_all_recipes, save_custom_recipe, delete_custom_recipe,
)

router = APIRouter(prefix="/api/recipes", tags=["Rezepte"])


def _recipe_to_out(r: NutrientRecipe) -> RecipeOut:
    return RecipeOut(
        name=r.name, description=r.description,
        no3_n=r.no3_n, nh4_n=r.nh4_n, p=r.p,
        k=r.k, ca=r.ca, mg=r.mg, s=r.s,
        fe=r.fe, mn=r.mn, zn=r.zn, cu=r.cu, b=r.b, mo=r.mo,
        ph_min=r.ph_min, ph_max=r.ph_max, ec_target=r.ec_target,
        suitable_plants=r.suitable_plants, source=r.source,
        is_custom=r.is_custom,
        total_n=r.total_n,
        ions_mg=r.as_mg_dict(),
        ions_mmol=r.as_mmol_dict(),
    )


@router.get("", response_model=list[RecipeOut])
def list_recipes():
    """Alle Rezepte (Standard + eigene)."""
    recipes = load_all_recipes()
    return [_recipe_to_out(r) for r in recipes.values()]


@router.get("/{name}", response_model=RecipeOut)
def get_recipe(name: str):
    """Einzelnes Rezept nach Name."""
    recipes = load_all_recipes()
    r = recipes.get(name)
    if not r:
        raise HTTPException(404, f"Rezept '{name}' nicht gefunden")
    return _recipe_to_out(r)


@router.post("", response_model=RecipeOut, status_code=201)
def create_recipe(data: RecipeIn):
    """Benutzerdefiniertes Rezept speichern."""
    recipe = NutrientRecipe(
        name=data.name, description=data.description,
        no3_n=data.no3_n, nh4_n=data.nh4_n, p=data.p,
        k=data.k, ca=data.ca, mg=data.mg, s=data.s,
        fe=data.fe, mn=data.mn, zn=data.zn, cu=data.cu, b=data.b, mo=data.mo,
        ph_min=data.ph_min, ph_max=data.ph_max, ec_target=data.ec_target,
        suitable_plants=data.suitable_plants, source=data.source,
        is_custom=True,
    )
    save_custom_recipe(recipe)
    return _recipe_to_out(recipe)


@router.delete("/{name}", status_code=204)
def remove_recipe(name: str):
    """Benutzerdefiniertes Rezept löschen."""
    delete_custom_recipe(name)
