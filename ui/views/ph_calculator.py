"""pH-Korrekturrechner View."""
import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.ph_correction import (
    calculate_ph_correction, ACIDS, BASES, PhCorrectionResult,
)
from database.data_manager import load_all_water_profiles
from ui.locales import t


class PhCalculatorView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("ph.title"),
                         subtitle=t("ph.subtitle"))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)

        left = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))

        self._build_input(left)
        self._build_result(right)

    def refresh_data(self): pass

    def _build_input(self, parent):
        # Wasserprofil-Schnellauswahl
        card_water = self._create_card(parent, title=t("ph.card_water"))
        card_water.pack(fill="x", pady=(0, 8))
        profiles = load_all_water_profiles()
        self.water_dropdown = self._create_labeled_dropdown(
            card_water, label=t("c.profile_load"),
            values=["(Manuell)"] + list(profiles.keys()), default="(Manuell)")
        self.water_dropdown.configure(command=self._on_water_selected)
        ctk.CTkFrame(card_water, fg_color="transparent", height=6).pack()

        # Parameter
        card = self._create_card(parent, title=t("ph.card_params"))
        card.pack(fill="x", pady=(0, 8))
        self.entry_hco3 = self._create_labeled_entry(card, label=t("ph.hco3"), placeholder="180")
        self.entry_water_ph = self._create_labeled_entry(card, label=t("ph.water_ph"), placeholder="7.5")
        self.entry_target_ph = self._create_labeled_entry(card, label=t("ph.target_ph"), placeholder="5.8")
        self.entry_volume = self._create_labeled_entry(card, label=t("c.volume_l"), placeholder="1000")
        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

        # Säure/Base-Auswahl
        card_ab = self._create_card(parent, title=t("ph.card_acid_base"))
        card_ab.pack(fill="x", pady=(0, 8))
        acid_names = {k: v.name for k, v in ACIDS.items()}
        base_names = {k: v.name for k, v in BASES.items()}
        self.acid_dropdown = self._create_labeled_dropdown(
            card_ab, label=t("ph.acid"), values=list(acid_names.values()), default=t("b.acid.hno3_65"))
        self.base_dropdown = self._create_labeled_dropdown(
            card_ab, label=t("ph.base"), values=list(base_names.values()), default=t("b.base.koh"))
        ctk.CTkFrame(card_ab, fg_color="transparent", height=6).pack()

        ctk.CTkButton(parent, text=t("ph.btn"), font=ctk.CTkFont(size=14, weight="bold"),
                      height=42, command=self._calculate).pack(fill="x", pady=(5, 8))

    def _build_result(self, parent):
        card = self._create_card(parent, title=t("ph.card_result"))
        card.pack(fill="x", pady=(0, 8))
        self.result_tb = ctk.CTkTextbox(card, height=250, font=ctk.CTkFont(family="Consolas", size=11),
                                        state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.result_tb.pack(fill="x", padx=15, pady=(5, 12))

        card2 = self._create_card(parent, title=t("ph.card_steps"))
        card2.pack(fill="x", pady=(0, 8))
        self.steps_tb = ctk.CTkTextbox(card2, height=200, font=ctk.CTkFont(family="Consolas", size=10),
                                       state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.steps_tb.pack(fill="x", padx=15, pady=(5, 12))

        card3 = self._create_card(parent, title=t("ph.card_notes"))
        card3.pack(fill="x", pady=(0, 8))
        self.warn_tb = ctk.CTkTextbox(card3, height=80, font=ctk.CTkFont(size=11),
                                      state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.warn_tb.pack(fill="x", padx=15, pady=(5, 12))

    def _on_water_selected(self, name):
        if name == "(Manuell)": return
        profiles = load_all_water_profiles()
        p = profiles.get(name)
        if not p: return
        self.entry_hco3.delete(0, "end"); self.entry_hco3.insert(0, str(p.hco3))
        self.entry_water_ph.delete(0, "end"); self.entry_water_ph.insert(0, str(p.ph))

    def _gf(self, entry, default):
        try: return float(entry.get().strip() or entry.cget("placeholder_text"))
        except: return default

    def _set_tb(self, tb, text):
        tb.configure(state="normal"); tb.delete("1.0", "end"); tb.insert("1.0", text); tb.configure(state="disabled")

    def _calculate(self):
        hco3 = self._gf(self.entry_hco3, 180)
        water_ph = self._gf(self.entry_water_ph, 7.5)
        target_ph = self._gf(self.entry_target_ph, 5.8)
        volume = self._gf(self.entry_volume, 1000)

        # Säure/Base Key finden
        acid_name = self.acid_dropdown.get()
        acid_key = next((k for k, v in ACIDS.items() if v.name == acid_name), "HNO3_65")
        base_name = self.base_dropdown.get()
        base_key = next((k for k, v in BASES.items() if v.name == base_name), "KOH")

        res = calculate_ph_correction(hco3, target_ph, water_ph, volume, acid_key, base_key)

        lines = []
        if res.direction == "down":
            lines.append(f"═══ {t('ph.lower')}: {water_ph:.1f} → {target_ph:.1f} ═══")
            lines.append(f"{t('ph.acid')} {res.acid_or_base.name}")
            lines.append(f"HCO₃⁻ zu neutralisieren: {res.h_mmol_needed:.2f} mmol/L")
            lines.append(f"")
            lines.append(f"{t('ph.need_per_l')}  {res.ml_per_liter:.3f} mL/L")
            lines.append(f"{t('ph.need_total')}     {res.ml_per_volume:.1f} mL / {volume:.0f} L")
        else:
            lines.append(f"═══ {t('ph.raise')}: {water_ph:.1f} → {target_ph:.1f} ═══")
            lines.append(f"{t('ph.base')} {res.acid_or_base.name}")
            lines.append(f"{t('ph.oh_demand')} {res.h_mmol_needed:.2f} mmol/L")
            lines.append(f"")
            lines.append(f"{t('ph.need_label')}  {res.g_per_liter:.4f} g/L = {res.g_per_volume:.2f} g {t('ph.total_label')}")

        if res.ion_additions:
            lines.append(f"\n{t('ph.extra_ions')}")
            for sym, mg in res.ion_additions.items():
                lines.append(f"  {sym}: +{mg:.1f} mg/L")
            lines.append(f"\n{t('ph.ion_note')}")

        self._set_tb(self.result_tb, "\n".join(lines))
        self._set_tb(self.steps_tb, "\n".join(f"→ {s}" for s in res.steps))
        self._set_tb(self.warn_tb, "\n".join(res.warnings) if res.warnings else t("c.no_warnings"))
