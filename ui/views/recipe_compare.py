"""Rezeptvergleich: Zwei Rezepte nebeneinander vergleichen."""
import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.ions import ION_BY_SYMBOL
from chemistry.ratios import check_ratios
from chemistry.ec_estimator import estimate_ec
from database.data_manager import load_all_recipes
from ui.locales import t, td, td


class RecipeCompareView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("compare.title"),
                         subtitle=t("compare.subtitle"))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        # Auswahl
        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        recipes = load_all_recipes()
        names = list(recipes.keys())

        ctk.CTkLabel(toolbar, text=t("compare.recipe_a"), font=ctk.CTkFont(size=12)).pack(side="left")
        self.dd_a = ctk.CTkOptionMenu(toolbar, values=names, width=220)
        self.dd_a.pack(side="left", padx=(5, 15))
        if names:
            self.dd_a.set(names[0])

        ctk.CTkLabel(toolbar, text=t("compare.recipe_b"), font=ctk.CTkFont(size=12)).pack(side="left")
        self.dd_b = ctk.CTkOptionMenu(toolbar, values=names, width=220)
        self.dd_b.pack(side="left", padx=(5, 15))
        if len(names) > 1:
            self.dd_b.set(names[1])
        elif names:
            self.dd_b.set(names[0])

        ctk.CTkButton(toolbar, text=t("compare.btn"), width=130, height=32,
                      command=self._compare).pack(side="left", padx=(10, 0))

        # Ergebnis
        result_frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        result_frame.grid(row=1, column=0, sticky="nswe")
        result_frame.grid_columnconfigure(0, weight=1)

        card_ions = self._create_card(result_frame, title=t("compare.card_ions"))
        card_ions.pack(fill="x", pady=(0, 8))
        self.ions_tb = ctk.CTkTextbox(
            card_ions, height=280, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.ions_tb.pack(fill="x", padx=15, pady=(5, 12))

        card_ratios = self._create_card(result_frame, title=t("compare.card_ratios"))
        card_ratios.pack(fill="x", pady=(0, 8))
        self.ratios_tb = ctk.CTkTextbox(
            card_ratios, height=160, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.ratios_tb.pack(fill="x", padx=15, pady=(5, 12))

        card_sum = self._create_card(result_frame, title=t("compare.card_summary"))
        card_sum.pack(fill="x", pady=(0, 8))
        self.summary_tb = ctk.CTkTextbox(
            card_sum, height=120, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.summary_tb.pack(fill="x", padx=15, pady=(5, 12))

    def refresh_data(self):
        recipes = load_all_recipes()
        names = list(recipes.keys())
        self.dd_a.configure(values=names)
        self.dd_b.configure(values=names)

    def _set_tb(self, tb, text):
        tb.configure(state="normal"); tb.delete("1.0", "end")
        tb.insert("1.0", text); tb.configure(state="disabled")

    def _compare(self):
        recipes = load_all_recipes()
        ra = recipes.get(self.dd_a.get())
        rb = recipes.get(self.dd_b.get())
        if not ra or not rb:
            self._set_tb(self.ions_tb, t("compare.not_found"))
            return

        mg_a = ra.as_mg_dict()
        mg_b = rb.as_mg_dict()

        # Ionen-Tabelle
        name_a = self.dd_a.get()[:18]
        name_b = self.dd_b.get()[:18]
        lines = [f"{'Ion':<10} {name_a:>18} {name_b:>18} {'Δ':>10} {'Δ%':>8}"]
        lines.append("─" * 68)

        all_ions_macro = ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4"]
        all_ions_micro = ["Fe", "Mn", "Zn", "Cu", "B", "Mo"]

        for sym in all_ions_macro:
            va = mg_a.get(sym, 0)
            vb = mg_b.get(sym, 0)
            delta = vb - va
            pct = (delta / va * 100) if va > 0 else 0
            display = ION_BY_SYMBOL[sym].display if sym in ION_BY_SYMBOL else sym
            bar = self._delta_bar(delta, max(va, vb, 1))
            lines.append(f"{display:<10} {va:>18.1f} {vb:>18.1f} {delta:>+10.1f} {pct:>+7.0f}% {bar}")

        lines.append("─" * 68)
        for sym in all_ions_micro:
            va = mg_a.get(sym, 0)
            vb = mg_b.get(sym, 0)
            delta = vb - va
            pct = (delta / va * 100) if va > 0 else 0
            display = ION_BY_SYMBOL[sym].display if sym in ION_BY_SYMBOL else sym
            lines.append(f"{display:<10} {va:>18.3f} {vb:>18.3f} {delta:>+10.3f} {pct:>+7.0f}%")

        self._set_tb(self.ions_tb, "\n".join(lines))

        # Ratios
        ratios_a = check_ratios(mg_a)
        ratios_b = check_ratios(mg_b)
        rlines = [f"{t('compare.ratio'):<14} {name_a:>14} {name_b:>14} {t('b.target'):>14}"]
        rlines.append("─" * 58)
        for ra_r, rb_r in zip(ratios_a, ratios_b):
            rlines.append(
                f"{ra_r.status_icon}/{rb_r.status_icon} {ra_r.name:<11} "
                f"{ra_r.actual:>12.2f}:1 {rb_r.actual:>12.2f}:1 {ra_r.target_str:>14}")
        self._set_tb(self.ratios_tb, "\n".join(rlines))

        # Zusammenfassung
        ec_a = estimate_ec(mg_a)
        ec_b = estimate_ec(mg_b)
        slines = [f"{'':20} {name_a:>18} {name_b:>18}"]
        slines.append("─" * 58)
        slines.append(f"{t('compare.ec_est'):<20} {ec_a:>17.2f} {ec_b:>17.2f} mS/cm")
        slines.append(f"{t('compare.ec_target'):<20} {ra.ec_target:>17.1f} {rb.ec_target:>17.1f} mS/cm")
        slines.append(f"{t('compare.ph_range_label'):<20} {ra.ph_min:>7.1f}–{ra.ph_max:<8.1f} {rb.ph_min:>7.1f}–{rb.ph_max:<8.1f}")
        slines.append(f"{t('compare.plants'):<20} {', '.join(ra.suitable_plants[:2]):>18} {', '.join(rb.suitable_plants[:2]):>18}")
        self._set_tb(self.summary_tb, "\n".join(slines))

    def _delta_bar(self, delta, ref):
        """Mini-Balkendiagramm für Δ."""
        if ref == 0: return ""
        ratio = delta / ref
        if ratio > 0.1: return "▲"
        if ratio < -0.1: return "▼"
        return "≈"
