"""
Rechner-View: Hauptfunktion zum Berechnen von Stammlösungen.
Vollständig verknüpft mit dem Chemistry-Backend (10-Schritt-Verfahren).
"""

import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.recipes import NutrientRecipe
from chemistry.water import WaterProfile, subtract_water
from chemistry.solver import solve, SolverResult, format_result_text
from chemistry.concentrate import calculate_concentrate, suggest_max_concentrate_factor
from chemistry.ec_estimator import estimate_ec, ec_rating
from chemistry.ratios import check_ratios
from chemistry.ab_split import validate_ab_split
from chemistry.ions import ION_BY_SYMBOL, mmol_to_mg, mg_to_mmol
from database.data_manager import (
    load_all_recipes, load_all_water_profiles, load_settings,
)
from ui.locales import t, td, salt_name


class CalculatorView(BaseView):
    def __init__(self, parent):
        super().__init__(
            parent,
            title=t("calc.title"),
            subtitle=t("calc.subtitle"),
        )

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)

        # Daten laden
        self.recipes = load_all_recipes()
        self.water_profiles = load_all_water_profiles()
        self.settings = load_settings()

        # Linke Spalte: Eingaben
        left_col = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        left_col.grid_columnconfigure(0, weight=1)

        self._build_input_section(left_col)

        # Rechte Spalte: Ergebnisse
        right_col = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nswe", padx=(8, 0))
        right_col.grid_columnconfigure(0, weight=1)

        self._build_results_section(right_col)

    def refresh_data(self):
        """Daten neu laden (nach Änderungen in anderen Views)."""
        self.recipes = load_all_recipes()
        self.water_profiles = load_all_water_profiles()
        self.settings = load_settings()
        self.recipe_dropdown.configure(values=list(self.recipes.keys()))
        self.water_dropdown.configure(values=list(self.water_profiles.keys()))

    # ─── Eingabebereich ───────────────────────────────────────────────

    def _build_input_section(self, parent):
        # ── Rezeptauswahl ──
        card_recipe = self._create_card(parent, title=t("calc.card_recipe"))
        card_recipe.pack(fill="x", pady=(0, 8))

        recipe_names = list(self.recipes.keys())
        self.recipe_dropdown = self._create_labeled_dropdown(
            card_recipe, label=t("c.recipe"),
            values=recipe_names, default=recipe_names[0] if recipe_names else "",
        )
        self.recipe_dropdown.configure(command=self._on_recipe_changed)

        self.unit_dropdown = self._create_labeled_dropdown(
            card_recipe, label=t("calc.units"),
            values=["mg/L (ppm)", "mmol/L"],
            default=self.settings.get("default_unit", "mg/L (ppm)"),
        )
        self.unit_dropdown.configure(command=self._on_unit_changed)

        # Rezept-Vorschau
        self.recipe_preview = ctk.CTkTextbox(
            card_recipe, height=130,
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8,
        )
        self.recipe_preview.pack(fill="x", padx=15, pady=(5, 12))

        # ── Wasserprofil ──
        card_water = self._create_card(parent, title=t("calc.card_water"))
        card_water.pack(fill="x", pady=(0, 8))

        water_names = list(self.water_profiles.keys())
        self.water_dropdown = self._create_labeled_dropdown(
            card_water, label=t("calc.profile"),
            values=water_names, default=water_names[0] if water_names else "",
        )
        self.water_dropdown.configure(command=self._on_water_changed)

        self.water_info = ctk.CTkLabel(
            card_water, text="", font=ctk.CTkFont(size=11),
            text_color="gray50", wraplength=350, justify="left",
        )
        self.water_info.pack(padx=15, pady=(0, 12), anchor="w")

        # ── Parameter ──
        card_params = self._create_card(parent, title=t("calc.card_params"))
        card_params.pack(fill="x", pady=(0, 8))

        self.entry_volume = self._create_labeled_entry(
            card_params, label=t("calc.target_vol"),
            placeholder=str(self.settings.get("default_volume", 1000)),
        )
        self.entry_concentrate = self._create_labeled_entry(
            card_params, label=t("calc.conc_factor"),
            placeholder=str(self.settings.get("default_concentrate_factor", 100)),
        )

        # ── Erweiterte Optionen ──
        card_options = self._create_card(parent, title=t("calc.card_salts"))
        card_options.pack(fill="x", pady=(0, 8))

        self.fe_dropdown = self._create_labeled_dropdown(
            card_options, label=t("calc.fe_chelate"),
            values=["Fe-DTPA", "Fe-EDTA", "Fe-EDDHA", "Fe-HBED"],
            default=self.settings.get("fe_chelate", "Fe-DTPA"),
        )
        self.nh4_dropdown = self._create_labeled_dropdown(
            card_options, label=t("calc.nh4_source"),
            values=["NH4NO3", "MAP", "DAP"],
            default=self.settings.get("nh4_source", "NH4NO3"),
        )
        self.p_dropdown = self._create_labeled_dropdown(
            card_options, label=t("calc.p_source"),
            values=["KH2PO4", "MAP", "H3PO4"],
            default=self.settings.get("p_source", "KH2PO4"),
        )

        # Mikronährstoff-Quelle
        from chemistry.salts import get_premixes
        premix_names = ["individual"] + [p.formula for p in get_premixes()]
        self.micro_dropdown = self._create_labeled_dropdown(
            card_options, label=t("calc.micro_source"),
            values=premix_names,
            default=self.settings.get("micro_source", "individual"),
        )

        # Dosierverhältnis
        self.dose_ratio_entry = self._create_labeled_entry(
            card_options, label=t("c.dose_ratio"),
            placeholder=self.settings.get("dose_ratio", "1:1"),
        )
        ctk.CTkFrame(card_options, fg_color="transparent", height=8).pack()

        # ── Berechnen-Button ──
        self.btn_calculate = ctk.CTkButton(
            parent, text=t("calc.btn"),
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45, corner_radius=10,
            command=self._on_calculate,
        )
        self.btn_calculate.pack(fill="x", pady=(5, 10))

        # Initial: Vorschau anzeigen
        self._on_recipe_changed(recipe_names[0] if recipe_names else "")
        self._on_water_changed(water_names[0] if water_names else "")

    # ─── Ergebnisbereich ──────────────────────────────────────────────

    def _build_results_section(self, parent):

        # ── Tank A ──
        card_a = self._create_card(parent, title=t("calc.tank_a"))
        card_a.pack(fill="x", pady=(0, 8))
        self.result_a = ctk.CTkTextbox(
            card_a, height=140, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8,
        )
        self.result_a.pack(fill="x", padx=15, pady=(5, 12))

        # ── Tank B ──
        card_b = self._create_card(parent, title=t("calc.tank_b"))
        card_b.pack(fill="x", pady=(0, 8))
        self.result_b = ctk.CTkTextbox(
            card_b, height=180, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8,
        )
        self.result_b.pack(fill="x", padx=15, pady=(5, 12))

        # ── Soll/Ist-Vergleich ──
        card_delta = self._create_card(parent, title=t("calc.target_actual"))
        card_delta.pack(fill="x", pady=(0, 8))
        self.result_delta = ctk.CTkTextbox(
            card_delta, height=220, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8,
        )
        self.result_delta.pack(fill="x", padx=15, pady=(5, 12))

        # ── Zusammenfassung ──
        card_summary = self._create_card(parent, title=t("calc.summary"))
        card_summary.pack(fill="x", pady=(0, 8))

        summary_grid = ctk.CTkFrame(card_summary, fg_color="transparent")
        summary_grid.pack(fill="x", padx=15, pady=(5, 5))

        labels = t("calc.summary_labels")
        self.summary_values = []
        for i, lbl in enumerate(labels):
            ctk.CTkLabel(summary_grid, text=lbl, font=ctk.CTkFont(size=12),
                         anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            val = ctk.CTkLabel(summary_grid, text="–",
                               font=ctk.CTkFont(size=12, weight="bold"),
                               text_color="gray50", anchor="w")
            val.grid(row=i, column=1, sticky="w", padx=(15, 0), pady=2)
            self.summary_values.append(val)

        # ── Ratios ──
        card_ratios = self._create_card(parent, title=t("calc.ratios"))
        card_ratios.pack(fill="x", pady=(0, 8))
        self.result_ratios = ctk.CTkTextbox(
            card_ratios, height=120, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8,
        )
        self.result_ratios.pack(fill="x", padx=15, pady=(5, 12))

        # ── Warnungen ──
        card_warn = self._create_card(parent, title=t("calc.warnings"))
        card_warn.pack(fill="x", pady=(0, 8))
        self.result_warnings = ctk.CTkTextbox(
            card_warn, height=100, font=ctk.CTkFont(size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8,
        )
        self.result_warnings.pack(fill="x", padx=15, pady=(5, 12))

        # ── Berechnungsschritte ──
        card_steps = self._create_card(parent, title=t("calc.protocol"))
        card_steps.pack(fill="x", pady=(0, 8))
        self.result_steps = ctk.CTkTextbox(
            card_steps, height=160, font=ctk.CTkFont(family="Consolas", size=10),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8,
        )
        self.result_steps.pack(fill="x", padx=15, pady=(5, 12))

    # ─── Callbacks ────────────────────────────────────────────────────

    def _on_recipe_changed(self, name: str):
        recipe = self.recipes.get(name)
        if not recipe:
            return
        self._update_recipe_preview(recipe)

    def _on_unit_changed(self, unit: str):
        name = self.recipe_dropdown.get()
        recipe = self.recipes.get(name)
        if recipe:
            self._update_recipe_preview(recipe)

    def _on_water_changed(self, name: str):
        profile = self.water_profiles.get(name)
        if not profile:
            return
        info = (f"Ca: {profile.ca:.0f}  Mg: {profile.mg:.0f}  "
                f"Na: {profile.na:.0f}  K: {profile.k:.0f}  "
                f"Cl: {profile.cl:.0f}  SO₄: {profile.so4:.0f}  "
                f"HCO₃: {profile.hco3:.0f}  EC: {profile.ec:.2f} mS/cm  "
                f"pH: {profile.ph:.1f}")
        self.water_info.configure(text=info)

    def _update_recipe_preview(self, recipe: NutrientRecipe):
        """Zeigt die Rezeptvorschau in der gewählten Einheit."""
        unit = self.unit_dropdown.get()
        use_mmol = "mmol" in unit

        self.recipe_preview.configure(state="normal")
        self.recipe_preview.delete("1.0", "end")

        if use_mmol:
            d = recipe.as_mmol_dict()
            fmt = ".3f"
            unit_label = "mmol/L"
        else:
            d = recipe.as_mg_dict()
            fmt = ".1f"
            unit_label = "mg/L"

        lines = [f"{recipe.description}  ({unit_label})\n"]
        # Makro
        for sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4"]:
            val = d.get(sym, 0)
            if val > 0:
                display = ION_BY_SYMBOL[sym].display
                lines.append(f"  {display:<8} {val:{fmt}}")
        lines.append("")
        # Mikro
        for sym in ["Fe", "Mn", "Zn", "Cu", "B", "Mo"]:
            val = d.get(sym, 0)
            if val > 0:
                display = ION_BY_SYMBOL[sym].display
                lines.append(f"  {display:<8} {val:{fmt}}")

        if recipe.ec_target > 0:
            lines.append(f"\n  {t('growth.ec_target')}: {recipe.ec_target:.1f} mS/cm  "
                         f"pH: {recipe.ph_min}–{recipe.ph_max}")

        self.recipe_preview.insert("1.0", "\n".join(lines))
        self.recipe_preview.configure(state="disabled")

    def _set_textbox(self, tb: ctk.CTkTextbox, text: str):
        """Hilfsfunktion: Text in eine disabled Textbox schreiben."""
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.insert("1.0", text)
        tb.configure(state="disabled")

    def _get_float(self, entry: ctk.CTkEntry, default: float) -> float:
        """Holt einen Float-Wert aus einem Entry-Feld."""
        val = entry.get().strip()
        if not val:
            val = entry.cget("placeholder_text")
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    # ─── Hauptberechnung ──────────────────────────────────────────────

    def _on_calculate(self):
        """Führt die vollständige Berechnung durch."""

        # Parameter sammeln
        recipe_name = self.recipe_dropdown.get()
        water_name = self.water_dropdown.get()
        recipe = self.recipes.get(recipe_name)
        water = self.water_profiles.get(water_name)

        if not recipe or not water:
            self._set_textbox(self.result_warnings, t("c.not_found"))
            return

        volume_l = self._get_float(self.entry_volume, 1000.0)
        concentrate_factor = self._get_float(self.entry_concentrate, 100.0)
        fe_chelate = self.fe_dropdown.get()
        nh4_source = self.nh4_dropdown.get()
        p_source = self.p_dropdown.get()
        micro_source = self.micro_dropdown.get()
        dose_ratio = self.dose_ratio_entry.get().strip()
        if not dose_ratio:
            dose_ratio = self.dose_ratio_entry.cget("placeholder_text") or "1:1"

        # Kosten anwenden
        from database.data_manager import apply_costs_to_salts
        apply_costs_to_salts()

        # 1. Wasserabzug
        target_mg = recipe.as_mg_dict()
        adjusted_mg, water_warnings = subtract_water(target_mg, water)

        # 2. Solver
        result = solve(
            adjusted_mg, volume_l, concentrate_factor,
            fe_chelate=fe_chelate,
            nh4_source=nh4_source,
            p_source=p_source,
            micro_source=micro_source,
            dose_ratio=dose_ratio,
        )

        # 3. Löslichkeitsprüfung
        conc_result = calculate_concentrate(result, volume_l, concentrate_factor)
        max_factor = suggest_max_concentrate_factor(result, volume_l)

        # 4. EC-Schätzung
        ec_method = self.settings.get("ec_method", "ionic")
        ec_val = estimate_ec(result.achieved_mg, method=ec_method)

        # 5. A/B-Validierung
        ab_warnings = validate_ab_split(
            [sr.salt for sr in result.tank_a],
            [sr.salt for sr in result.tank_b],
        )

        # 6. Verhältnisse
        total_mg = dict(result.achieved_mg)
        water_mg_dict = water.as_mg_dict()
        for sym in ["Ca", "Mg", "K", "SO4", "NO3"]:
            if sym in water_mg_dict and sym in total_mg:
                total_mg[sym] += water_mg_dict.get(sym, 0)
        ratio_results = check_ratios(total_mg)

        # ── Ergebnisse anzeigen ──

        has_costs = result.total_cost > 0

        # Tank A
        lines_a = []
        if result.tank_a:
            hdr = f"{t('calc.col_salt'):<30} {'g/L':>8} {t('calc.col_g_total'):>9} {t('calc.col_g_tank'):>8}"
            if has_costs:
                hdr += f" {'€':>7}"
            lines_a.append(hdr)
            lines_a.append("─" * (58 + (8 if has_costs else 0)))
            for sr in result.tank_a:
                line = f"{salt_name(sr.salt.name):<30} {sr.g_per_l:>8.4f} {sr.g_total:>9.2f} {sr.g_concentrate:>8.2f}"
                if has_costs:
                    line += f" {sr.cost_total:>7.4f}" if sr.cost_total > 0 else f" {'–':>7}"
                lines_a.append(line)
        else:
            lines_a.append(f"– {t('calc.tank_a')}: –")
        self._set_textbox(self.result_a, "\n".join(lines_a))

        # Tank B
        lines_b = []
        if result.tank_b:
            hdr = f"{t('calc.col_salt'):<30} {'g/L':>8} {t('calc.col_g_total'):>9} {t('calc.col_g_tank'):>8}"
            if has_costs:
                hdr += f" {'€':>7}"
            lines_b.append(hdr)
            lines_b.append("─" * (58 + (8 if has_costs else 0)))
            for sr in result.tank_b:
                line = f"{salt_name(sr.salt.name):<30} {sr.g_per_l:>8.4f} {sr.g_total:>9.2f} {sr.g_concentrate:>8.2f}"
                if has_costs:
                    line += f" {sr.cost_total:>7.4f}" if sr.cost_total > 0 else f" {'–':>7}"
                lines_b.append(line)
        else:
            lines_b.append(f"– {t('calc.tank_b')}: –")
        self._set_textbox(self.result_b, "\n".join(lines_b))

        # Soll/Ist
        lines_d = []
        lines_d.append(f"{'Ion':<10} {t('b.target'):>8} {t('b.actual'):>8} {'Δ':>8} mg/L")
        lines_d.append("─" * 38)
        for sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4"]:
            soll = adjusted_mg.get(sym, 0)
            ist = result.achieved_mg.get(sym, 0)
            delta = result.delta_mg.get(sym, 0)
            if soll > 0 or ist > 0:
                display = ION_BY_SYMBOL[sym].display
                marker = " ⚠️" if abs(delta) > 5 else ""
                lines_d.append(
                    f"{display:<10} {soll:>8.1f} {ist:>8.1f} {delta:>+8.1f}{marker}")
        # Mikros (eigene Sektion)
        has_micros = any(adjusted_mg.get(s, 0) > 0 for s in ["Fe", "Mn", "Zn", "Cu", "B", "Mo"])
        if has_micros:
            lines_d.append("─" * 38)
            for sym in ["Fe", "Mn", "Zn", "Cu", "B", "Mo"]:
                soll = adjusted_mg.get(sym, 0)
                ist = result.achieved_mg.get(sym, 0)
                delta = result.delta_mg.get(sym, 0)
                if soll > 0 or ist > 0:
                    display = ION_BY_SYMBOL[sym].display if sym in ION_BY_SYMBOL else sym
                    # Mikros: kleinere Toleranz
                    marker = " ⚠️" if abs(delta) > max(0.5, soll * 0.2) else ""
                    lines_d.append(
                        f"{display:<10} {soll:>8.3f} {ist:>8.3f} {delta:>+8.3f}{marker}")
            if micro_source != "individual":
                premix_name = next(
                    (s.salt.name for s in result.all_salts if s.salt.is_premix), micro_source)
                lines_d.append(f"\n{t('calc.micros_via')} {premix_name}")
        self._set_textbox(self.result_delta, "\n".join(lines_d))

        # Zusammenfassung
        ec_text = ec_rating(ec_val, recipe.ec_target)
        self.summary_values[0].configure(text=ec_text,
            text_color="#4CAF50" if "✅" in ec_text else "#e8a838")

        self.summary_values[1].configure(
            text=f"{recipe.ph_min} – {recipe.ph_max}", text_color="white")

        if conc_result.all_ok:
            self.summary_values[2].configure(text=t("calc.all_soluble"),
                                             text_color="#4CAF50")
        else:
            self.summary_values[2].configure(
                text=f"⛔ {len(conc_result.critical_checks)} {t('calc.salts_exceed')}",
                text_color="#e74c3c")

        self.summary_values[3].configure(text=f"{max_factor:.0f}x",
                                         text_color="white")

        # Kosten
        if result.total_cost > 0:
            cpl = result.cost_per_liter()
            self.summary_values[4].configure(
                text=f"{result.total_cost:.4f} € {t('calc.col_g_total')} | {cpl:.5f} €/L | {cpl*10:.4f} €/10L",
                text_color="#e8a838")
        else:
            self.summary_values[4].configure(text=t("calc.no_prices"),
                                             text_color="gray50")

        # Dosierverhältnis
        self.summary_values[5].configure(
            text=f"{result.dose_ratio_a:.0f} : {result.dose_ratio_b:.0f}",
            text_color="white")

        # Ratios
        lines_r = []
        for r in ratio_results:
            lines_r.append(
                f"{r.status_icon} {r.name:<12} "
                f"{t('b.actual')}: {r.actual:>5.2f}:1  "
                f"{t('b.target')}: {r.target_str}")
        self._set_textbox(self.result_ratios, "\n".join(lines_r))

        # Warnungen
        all_warnings = water_warnings + result.warnings + conc_result.warnings + ab_warnings
        ratio_warnings = [r.warning for r in ratio_results if r.warning]
        all_warnings += ratio_warnings

        if all_warnings:
            self._set_textbox(self.result_warnings, "\n".join(
                f"{i+1}. {w}" for i, w in enumerate(all_warnings)))
        else:
            self._set_textbox(self.result_warnings, t("c.no_warnings"))

        # Schritte
        if result.steps:
            self._set_textbox(self.result_steps, "\n".join(
                f"→ {s}" for s in result.steps))
        else:
            self._set_textbox(self.result_steps, t("calc.no_steps"))
