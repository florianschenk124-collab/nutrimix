"""
API-Router: Stammdaten (Pflanzen, Wachstumsphasen, Einstellungen, Übersetzungen).
"""

from fastapi import APIRouter, HTTPException
from api.models import (
    PlantOut, PlantIn,
    GrowthPlanOut, GrowthPhaseOut,
    SettingsModel,
)
from database.data_manager import (
    load_all_plants, save_custom_plant, delete_custom_plant,
    load_settings, save_settings,
)
from chemistry.growth_phases import DEFAULT_GROWTH_PLANS
from ui.locales import TRANSLATIONS, DATA_TRANSLATIONS, SALT_NAMES, SALT_NOTES, set_language


router = APIRouter(tags=["Stammdaten"])


# ═══════════════════════════════════════════════════════════════════════
# Pflanzen
# ═══════════════════════════════════════════════════════════════════════

plants_router = APIRouter(prefix="/api/plants", tags=["Pflanzen"])


@plants_router.get("", response_model=list[PlantOut])
def list_plants():
    return [PlantOut(**p) for p in load_all_plants()]


@plants_router.post("", response_model=PlantOut, status_code=201)
def create_plant(data: PlantIn):
    plant_dict = data.model_dump()
    save_custom_plant(plant_dict)
    return PlantOut(**plant_dict)


@plants_router.delete("/{name}", status_code=204)
def remove_plant(name: str):
    delete_custom_plant(name)


# ═══════════════════════════════════════════════════════════════════════
# Wachstumsphasen
# ═══════════════════════════════════════════════════════════════════════

growth_router = APIRouter(prefix="/api/growth-plans", tags=["Wachstumsphasen"])


@growth_router.get("", response_model=list[GrowthPlanOut])
def list_growth_plans():
    plans = []
    for plan in DEFAULT_GROWTH_PLANS.values():
        phases = [
            GrowthPhaseOut(
                name=ph.name, week_start=ph.week_start, week_end=ph.week_end,
                n_factor=ph.n_factor, k_factor=ph.k_factor,
                ca_factor=ph.ca_factor, mg_factor=ph.mg_factor,
                p_factor=ph.p_factor, ec_target=ph.ec_target,
                nh4_ratio=ph.nh4_ratio, notes=ph.notes,
            )
            for ph in plan.phases
        ]
        plans.append(GrowthPlanOut(
            name=plan.name,
            description=plan.description,
            base_recipe_name=plan.base_recipe_name,
            phases=phases,
        ))
    return plans


@growth_router.get("/{name}/schedule")
def get_weekly_schedule(name: str, recipe_override: str | None = None):
    """Wöchentlicher Zeitplan mit angepassten Ionenkonzentrationen.

    Falls das Basisrezept nicht gefunden wird, wird ein passendes
    Rezept per Teilname gesucht oder das erste verfügbare verwendet.
    Optional kann ein Rezept per ?recipe_override=Name erzwungen werden.
    """
    from chemistry.growth_phases import generate_weekly_schedule
    from database.data_manager import load_all_recipes

    plan = DEFAULT_GROWTH_PLANS.get(name)
    if not plan:
        raise HTTPException(404, f"Wachstumsplan '{name}' nicht gefunden")

    recipes = load_all_recipes()

    # 1. Override
    if recipe_override and recipe_override in recipes:
        base_recipe = recipes[recipe_override]
        used_recipe = recipe_override
    else:
        # 2. Exakter Name
        base_recipe = recipes.get(plan.base_recipe_name)
        used_recipe = plan.base_recipe_name

        # 3. Fallback: Teilname-Match (z.B. "Tomate" → "Sonneveld – Tomate")
        if not base_recipe:
            crop = plan.crop.lower() if hasattr(plan, 'crop') else ""
            plan_base = plan.base_recipe_name.lower()
            for rname, r in recipes.items():
                rname_lower = rname.lower()
                if crop and crop in rname_lower:
                    base_recipe = r
                    used_recipe = rname
                    break
                if any(word in rname_lower for word in plan_base.split() if len(word) > 3):
                    base_recipe = r
                    used_recipe = rname
                    break

        # 4. Fallback: erstes Rezept
        if not base_recipe:
            first_name = next(iter(recipes))
            base_recipe = recipes[first_name]
            used_recipe = first_name

    schedule = generate_weekly_schedule(plan, base_recipe.as_mg_dict())
    return {
        "plan_name": plan.name,
        "base_recipe": used_recipe,
        "original_recipe": plan.base_recipe_name,
        "total_weeks": plan.total_weeks,
        "weeks": schedule,
    }


@growth_router.get("/{name}", response_model=GrowthPlanOut)
def get_growth_plan(name: str):
    plan = DEFAULT_GROWTH_PLANS.get(name)
    if not plan:
        raise HTTPException(404, f"Wachstumsplan '{name}' nicht gefunden")
    phases = [
        GrowthPhaseOut(
            name=ph.name, week_start=ph.week_start, week_end=ph.week_end,
            n_factor=ph.n_factor, k_factor=ph.k_factor,
            ca_factor=ph.ca_factor, mg_factor=ph.mg_factor,
            p_factor=ph.p_factor, ec_target=ph.ec_target,
            nh4_ratio=ph.nh4_ratio, notes=ph.notes,
        )
        for ph in plan.phases
    ]
    return GrowthPlanOut(
        name=plan.name,
        description=plan.description,
        base_recipe_name=plan.base_recipe_name,
        phases=phases,
    )


# ═══════════════════════════════════════════════════════════════════════
# Einstellungen
# ═══════════════════════════════════════════════════════════════════════

settings_router = APIRouter(prefix="/api/settings", tags=["Einstellungen"])


@settings_router.get("", response_model=SettingsModel)
def get_settings():
    s = load_settings()
    return SettingsModel(**s)


@settings_router.put("", response_model=SettingsModel)
def update_settings(data: SettingsModel):
    settings = data.model_dump()
    save_settings(settings)
    # Sprache global setzen (für Backend-Übersetzungen)
    set_language(settings.get("language", "de"))
    return data


# ═══════════════════════════════════════════════════════════════════════
# Lokalisierung
# ═══════════════════════════════════════════════════════════════════════

locales_router = APIRouter(prefix="/api/locales", tags=["Lokalisierung"])


@locales_router.get("/{lang}")
def get_translations(lang: str):
    """
    Alle Übersetzungen für eine Sprache als flaches Dict.

    Kombiniert UI-Translations, Salznamen, Notizen und Data-Translations.
    """
    if lang not in ("de", "en"):
        raise HTTPException(400, f"Sprache '{lang}' nicht unterstützt (de/en)")

    result = {}

    # UI-Translations
    for key, entry in TRANSLATIONS.items():
        result[key] = entry.get(lang, entry.get("de", key))

    # Salznamen
    for de_name, entry in SALT_NAMES.items():
        if lang == "de":
            result[f"salt.name.{de_name}"] = de_name
        else:
            result[f"salt.name.{de_name}"] = entry.get("en", de_name)

    # Salznotizen
    for de_note, entry in SALT_NOTES.items():
        if lang == "de":
            result[f"salt.note.{de_note}"] = de_note
        else:
            result[f"salt.note.{de_note}"] = entry.get("en", de_note)

    # Data-Level Translations (Rezeptnamen, Phasennamen, etc.)
    for de_text, entry in DATA_TRANSLATIONS.items():
        if lang == "de":
            result[f"data.{de_text}"] = de_text
        else:
            result[f"data.{de_text}"] = entry.get("en", de_text)

    return result
