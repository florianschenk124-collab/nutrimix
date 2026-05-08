"""Verdünnungsrechner View."""
import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.dilution import calculate_dilution, ec_dilution_table
from chemistry.solver import solve
from chemistry.water import subtract_water
from chemistry.ions import ION_BY_SYMBOL
from database.data_manager import load_all_recipes, load_all_water_profiles, load_settings
from ui.locales import t, td, td


class DilutionCalculatorView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("dil.title"),
                         subtitle=t("dil.subtitle"))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)

        left = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))

        self._build_input(left)
        self._build_result(right)

    def refresh_data(self):
        r = load_all_recipes(); self.recipe_dd.configure(values=list(r.keys()))
        w = load_all_water_profiles(); self.water_dd.configure(values=list(w.keys()))

    def _build_input(self, parent):
        card = self._create_card(parent, title=t("dil.card_stock"))
        card.pack(fill="x", pady=(0, 8))
        recipes = load_all_recipes(); water = load_all_water_profiles()
        self.recipe_dd = self._create_labeled_dropdown(card, label=t("c.recipe"),
            values=list(recipes.keys()), default=list(recipes.keys())[0] if recipes else "")
        self.water_dd = self._create_labeled_dropdown(card, label=t("c.water"),
            values=list(water.keys()), default="Osmosewasser")
        self.entry_factor = self._create_labeled_entry(card, label=t("c.conc_factor"), placeholder="100")
        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

        card2 = self._create_card(parent, title=t("dil.card_dilution"))
        card2.pack(fill="x", pady=(0, 8))
        self.entry_target_ec = self._create_labeled_entry(card2, label=t("dil.target_ec"), placeholder="1.5")
        self.entry_volume = self._create_labeled_entry(card2, label=t("c.volume_l"), placeholder="100")
        self.entry_water_ec = self._create_labeled_entry(card2, label=t("dil.water_ec"), placeholder="0.0")
        self.entry_ratio = self._create_labeled_entry(card2, label=t("c.dose_ratio"), placeholder="1:1")
        ctk.CTkFrame(card2, fg_color="transparent", height=6).pack()

        ctk.CTkButton(parent, text=t("dil.btn"), font=ctk.CTkFont(size=14, weight="bold"),
                      height=42, command=self._calculate).pack(fill="x", pady=(5, 5))
        ctk.CTkButton(parent, text=t("dil.btn_table"), font=ctk.CTkFont(size=12),
                      height=35, fg_color="transparent", border_width=1, border_color="gray40",
                      command=self._show_table).pack(fill="x", pady=(0, 8))

    def _build_result(self, parent):
        card = self._create_card(parent, title=t("dil.card_dosing"))
        card.pack(fill="x", pady=(0, 8))
        self.result_tb = ctk.CTkTextbox(card, height=200, font=ctk.CTkFont(family="Consolas", size=11),
                                        state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.result_tb.pack(fill="x", padx=15, pady=(5, 12))

        card2 = self._create_card(parent, title=t("dil.card_ions"))
        card2.pack(fill="x", pady=(0, 8))
        self.ions_tb = ctk.CTkTextbox(card2, height=180, font=ctk.CTkFont(family="Consolas", size=11),
                                      state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.ions_tb.pack(fill="x", padx=15, pady=(5, 12))

        card3 = self._create_card(parent, title=t("dil.card_table"))
        card3.pack(fill="x", pady=(0, 8))
        self.table_tb = ctk.CTkTextbox(card3, height=200, font=ctk.CTkFont(family="Consolas", size=11),
                                       state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.table_tb.pack(fill="x", padx=15, pady=(5, 12))

    def _gf(self, entry, default):
        try: return float(entry.get().strip() or entry.cget("placeholder_text"))
        except: return default

    def _set_tb(self, tb, text):
        tb.configure(state="normal"); tb.delete("1.0", "end"); tb.insert("1.0", text); tb.configure(state="disabled")

    def _get_solver_result(self):
        recipes = load_all_recipes(); water = load_all_water_profiles(); settings = load_settings()
        recipe = recipes.get(self.recipe_dd.get()); w = water.get(self.water_dd.get())
        if not recipe or not w: return None, 0, 0
        factor = self._gf(self.entry_factor, 100)
        adj, _ = subtract_water(recipe.as_mg_dict(), w)
        ratio = self.entry_ratio.get().strip() or "1:1"
        res = solve(adj, 1000, factor, fe_chelate=settings.get("fe_chelate", "Fe-DTPA"),
                    nh4_source=settings.get("nh4_source", "NH4NO3"),
                    p_source=settings.get("p_source", "KH2PO4"),
                    micro_source=settings.get("micro_source", "individual"),
                    dose_ratio=ratio)
        parts = ratio.split(":"); ra = float(parts[0]); rb = float(parts[1])
        return res, ra, rb

    def _calculate(self):
        res, ra, rb = self._get_solver_result()
        if not res:
            self._set_tb(self.result_tb, t("dil.not_found")); return
        target_ec = self._gf(self.entry_target_ec, 1.5)
        volume = self._gf(self.entry_volume, 100)
        water_ec = self._gf(self.entry_water_ec, 0)
        factor = self._gf(self.entry_factor, 100)

        dil = calculate_dilution(res, target_ec, volume, factor, ra, rb, water_ec)

        lines = [f"═══ {t('dil.dilution_to')} {target_ec:.1f} mS/cm ═══", ""]
        lines.append(f"{t('dil.base_ec')}    {dil.base_ec:.2f} mS/cm")
        lines.append(f"{t('dil.dil_factor')}  {dil.dilution_factor:.1%}")
        lines.append(f"")
        lines.append(f"{t('dil.dosing_per_l'):<25}")
        lines.append(f"  Tank A:  {dil.ml_a_per_liter:.2f} mL/L")
        lines.append(f"  Tank B:  {dil.ml_b_per_liter:.2f} mL/L")
        lines.append(f"  {t('b.total')}:  {dil.ml_a_per_liter + dil.ml_b_per_liter:.2f} mL/L")
        lines.append(f"")
        lines.append(f"{t('dil.for_volume')} {volume:.0f} L:")
        lines.append(f"  Tank A:  {dil.ml_a_total:.1f} mL")
        lines.append(f"  Tank B:  {dil.ml_b_total:.1f} mL")
        lines.append(f"\nEC erreicht: {dil.achieved_ec:.2f} mS/cm")
        if dil.warnings:
            lines.append(f"\n⚠️  {' | '.join(dil.warnings)}")
        self._set_tb(self.result_tb, "\n".join(lines))

        # Ionen
        ion_lines = [f"{'Ion':<10} {'100%':>8} {t('dil.diluted'):>10} mg/L"]
        ion_lines.append("─" * 30)
        for sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4"]:
            full = res.achieved_mg.get(sym, 0)
            diluted = dil.diluted_mg.get(sym, 0)
            if full > 0:
                display = ION_BY_SYMBOL[sym].display if sym in ION_BY_SYMBOL else sym
                ion_lines.append(f"{display:<10} {full:>8.1f} {diluted:>10.1f}")
        self._set_tb(self.ions_tb, "\n".join(ion_lines))

    def _show_table(self):
        res, ra, rb = self._get_solver_result()
        if not res:
            self._set_tb(self.table_tb, t("dil.select_first")); return
        factor = self._gf(self.entry_factor, 100)
        table = ec_dilution_table(res, factor, ra, rb)
        lines = [f"{'EC':>5} {t('b.dil_factor_short'):>8} {'mL A/L':>8} {'mL B/L':>8} {t('b.total')+'/L':>8}"]
        lines.append("─" * 42)
        for row in table:
            lines.append(f"{row['ec']:>5.1f} {row['factor']:>7.1%} {row['ml_a']:>8.2f} {row['ml_b']:>8.2f} {row['ml_total']:>8.2f}")
        self._set_tb(self.table_tb, "\n".join(lines))
