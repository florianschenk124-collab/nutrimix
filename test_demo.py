#!/usr/bin/env python3
"""
Demo/Test: Vollständige Berechnung einer Nährlösung.

Beispiel: Hoagland-Rezept mit Dresdner Leitungswasser,
100-fach konzentrierte Stammlösung, 1000 L Endvolumen.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from chemistry.recipes import DEFAULT_RECIPES, get_recipe
from chemistry.water import DEFAULT_WATER_PROFILES, subtract_water
from chemistry.solver import solve, format_result_text
from chemistry.concentrate import calculate_concentrate, suggest_max_concentrate_factor
from chemistry.ec_estimator import estimate_ec, ec_rating
from chemistry.ab_split import validate_ab_split
from chemistry.ions import ION_BY_SYMBOL, mmol_to_mg, mg_to_mmol
from chemistry.ratios import check_ratios, format_ratio_summary


def print_separator(title: str = ""):
    print(f"\n{'═' * 70}")
    if title:
        print(f"  {title}")
        print(f"{'═' * 70}")


def main():
    # ── Parameter ──
    recipe_name = "Hoagland & Arnon"
    water_name = "Leitungswasser Dresden (Beispiel)"
    volume_l = 1000.0
    concentrate_factor = 100.0
    fe_chelate = "Fe-DTPA"

    # ── Rezept laden ──
    recipe = get_recipe(recipe_name)
    water = DEFAULT_WATER_PROFILES[water_name]

    print_separator("NutrientMixer – Berechnungs-Demo")
    print(f"\n  Rezept:            {recipe.name}")
    print(f"  Beschreibung:      {recipe.description}")
    print(f"  Wasserprofil:      {water.name}")
    print(f"  Endvolumen:        {volume_l:.0f} L")
    print(f"  Konzentratfaktor:  {concentrate_factor:.0f}x")
    print(f"  Fe-Chelat:         {fe_chelate}")

    # ── Zielkonzentrationen anzeigen ──
    print_separator("Ziel-Ionenkonzentrationen (Rezept)")
    target_mg = recipe.as_mg_dict()
    target_mmol = recipe.as_mmol_dict()

    print(f"\n  {'Ion':<12} {'mg/L':>10} {'mmol/L':>10}")
    print(f"  {'─' * 34}")
    for ion_sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4",
                     "Fe", "Mn", "Zn", "Cu", "B", "Mo"]:
        mg = target_mg.get(ion_sym, 0)
        mmol = target_mmol.get(ion_sym, 0)
        if mg > 0:
            display = ION_BY_SYMBOL[ion_sym].display
            print(f"  {display:<12} {mg:>10.2f} {mmol:>10.4f}")

    # ── Wasseranalyse anzeigen ──
    print_separator("Wasseranalyse")
    water_mg = water.as_mg_dict()
    print(f"\n  {'Ion':<12} {'mg/L':>10}")
    print(f"  {'─' * 24}")
    for ion_sym, val in water_mg.items():
        if val > 0:
            display = ION_BY_SYMBOL.get(ion_sym, None)
            name = display.display if display else ion_sym
            print(f"  {name:<12} {val:>10.2f}")
    print(f"  {'─' * 24}")
    print(f"  {'EC':<12} {water.ec:>10.2f} mS/cm")
    print(f"  {'pH':<12} {water.ph:>10.1f}")

    # ── Wasserabzug ──
    print_separator("Wasserabzug (Ziel – Wasser)")
    adjusted_mg, water_warnings = subtract_water(target_mg, water)

    print(f"\n  {'Ion':<12} {'Ziel':>8} {'Wasser':>8} {'Bedarf':>8} mg/L")
    print(f"  {'─' * 40}")
    for ion_sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4", "Fe"]:
        original = target_mg.get(ion_sym, 0)
        adjusted = adjusted_mg.get(ion_sym, 0)
        water_val = original - adjusted
        if original > 0 or water_val > 0:
            display = ION_BY_SYMBOL[ion_sym].display
            print(f"  {display:<12} {original:>8.1f} {water_val:>8.1f} {adjusted:>8.1f}")

    for w in water_warnings:
        print(f"\n  {w}")

    # ── Solver: Salzmengen berechnen ──
    print_separator("Berechnete Salzmengen (10-Schritt-Verfahren)")
    result = solve(adjusted_mg, volume_l, concentrate_factor, fe_chelate,
                   nh4_source="NH4NO3", p_source="KH2PO4")

    # Berechnungsschritte anzeigen
    print(f"\n  Berechnungsschritte:")
    for step in result.steps:
        print(f"    → {step}")

    print(f"\n  ── Tank A (Calcium / Eisen) ──")
    print(f"  {'Salz':<35} {'g/L':>10} {'g gesamt':>12} {'g/Tank':>10}")
    print(f"  {'─' * 70}")
    for sr in result.tank_a:
        print(f"  {format_result_text(sr)}")

    print(f"\n  ── Tank B (Sulfate / Phosphate / Mikro) ──")
    print(f"  {'Salz':<35} {'g/L':>10} {'g gesamt':>12} {'g/Tank':>10}")
    print(f"  {'─' * 70}")
    for sr in result.tank_b:
        print(f"  {format_result_text(sr)}")

    # ── Ist-Konzentrationen ──
    print_separator("Soll/Ist-Vergleich (erreichte Konzentrationen)")
    print(f"\n  {'Ion':<12} {'Soll mg/L':>10} {'Ist mg/L':>10} {'Δ mg/L':>10}")
    print(f"  {'─' * 44}")
    for ion_sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4"]:
        soll = adjusted_mg.get(ion_sym, 0)
        ist = result.achieved_mg.get(ion_sym, 0)
        delta = result.delta_mg.get(ion_sym, 0)
        if soll > 0 or ist > 0:
            display = ION_BY_SYMBOL[ion_sym].display
            marker = " ⚠️" if abs(delta) > 5 else ""
            print(f"  {display:<12} {soll:>10.1f} {ist:>10.1f} {delta:>+10.1f}{marker}")

    # ── Löslichkeitsprüfung ──
    print_separator("Löslichkeitsprüfung (Stammlösung)")
    conc_result = calculate_concentrate(result, volume_l, concentrate_factor)

    print(f"\n  Tankvolumen: {conc_result.tank_a_volume_l:.1f} L (A), "
          f"{conc_result.tank_b_volume_l:.1f} L (B)")
    print(f"\n  {'Salz':<30} {'g/L Konz.':>10} {'Lösl.':>8} {'Sättigung':>10} {'Status':>8}")
    print(f"  {'─' * 70}")
    for check in conc_result.checks:
        status = "✅" if check.is_ok else "⛔"
        if check.is_ok and check.saturation_pct > 70:
            status = "⚠️"
        print(
            f"  {check.salt_name:<30} "
            f"{check.g_per_l_concentrate:>10.1f} "
            f"{check.solubility_limit:>8.0f} "
            f"{check.saturation_pct:>9.1f}% "
            f"{status:>8}"
        )

    max_factor = suggest_max_concentrate_factor(result, volume_l)
    print(f"\n  Maximaler Konzentratfaktor: {max_factor:.0f}x")

    # ── A/B-Validierung ──
    ab_warnings = validate_ab_split(
        [sr.salt for sr in result.tank_a],
        [sr.salt for sr in result.tank_b],
    )
    if ab_warnings:
        print(f"\n  A/B-Trennung Warnungen:")
        for w in ab_warnings:
            print(f"    {w}")
    else:
        print(f"\n  ✅ A/B-Trennung korrekt")

    # ── EC-Schätzung ──
    print_separator("EC-Schätzung")
    ec_simple = estimate_ec(result.achieved_mg, method="simple")
    ec_ionic = estimate_ec(result.achieved_mg, method="ionic")

    print(f"\n  Einfache Methode:      {ec_simple:.2f} mS/cm")
    print(f"  Ionenspezifisch:       {ec_ionic:.2f} mS/cm")
    print(f"  Bewertung:             {ec_rating(ec_ionic, recipe.ec_target)}")

    # ── Nährstoff-Verhältnisse prüfen ──
    print_separator("Kritische Nährstoff-Verhältnisse (5 Ratios)")
    # Verwende die Ist-Konzentrationen + Wasseranteile für realistische Verhältnisse
    total_achieved_mg = dict(result.achieved_mg)
    # Wasser-Ionen draufrechnen (die sind ja in der Endlösung mit drin)
    water_mg = water.as_mg_dict()
    for ion_sym in ["Ca", "Mg", "K", "SO4", "NO3"]:
        w_key = ion_sym
        if w_key in water_mg and ion_sym in total_achieved_mg:
            total_achieved_mg[ion_sym] += water_mg[w_key]

    ratio_results = check_ratios(total_achieved_mg)
    print(f"\n{format_ratio_summary(ratio_results)}")

    # ── Warnungen ──
    all_warnings = water_warnings + result.warnings + conc_result.warnings
    ratio_warnings = [r.warning for r in ratio_results if r.warning]
    all_warnings += ratio_warnings
    if all_warnings:
        print_separator("Alle Warnungen")
        for i, w in enumerate(all_warnings, 1):
            print(f"  {i}. {w}")

    print_separator()
    print("  Berechnung abgeschlossen.\n")


if __name__ == "__main__":
    main()
