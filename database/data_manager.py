"""
Daten-Manager: Persistenz für benutzerdefinierte Rezepte, Wasserprofile und Einstellungen.
Verwendet JSON-Dateien im Benutzerverzeichnis.
"""

import json
import os
from pathlib import Path
from chemistry.recipes import NutrientRecipe, DEFAULT_RECIPES
from chemistry.water import WaterProfile, DEFAULT_WATER_PROFILES


def _get_data_dir() -> Path:
    """Gibt das Datenverzeichnis zurück. Neben der .exe oder neben main.py."""
    import sys
    if getattr(sys, 'frozen', False):
        # PyInstaller .exe → Daten neben der .exe speichern
        base = Path(sys.executable).parent / "nutrient_mixer_data"
    else:
        base = Path(__file__).parent / "user_data"
    base.mkdir(exist_ok=True)
    return base


# ═══════════════════════════════════════════════════════════════════════
# Rezepte
# ═══════════════════════════════════════════════════════════════════════

def _recipe_to_dict(r: NutrientRecipe) -> dict:
    return {
        "name": r.name, "description": r.description,
        "no3_n": r.no3_n, "nh4_n": r.nh4_n, "p": r.p,
        "k": r.k, "ca": r.ca, "mg": r.mg, "s": r.s,
        "fe": r.fe, "mn": r.mn, "zn": r.zn, "cu": r.cu, "b": r.b, "mo": r.mo,
        "ph_min": r.ph_min, "ph_max": r.ph_max, "ec_target": r.ec_target,
        "suitable_plants": r.suitable_plants, "source": r.source,
        "is_custom": True,
    }

def _dict_to_recipe(d: dict) -> NutrientRecipe:
    return NutrientRecipe(**{k: v for k, v in d.items() if k != "is_custom"},
                          is_custom=d.get("is_custom", True))

def load_all_recipes() -> dict[str, NutrientRecipe]:
    """Lädt Standard- und benutzerdefinierte Rezepte."""
    recipes = dict(DEFAULT_RECIPES)
    path = _get_data_dir() / "custom_recipes.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                custom = json.load(f)
            for d in custom:
                r = _dict_to_recipe(d)
                recipes[r.name] = r
        except (json.JSONDecodeError, KeyError):
            pass
    return recipes

def save_custom_recipe(recipe: NutrientRecipe):
    """Speichert ein benutzerdefiniertes Rezept."""
    path = _get_data_dir() / "custom_recipes.json"
    existing = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = []
    # Duplikat ersetzen
    existing = [d for d in existing if d.get("name") != recipe.name]
    existing.append(_recipe_to_dict(recipe))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

def delete_custom_recipe(name: str):
    """Löscht ein benutzerdefiniertes Rezept."""
    path = _get_data_dir() / "custom_recipes.json"
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        existing = json.load(f)
    existing = [d for d in existing if d.get("name") != name]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════
# Wasserprofile
# ═══════════════════════════════════════════════════════════════════════

def _water_to_dict(w: WaterProfile) -> dict:
    return {
        "name": w.name, "ca": w.ca, "mg": w.mg, "na": w.na, "k": w.k,
        "cl": w.cl, "so4": w.so4, "hco3": w.hco3, "no3": w.no3, "fe": w.fe,
        "ec": w.ec, "ph": w.ph,
    }

def _dict_to_water(d: dict) -> WaterProfile:
    return WaterProfile(**d)

def load_all_water_profiles() -> dict[str, WaterProfile]:
    """Lädt Standard- und benutzerdefinierte Wasserprofile."""
    profiles = dict(DEFAULT_WATER_PROFILES)
    path = _get_data_dir() / "custom_water_profiles.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                custom = json.load(f)
            for d in custom:
                w = _dict_to_water(d)
                profiles[w.name] = w
        except (json.JSONDecodeError, KeyError):
            pass
    return profiles

def save_custom_water_profile(profile: WaterProfile):
    """Speichert ein benutzerdefiniertes Wasserprofil."""
    path = _get_data_dir() / "custom_water_profiles.json"
    existing = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = []
    existing = [d for d in existing if d.get("name") != profile.name]
    existing.append(_water_to_dict(profile))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

def delete_custom_water_profile(name: str):
    """Löscht ein benutzerdefiniertes Wasserprofil."""
    path = _get_data_dir() / "custom_water_profiles.json"
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        existing = json.load(f)
    existing = [d for d in existing if d.get("name") != name]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════
# Einstellungen
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_SETTINGS = {
    "default_unit": "mg/L (ppm)",
    "default_concentrate_factor": 100,
    "default_volume": 1000,
    "ec_method": "ionic",
    "fe_chelate": "Fe-DTPA",
    "nh4_source": "NH4NO3",
    "p_source": "KH2PO4",
    "micro_source": "individual",
    "dose_ratio": "1:1",
    "language": "de",
}

def load_settings() -> dict:
    path = _get_data_dir() / "settings.json"
    settings = dict(DEFAULT_SETTINGS)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            settings.update(loaded)
        except json.JSONDecodeError:
            pass
    return settings

def save_settings(settings: dict):
    path = _get_data_dir() / "settings.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════
# Pflanzen
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_PLANTS = [
    {"name": "🍅 Tomate", "category": "Fruchtgemüse",
     "ec_min": 2.0, "ec_max": 3.5, "ph_min": 5.5, "ph_max": 6.5,
     "notes": "Hoher K-Bedarf in Fruchtphase, Ca wichtig gegen Blütenendfäule",
     "keywords": ["tomate", "tomato"]},
    {"name": "🥒 Gurke", "category": "Fruchtgemüse",
     "ec_min": 1.5, "ec_max": 2.5, "ph_min": 5.5, "ph_max": 6.0,
     "notes": "Empfindlich gegen hohe EC, gleichmäßige Nährstoffversorgung",
     "keywords": ["gurke", "cucumber"]},
    {"name": "🫑 Paprika", "category": "Fruchtgemüse",
     "ec_min": 1.8, "ec_max": 2.8, "ph_min": 5.5, "ph_max": 6.5,
     "notes": "Moderater K-Bedarf, Ca-empfindlich",
     "keywords": ["paprika", "chili", "pepper"]},
    {"name": "🥬 Salat", "category": "Blattgemüse",
     "ec_min": 0.8, "ec_max": 1.5, "ph_min": 5.5, "ph_max": 6.5,
     "notes": "Niedrige EC, hoher N-Bedarf, Tipburn bei Ca-Mangel",
     "keywords": ["salat", "lettuce"]},
    {"name": "🌿 Basilikum", "category": "Kräuter",
     "ec_min": 1.0, "ec_max": 1.6, "ph_min": 5.5, "ph_max": 6.5,
     "notes": "Leicht erhöhter K-Bedarf, gute Mg-Versorgung wichtig",
     "keywords": ["basilikum", "basil"]},
    {"name": "🍓 Erdbeere", "category": "Fruchtgemüse",
     "ec_min": 1.2, "ec_max": 2.0, "ph_min": 5.5, "ph_max": 6.5,
     "notes": "Fe-empfindlich (Chlorose), K für Fruchtqualität",
     "keywords": ["erdbeere", "strawberry"]},
    {"name": "🌶️ Chili", "category": "Fruchtgemüse",
     "ec_min": 2.0, "ec_max": 3.0, "ph_min": 5.5, "ph_max": 6.5,
     "notes": "Verträgt höhere EC, K für Schärfe",
     "keywords": ["chili", "hot pepper"]},
    {"name": "🥦 Brokkoli", "category": "Kohlgemüse",
     "ec_min": 2.0, "ec_max": 3.0, "ph_min": 6.0, "ph_max": 6.8,
     "notes": "Hoher Ca- und S-Bedarf, Bor wichtig",
     "keywords": ["brokkoli", "broccoli"]},
    {"name": "🍃 Spinat", "category": "Blattgemüse",
     "ec_min": 1.5, "ec_max": 2.5, "ph_min": 6.0, "ph_max": 7.0,
     "notes": "Verträgt höhere EC als Salat, Fe-Bedarf beachten",
     "keywords": ["spinat", "spinach"]},
    {"name": "🌱 Koriander", "category": "Kräuter",
     "ec_min": 1.0, "ec_max": 1.8, "ph_min": 5.5, "ph_max": 6.5,
     "notes": "Schnellwachsend, moderate Ansprüche",
     "keywords": ["koriander", "cilantro"]},
]

def load_all_plants() -> list[dict]:
    """Lädt Standard- und benutzerdefinierte Pflanzen."""
    plants = list(DEFAULT_PLANTS)
    path = _get_data_dir() / "custom_plants.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                custom = json.load(f)
            plants.extend(custom)
        except json.JSONDecodeError:
            pass
    return plants

def save_custom_plant(plant: dict):
    """Speichert eine benutzerdefinierte Pflanze."""
    path = _get_data_dir() / "custom_plants.json"
    existing = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = []
    existing = [p for p in existing if p.get("name") != plant["name"]]
    existing.append(plant)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

def delete_custom_plant(name: str):
    path = _get_data_dir() / "custom_plants.json"
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        existing = json.load(f)
    existing = [p for p in existing if p.get("name") != name]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════
# Salzkosten
# ═══════════════════════════════════════════════════════════════════════

def load_salt_costs() -> dict[str, float]:
    """Lädt Salzkosten (EUR/kg) als {formula: preis}."""
    path = _get_data_dir() / "salt_costs.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}

def save_salt_costs(costs: dict[str, float]):
    path = _get_data_dir() / "salt_costs.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(costs, f, indent=2, ensure_ascii=False)

def apply_costs_to_salts():
    """Wendet gespeicherte Kosten auf die Salzdatenbank an."""
    from chemistry.salts import DEFAULT_SALTS
    costs = load_salt_costs()
    for formula, price in costs.items():
        if formula in DEFAULT_SALTS:
            DEFAULT_SALTS[formula].cost_per_kg = price


# ═══════════════════════════════════════════════════════════════════════
# Eigene Salze
# ═══════════════════════════════════════════════════════════════════════

def _salt_to_dict(s) -> dict:
    return {
        "name": s.name, "formula": s.formula, "molar_mass": s.molar_mass,
        "solubility_20": s.solubility_20, "tank": s.tank,
        "ion_contribution": s.ion_contribution, "notes": s.notes,
        "category": s.category, "cost_per_kg": s.cost_per_kg,
        "is_chelate": s.is_chelate, "fe_content_pct": s.fe_content_pct,
    }

def _dict_to_salt(d: dict):
    from chemistry.salts import Salt
    return Salt(
        name=d["name"], formula=d["formula"],
        molar_mass=d["molar_mass"], solubility_20=d["solubility_20"],
        tank=d.get("tank", "B"), ion_contribution=d.get("ion_contribution", {}),
        notes=d.get("notes", ""), category=d.get("category", "macro"),
        cost_per_kg=d.get("cost_per_kg", 0.0),
        is_chelate=d.get("is_chelate", False),
        fe_content_pct=d.get("fe_content_pct", 0.0),
    )

def load_custom_salts() -> list:
    path = _get_data_dir() / "custom_salts.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return [_dict_to_salt(d) for d in json.load(f)]
        except (json.JSONDecodeError, KeyError):
            pass
    return []

def save_custom_salt(salt):
    path = _get_data_dir() / "custom_salts.json"
    existing = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            pass
    # Update or append
    existing = [d for d in existing if d["formula"] != salt.formula]
    existing.append(_salt_to_dict(salt))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

def delete_custom_salt(formula: str):
    path = _get_data_dir() / "custom_salts.json"
    if not path.exists():
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing = [d for d in existing if d["formula"] != formula]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        pass

def register_custom_salts():
    """Registriert eigene Salze in DEFAULT_SALTS."""
    from chemistry.salts import DEFAULT_SALTS
    for salt in load_custom_salts():
        DEFAULT_SALTS[salt.formula] = salt
