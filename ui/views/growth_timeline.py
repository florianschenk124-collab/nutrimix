"""Wachstumsphasen-Timeline: Wochenbasierter Nährstoffplan."""
import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.growth_phases import (
    DEFAULT_GROWTH_PLANS, GrowthPlan, generate_weekly_schedule,
    apply_phase_to_recipe, interpolate_week,
)
from chemistry.ions import ION_BY_SYMBOL
from database.data_manager import load_all_recipes
from ui.locales import t, td, td


class GrowthTimelineView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("growth.title"),
                         subtitle=t("growth.subtitle"))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))

        # 1. Zuerst alle UI-Elemente definieren
        self._build_plan_selector(left)
        self._build_phase_info_ui(left)    # Nur UI erstellen, noch keine Daten laden
        self._build_timeline(right)
        self._build_week_detail(right)

        # 2. Erst jetzt die Daten initial laden, da alle Attribute (wie week_slider) existieren
        self._on_plan_changed(self.plan_dd.get())

    def refresh_data(self):
        pass

    # ─── Linke Seite ──────────────────────────────────────────────────

    def _build_plan_selector(self, parent):
        card = self._create_card(parent, title=t("growth.card_select"))
        card.pack(fill="x", pady=(0, 8))

        plan_names = list(DEFAULT_GROWTH_PLANS.keys())
        self.plan_dd = self._create_labeled_dropdown(
            card, label=t("growth.plan"), values=plan_names,
            default=plan_names[0] if plan_names else "")
        self.plan_dd.configure(command=self._on_plan_changed)
        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

        self.plan_info = ctk.CTkLabel(
            card, text="", font=ctk.CTkFont(size=11), text_color="gray50",
            wraplength=350, justify="left")
        self.plan_info.pack(padx=15, pady=(0, 12), anchor="w")

    def _build_phase_info_ui(self, parent):
        card = self._create_card(parent, title=t("growth.card_phases"))
        card.pack(fill="x", pady=(0, 8))
        self.phase_tb = ctk.CTkTextbox(
            card, height=260, font=ctk.CTkFont(family="Consolas", size=10),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.phase_tb.pack(fill="x", padx=15, pady=(5, 12))

    # ─── Rechte Seite ─────────────────────────────────────────────────

    def _build_timeline(self, parent):
        card = self._create_card(parent, title=t("growth.card_timeline"))
        card.pack(fill="x", pady=(0, 8))

        self.timeline_tb = ctk.CTkTextbox(
            card, height=280, font=ctk.CTkFont(family="Consolas", size=10),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.timeline_tb.pack(fill="x", padx=15, pady=(5, 12))

    def _build_week_detail(self, parent):
        card = self._create_card(parent, title=t("growth.card_week"))
        card.pack(fill="x", pady=(0, 8))

        week_frame = ctk.CTkFrame(card, fg_color="transparent")
        week_frame.pack(fill="x", padx=15, pady=(5, 5))

        ctk.CTkLabel(week_frame, text=t("growth.week"), font=ctk.CTkFont(size=12)).pack(side="left")
        self.week_slider = ctk.CTkSlider(week_frame, from_=0, to=24, number_of_steps=24,
                                        width=200, command=self._on_week_changed)
        self.week_slider.set(0)
        self.week_slider.pack(side="left", padx=(10, 10))
        self.week_label = ctk.CTkLabel(week_frame, text="W0",
                                      font=ctk.CTkFont(size=12, weight="bold"))
        self.week_label.pack(side="left")

        self.week_detail_tb = ctk.CTkTextbox(
            card, height=200, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.week_detail_tb.pack(fill="x", padx=15, pady=(5, 12))

    # ─── Callbacks ────────────────────────────────────────────────────

    def _set_tb(self, tb, text):
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.insert("1.0", text)
        tb.configure(state="disabled")

    def _on_plan_changed(self, name):
        plan = DEFAULT_GROWTH_PLANS.get(name)
        if not plan:
            return

        # Plan-Info
        self.plan_info.configure(
            text=f"{t('growth.culture_label')}: {td(plan.crop)} | {plan.total_weeks} {t('growth.weeks')} | "
                 f"{len(plan.phases)} {t('growth.phases')}\n{t('growth.base_label')}: {td(plan.base_recipe_name)}\n"
                 f"{t('growth.source_label')}: {td(plan.source)}\n{td(plan.description)}")

        # Slider anpassen
        self.week_slider.configure(to=plan.total_weeks,
                                    number_of_steps=plan.total_weeks)

        # Phasenübersicht
        lines = []
        for p in plan.phases:
            lines.append(f"{'═' * 44}")
            lines.append(f"  {td(p.name)}  (W{p.week_start}–W{p.week_end})")
            lines.append(f"  {t('growth.ec_target')}: {p.ec_target:.1f} mS/cm  |  NH₄: {p.nh4_ratio:.0%}")
            mods = []
            if p.n_factor != 1.0: mods.append(f"N ×{p.n_factor:.2f}")
            if p.k_factor != 1.0: mods.append(f"K ×{p.k_factor:.2f}")
            if p.ca_factor != 1.0: mods.append(f"Ca ×{p.ca_factor:.2f}")
            if p.mg_factor != 1.0: mods.append(f"Mg ×{p.mg_factor:.2f}")
            if p.p_factor != 1.0: mods.append(f"P ×{p.p_factor:.2f}")
            if mods:
                lines.append(f"  {t('growth.modifiers')}: {', '.join(mods)}")
            if p.notes:
                lines.append(f"  💡 {td(p.notes)}")
        self._set_tb(self.phase_tb, "\n".join(lines))

        # Timeline
        recipes = load_all_recipes()
        base_recipe = recipes.get(plan.base_recipe_name)
        if not base_recipe:
            base_recipe = next(iter(recipes.values())) if recipes else None
        if not base_recipe:
            self._set_tb(self.timeline_tb, t("growth.no_recipe"))
            return

        schedule = generate_weekly_schedule(plan, base_recipe.as_mg_dict())

        tlines = [f"{'W':>3} {t('growth.phase_label'):<20} {'EC':>5} {'N×':>5} {'K×':>5} {'N:K':>6}"]
        tlines.append("─" * 48)
        for entry in schedule:
            w = entry["week"]
            phase = entry["phase_name"][:19]
            ec = entry["ec_target"]
            nf = entry["factors"]["n_factor"]
            kf = entry["factors"]["k_factor"]
            adj = entry["adjusted_mg"]
            n_total = adj.get("NO3", 0) + adj.get("NH4", 0)
            k = adj.get("K", 0)
            nk = f"{n_total/k:.2f}" if k > 0 else "–"
            tlines.append(f"{w:>3} {phase:<20} {ec:>5.1f} {nf:>5.2f} {kf:>5.2f} {nk:>6}")
        self._set_tb(self.timeline_tb, "\n".join(tlines))

        # Initial week detail
        self._on_week_changed(0)

    def _on_week_changed(self, value):
        week = int(float(value))
        self.week_label.configure(text=f"W{week}")

        plan = DEFAULT_GROWTH_PLANS.get(self.plan_dd.get())
        if not plan:
            return

        recipes = load_all_recipes()
        base_recipe = recipes.get(plan.base_recipe_name)
        if not base_recipe:
            base_recipe = next(iter(recipes.values())) if recipes else None
        if not base_recipe:
            return

        factors = interpolate_week(plan, week)
        adjusted = apply_phase_to_recipe(base_recipe.as_mg_dict(), factors)

        phase_name = t("growth.transition")
        for p in plan.phases:
            if p.week_start <= week <= p.week_end:
                phase_name = td(p.name)
                break

        lines = [f"═══ {t('growth.week_header')} {week}: {phase_name} ═══", ""]
        lines.append(f"{t('growth.ec_target')}: {factors.get('ec_target', 0):.1f} mS/cm  |  NH₄-Ratio: {factors.get('nh4_ratio', 0.05):.0%}")
        lines.append(f"{t('growth.modifiers')}: N×{factors['n_factor']:.2f}  K×{factors['k_factor']:.2f}  "
                     f"Ca×{factors['ca_factor']:.2f}  Mg×{factors['mg_factor']:.2f}  P×{factors['p_factor']:.2f}")
        lines.append("")

        base_mg = base_recipe.as_mg_dict()
        lines.append(f"{'Ion':<10} {t('growth.base_label'):>8} {t('growth.week_header'):>8} {'Δ':>8} mg/L")
        lines.append("─" * 36)
        for sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4"]:
            b = base_mg.get(sym, 0)
            a = adjusted.get(sym, 0)
            delta = a - b
            display = ION_BY_SYMBOL[sym].display if sym in ION_BY_SYMBOL else sym
            lines.append(f"{display:<10} {b:>8.1f} {a:>8.1f} {delta:>+8.1f}")

        self._set_tb(self.week_detail_tb, "\n".join(lines))