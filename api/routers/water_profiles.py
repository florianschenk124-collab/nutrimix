"""
API-Router: Wasserprofile (Standard + benutzerdefiniert).
"""

from fastapi import APIRouter, HTTPException
from api.models import WaterProfileIn, WaterProfileOut
from chemistry.water import WaterProfile, DEFAULT_WATER_PROFILES
from database.data_manager import (
    load_all_water_profiles, save_custom_water_profile,
    delete_custom_water_profile,
)

router = APIRouter(prefix="/api/water-profiles", tags=["Wasserprofile"])


def _is_custom(name: str) -> bool:
    return name not in DEFAULT_WATER_PROFILES


def _wp_to_out(w: WaterProfile) -> WaterProfileOut:
    return WaterProfileOut(
        name=w.name, ca=w.ca, mg=w.mg, na=w.na, k=w.k,
        cl=w.cl, so4=w.so4, hco3=w.hco3, no3=w.no3, fe=w.fe,
        ec=w.ec, ph=w.ph,
        is_custom=_is_custom(w.name),
    )


@router.get("", response_model=list[WaterProfileOut])
def list_profiles():
    profiles = load_all_water_profiles()
    return [_wp_to_out(w) for w in profiles.values()]


@router.get("/{name}", response_model=WaterProfileOut)
def get_profile(name: str):
    profiles = load_all_water_profiles()
    w = profiles.get(name)
    if not w:
        raise HTTPException(404, f"Wasserprofil '{name}' nicht gefunden")
    return _wp_to_out(w)


@router.post("", response_model=WaterProfileOut, status_code=201)
def create_profile(data: WaterProfileIn):
    wp = WaterProfile(
        name=data.name, ca=data.ca, mg=data.mg, na=data.na, k=data.k,
        cl=data.cl, so4=data.so4, hco3=data.hco3, no3=data.no3, fe=data.fe,
        ec=data.ec, ph=data.ph,
    )
    save_custom_water_profile(wp)
    return _wp_to_out(wp)


@router.delete("/{name}", status_code=204)
def remove_profile(name: str):
    delete_custom_water_profile(name)
