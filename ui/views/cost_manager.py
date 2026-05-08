"""
Kosten-Manager: Salzpreise eintragen und Rezeptkosten berechnen.
"""

import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.salts import DEFAULT_SALTS
from chemistry.recipes import DEFAULT_RECIPES
from chemistry.water import DEFAULT_WATER_PROFILES
from chemistry.solver import solve
from chemistry.water import subtract_water
from database.data_manager import (
    load_salt_costs, save_salt_costs, apply_costs_to_salts,
    load_all_recipes, load_all_water_profiles, load_settings,
)
from ui.locales import t, salt_name, warn_fmt


class CostManagerView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("costs.title"),
                         subtitle=t("costs.subtitle"))

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Links: Salzpreise
        left = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        left.grid_columnconfigure(0, weight=1)
        self._build_cost_editor(left)

        # Rechts: Kostenrechner
        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))
        right.grid_columnconfigure(0, weight=1)
        self._build_cost_calculator(right)

    def refresh_data(self):
        pass

    # ─── Salzpreise ────────────────────────────────────────────────────

    def _build_cost_editor(self, parent):
        card = self._create_card(parent, title=t("costs.card_prices"))
        card.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(card, text=t("costs.prices_hint"),
                     font=ctk.CTkFont(size=11), text_color="gray50").pack(padx=15, pady=(5, 8), anchor="w")

        # Preise laden
        self.costs = load_salt_costs()
        self.cost_entries = {}

        # Nach Kategorie gruppieren
        categories = {
            t("costs.macro_salts"): [s for s in DEFAULT_SALTS.values() if s.category == "macro"],
            t("costs.cat_chelates"): [s for s in DEFAULT_SALTS.values() if s.category == "chelate"],
            t("costs.micro_nutrients"): [s for s in DEFAULT_SALTS.values() if s.category == "micro"],
            t("costs.cat_premixes"): [s for s in DEFAULT_SALTS.values() if s.category == "premix"],
        }

        for cat_name, salts in categories.items():
            if not salts:
                continue
            cat_label = ctk.CTkLabel(card, text=f"── {cat_name} ──",
                                     font=ctk.CTkFont(size=11, weight="bold"),
                                     text_color="#4CAF50")
            cat_label.pack(padx=15, pady=(10, 4), anchor="w")

            for salt in salts:
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=1)
                row.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(row, text=salt_name(salt.name), font=ctk.CTkFont(size=11),
                             anchor="w").grid(row=0, column=0, sticky="w")

                entry = ctk.CTkEntry(row, width=80, placeholder_text="0.00",
                                     font=ctk.CTkFont(size=11))
                entry.grid(row=0, column=1, padx=(5, 0))
                ctk.CTkLabel(row, text="€/kg", font=ctk.CTkFont(size=10),
                             text_color="gray50").grid(row=0, column=2, padx=(3, 0))

                # Vorhandenen Preis eintragen
                if salt.formula in self.costs:
                    entry.insert(0, f"{self.costs[salt.formula]:.2f}")

                self.cost_entries[salt.formula] = entry

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

        self.cost_status = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12))
        self.cost_status.pack(padx=15, pady=(5, 5))

        ctk.CTkButton(card, text=t("costs.btn_save"),
                      font=ctk.CTkFont(size=13, weight="bold"), height=40,
                      command=self._save_costs).pack(fill="x", padx=15, pady=(0, 12))

    def _save_costs(self):
        costs = {}
        for formula, entry in self.cost_entries.items():
            val = entry.get().strip().replace(",", ".")
            if val:
                try:
                    price = float(val)
                    if price > 0:
                        costs[formula] = price
                except ValueError:
                    pass
        save_salt_costs(costs)
        apply_costs_to_salts()
        self.costs = costs
        count = len([v for v in costs.values() if v > 0])
        self.cost_status.configure(text=warn_fmt("d.prices_saved", count), text_color="#4CAF50")

    # ─── Kostenrechner ────────────────────────────────────────────────

    def _build_cost_calculator(self, parent):
        card_calc = self._create_card(parent, title=t("costs.card_calc"))
        card_calc.pack(fill="x", pady=(0, 8))

        recipes = load_all_recipes()
        water_profiles = load_all_water_profiles()

        self.calc_recipe = self._create_labeled_dropdown(
            card_calc, label=t("c.recipe"),
            values=list(recipes.keys()),
            default=list(recipes.keys())[0] if recipes else "",
        )
        self.calc_water = self._create_labeled_dropdown(
            card_calc, label=t("c.water_profile"),
            values=list(water_profiles.keys()),
            default="Osmosewasser",
        )
        self.calc_volume = self._create_labeled_entry(
            card_calc, label=t("c.volume_l"), placeholder="10",
        )
        self.calc_factor = self._create_labeled_entry(
            card_calc, label=t("c.conc_factor"), placeholder="100",
        )

        ctk.CTkFrame(card_calc, fg_color="transparent", height=8).pack()

        ctk.CTkButton(card_calc, text=t("costs.btn_calc"),
                      font=ctk.CTkFont(size=13, weight="bold"), height=40,
                      command=self._calculate_cost).pack(fill="x", padx=15, pady=(0, 12))

        # Ergebnis
        card_result = self._create_card(parent, title=t("costs.card_result"))
        card_result.pack(fill="x", pady=(0, 8))

        self.cost_result = ctk.CTkTextbox(
            card_result, height=300, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8,
        )
        self.cost_result.pack(fill="x", padx=15, pady=(5, 12))

        # Schnellvergleich
        card_compare = self._create_card(parent, title=t("costs.card_compare"))
        card_compare.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(card_compare, text=t("costs.btn_compare"),
                      font=ctk.CTkFont(size=12), height=35,
                      command=self._compare_all).pack(fill="x", padx=15, pady=(8, 5))

        self.compare_result = ctk.CTkTextbox(
            card_compare, height=200, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8,
        )
        self.compare_result.pack(fill="x", padx=15, pady=(5, 12))

    def _get_float(self, entry, default):
        try:
            v = entry.get().strip()
            return float(v) if v else default
        except ValueError:
            return default

    def _set_tb(self, tb, text):
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.insert("1.0", text)
        tb.configure(state="disabled")

    def _calculate_cost(self):
        apply_costs_to_salts()
        recipes = load_all_recipes()
        water_profiles = load_all_water_profiles()
        settings = load_settings()

        recipe = recipes.get(self.calc_recipe.get())
        water = water_profiles.get(self.calc_water.get())
        if not recipe or not water:
            self._set_tb(self.cost_result, t("d.recipe_not_found2"))
            return

        volume_l = self._get_float(self.calc_volume, 10.0)
        factor = self._get_float(self.calc_factor, 100.0)

        target = recipe.as_mg_dict()
        adjusted, _ = subtract_water(target, water)
        result = solve(adjusted, volume_l, factor,
                       fe_chelate=settings.get("fe_chelate", "Fe-DTPA"),
                       nh4_source=settings.get("nh4_source", "NH4NO3"),
                       p_source=settings.get("p_source", "KH2PO4"),
                       micro_source=settings.get("micro_source", "individual"))

        lines = [f"{t('c.recipe')} {recipe.name}  |  {t('c.volume_l')} {volume_l:.0f}", ""]
        lines.append(f"{t('costs.salt_label'):<30} {t('costs.g_total'):>8} {'€/kg':>7} {t('costs.cost_label'):>8}")
        lines.append("─" * 56)

        total = 0.0
        for sr in result.all_salts:
            cost = sr.cost_total
            total += cost
            price_str = f"{sr.salt.cost_per_kg:.2f}" if sr.salt.cost_per_kg > 0 else "  –  "
            cost_str = f"{cost:.4f}" if cost > 0 else "  –  "
            lines.append(f"{salt_name(sr.salt.name):<30} {sr.g_total:>8.2f} {price_str:>7} {cost_str:>8}")

        lines.append("─" * 56)
        lines.append(f"{'GESAMT':.<30} {'':>8} {'':>7} {total:>8.4f} €")
        lines.append("")
        lines.append(f"{t('costs.cost_per_l')}  {result.cost_per_liter():.6f} €/L")
        lines.append(f"{warn_fmt('costs.cost_for', 10)}   {result.cost_per_liter() * 10:.4f} €")
        lines.append(f"{warn_fmt('costs.cost_for', 100)}  {result.cost_per_liter() * 100:.4f} €")
        lines.append(f"{warn_fmt('costs.cost_for', 1000)} {result.cost_per_liter() * 1000:.2f} €")

        if total == 0:
            lines.extend(["", t("costs.no_prices_hint")])

        self._set_tb(self.cost_result, "\n".join(lines))

    def _compare_all(self):
        apply_costs_to_salts()
        recipes = load_all_recipes()
        water_profiles = load_all_water_profiles()
        settings = load_settings()
        water = water_profiles.get("Osmosewasser")

        lines = [f"{t('costs.recipe_col'):<28} {'€/L':>8} {'€/10L':>8} {'€/1000L':>9}"]
        lines.append("─" * 56)

        for name, recipe in recipes.items():
            target = recipe.as_mg_dict()
            adjusted, _ = subtract_water(target, water)
            result = solve(adjusted, 1000, 100,
                           fe_chelate=settings.get("fe_chelate", "Fe-DTPA"),
                           nh4_source=settings.get("nh4_source", "NH4NO3"),
                           p_source=settings.get("p_source", "KH2PO4"),
                           micro_source=settings.get("micro_source", "individual"))
            cpl = result.cost_per_liter()
            lines.append(f"{name:<28} {cpl:>8.5f} {cpl*10:>8.4f} {cpl*1000:>9.2f}")

        self._set_tb(self.compare_result, "\n".join(lines))
