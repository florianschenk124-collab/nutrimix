"""
API-Router: Salz-Datenbank, Ionen, Salzkosten.
"""

from fastapi import APIRouter, HTTPException
from api.models import SaltOut, SaltIn, SaltCostsIn, IonOut
from chemistry.salts import Salt, DEFAULT_SALTS, get_premixes, get_salts_by_category
from chemistry.ions import ALL_IONS
from database.data_manager import (
    load_custom_salts, save_custom_salt, delete_custom_salt,
    load_salt_costs, save_salt_costs, apply_costs_to_salts,
)

router = APIRouter(prefix="/api/salts", tags=["Salze"])


def _salt_to_out(s: Salt) -> SaltOut:
    return SaltOut(
        name=s.name, formula=s.formula,
        molar_mass=s.molar_mass, solubility_20=s.solubility_20,
        tank=s.tank, ion_contribution=s.ion_contribution,
        is_chelate=s.is_chelate, fe_content_pct=s.fe_content_pct,
        is_premix=s.is_premix, premix_mg_per_g=s.premix_mg_per_g,
        notes=s.notes, category=s.category, cost_per_kg=s.cost_per_kg,
        mg_ion_per_gram=s.mg_ion_per_gram(),
    )


@router.get("", response_model=list[SaltOut])
def list_salts(category: str | None = None):
    """Alle Salze, optional nach Kategorie gefiltert."""
    if category:
        salts = get_salts_by_category(category)
        return [_salt_to_out(s) for s in salts]
    return [_salt_to_out(s) for s in DEFAULT_SALTS.values()]


@router.get("/premixes", response_model=list[SaltOut])
def list_premixes():
    """Nur Premixe."""
    return [_salt_to_out(s) for s in get_premixes()]


@router.get("/{formula}", response_model=SaltOut)
def get_salt(formula: str):
    s = DEFAULT_SALTS.get(formula)
    if not s:
        raise HTTPException(404, f"Salz '{formula}' nicht gefunden")
    return _salt_to_out(s)


@router.post("", response_model=SaltOut, status_code=201)
def create_salt(data: SaltIn):
    salt = Salt(
        name=data.name, formula=data.formula,
        molar_mass=data.molar_mass, solubility_20=data.solubility_20,
        tank=data.tank, ion_contribution=data.ion_contribution,
        notes=data.notes, category=data.category,
        cost_per_kg=data.cost_per_kg,
        is_chelate=data.is_chelate, fe_content_pct=data.fe_content_pct,
    )
    save_custom_salt(salt)
    # Auch in Runtime-Registry aufnehmen
    DEFAULT_SALTS[salt.formula] = salt
    return _salt_to_out(salt)


@router.delete("/{formula}", status_code=204)
def remove_salt(formula: str):
    delete_custom_salt(formula)
    DEFAULT_SALTS.pop(formula, None)


# ── Salzkosten ──────────────────────────────────────────────────

@router.get("/costs/all")
def get_costs() -> dict[str, float]:
    return load_salt_costs()


@router.put("/costs")
def update_costs(data: SaltCostsIn):
    save_salt_costs(data.costs)
    apply_costs_to_salts()
    return {"status": "ok"}


# ── Ionen ───────────────────────────────────────────────────────

ions_router = APIRouter(prefix="/api/ions", tags=["Ionen"])


@ions_router.get("", response_model=list[IonOut])
def list_ions():
    return [
        IonOut(
            symbol=ion.symbol, display=ion.display, element=ion.element,
            molar_mass=ion.molar_mass, ion_molar_mass=ion.ion_molar_mass,
            charge=ion.charge,
        )
        for ion in ALL_IONS
    ]
