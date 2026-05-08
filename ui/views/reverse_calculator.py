"""Rückwärtsrechner View: Salzeinwaagen → Ionenkonzentrationen."""
import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.salts import DEFAULT_SALTS, Salt
from chemistry.reverse_solver import reverse_calculate, find_matching_recipe, SaltInput
from chemistry.ions import ION_BY_SYMBOL
from ui.locales import t, salt_name


class ReverseCalculatorView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("rev.title"),
                         subtitle=t("rev.subtitle"))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)

        left = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))

        self._build_input(left)
        self._build_result(right)

    def refresh_data(self):
        pass

    def _build_input(self, parent):
        card_vol = self._create_card(parent, title=t("rev.card_volume"))
        card_vol.pack(fill="x", pady=(0, 8))
        self.entry_volume = self._create_labeled_entry(
            card_vol, label=t("rev.end_volume"), placeholder="10")
        ctk.CTkFrame(card_vol, fg_color="transparent", height=6).pack()

        # Salz hinzufügen
        card_add = self._create_card(parent, title=t("rev.card_add"))
        card_add.pack(fill="x", pady=(0, 8))

        salt_names = [f"{salt_name(s.name)} ({s.formula})" for s in DEFAULT_SALTS.values()]
        self.salt_dropdown = self._create_labeled_dropdown(
            card_add, label=t("rev.salt"), values=salt_names,
            default=salt_names[0] if salt_names else "")
        self.entry_grams = self._create_labeled_entry(
            card_add, label=t("rev.grams"), placeholder="10.0")

        ctk.CTkButton(card_add, text=t("rev.btn_add"), height=32,
                      command=self._add_salt).pack(fill="x", padx=15, pady=(5, 12))

        # Liste der eingewogenen Salze
        card_list = self._create_card(parent, title=t("rev.card_list"))
        card_list.pack(fill="x", pady=(0, 8))

        self.salt_list_frame = ctk.CTkScrollableFrame(
            card_list, height=200, fg_color="transparent")
        self.salt_list_frame.pack(fill="x", padx=15, pady=(5, 5))
        self.salt_list_frame.grid_columnconfigure(0, weight=1)

        btn_frame = ctk.CTkFrame(card_list, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 12))
        ctk.CTkButton(btn_frame, text=t("rev.btn_clear"), height=30, width=130,
                      fg_color="transparent", border_width=1, border_color="#c0392b",
                      text_color="#e74c3c", command=self._clear_all
                      ).pack(side="left")

        self.salt_entries: list[tuple[Salt, float]] = []

        ctk.CTkButton(parent, text=t("rev.btn"),
                      font=ctk.CTkFont(size=14, weight="bold"), height=42,
                      command=self._calculate).pack(fill="x", pady=(5, 8))

    def _build_result(self, parent):
        card = self._create_card(parent, title=t("rev.card_ions"))
        card.pack(fill="x", pady=(0, 8))
        self.result_tb = ctk.CTkTextbox(
            card, height=250, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.result_tb.pack(fill="x", padx=15, pady=(5, 12))

        card2 = self._create_card(parent, title=t("rev.card_ratios"))
        card2.pack(fill="x", pady=(0, 8))
        self.ratios_tb = ctk.CTkTextbox(
            card2, height=150, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.ratios_tb.pack(fill="x", padx=15, pady=(5, 12))

        card3 = self._create_card(parent, title=t("rev.card_match"))
        card3.pack(fill="x", pady=(0, 8))
        self.match_tb = ctk.CTkTextbox(
            card3, height=100, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.match_tb.pack(fill="x", padx=15, pady=(5, 12))

        card4 = self._create_card(parent, title=t("rev.card_steps"))
        card4.pack(fill="x", pady=(0, 8))
        self.steps_tb = ctk.CTkTextbox(
            card4, height=150, font=ctk.CTkFont(family="Consolas", size=10),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.steps_tb.pack(fill="x", padx=15, pady=(5, 12))

    def _set_tb(self, tb, text):
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.insert("1.0", text)
        tb.configure(state="disabled")

    def _add_salt(self):
        name_formula = self.salt_dropdown.get()
        grams_str = self.entry_grams.get().strip()
        if not grams_str:
            return
        try:
            grams = float(grams_str.replace(",", "."))
        except ValueError:
            return
        if grams <= 0:
            return

        # Salz finden
        salt = None
        for s in DEFAULT_SALTS.values():
            if f"{salt_name(s.name)} ({s.formula})" == name_formula:
                salt = s
                break
        if not salt:
            return

        self.salt_entries.append((salt, grams))
        self.entry_grams.delete(0, "end")
        self._refresh_list()

    def _clear_all(self):
        self.salt_entries.clear()
        self._refresh_list()

    def _remove_salt(self, index):
        if 0 <= index < len(self.salt_entries):
            self.salt_entries.pop(index)
            self._refresh_list()

    def _refresh_list(self):
        for w in self.salt_list_frame.winfo_children():
            w.destroy()

        for i, (salt, grams) in enumerate(self.salt_entries):
            row = ctk.CTkFrame(self.salt_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row, text=f"{salt_name(salt.name)}: {grams:.2f} g",
                         font=ctk.CTkFont(size=11), anchor="w"
                         ).grid(row=0, column=0, sticky="w")

            ctk.CTkButton(row, text="✕", width=25, height=22,
                          fg_color="transparent", text_color="#e74c3c",
                          font=ctk.CTkFont(size=11),
                          command=lambda idx=i: self._remove_salt(idx)
                          ).grid(row=0, column=1)

    def _calculate(self):
        if not self.salt_entries:
            self._set_tb(self.result_tb, t("rev.no_salts"))
            return

        vol_str = self.entry_volume.get().strip()
        if not vol_str:
            vol_str = self.entry_volume.cget("placeholder_text")
        try:
            volume = float(vol_str)
        except ValueError:
            volume = 10.0

        salt_inputs = [SaltInput(salt=s, grams=g) for s, g in self.salt_entries]
        result = reverse_calculate(salt_inputs, volume)

        # Ionen-Tabelle
        lines = [f"{'Ion':<12} {'mg/L':>8} {'mmol/L':>8}"]
        lines.append("─" * 30)
        for sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4"]:
            mg = result.ion_mg.get(sym, 0)
            mmol = result.ion_mmol.get(sym, 0)
            if mg > 0.01:
                display = ION_BY_SYMBOL[sym].display if sym in ION_BY_SYMBOL else sym
                lines.append(f"{display:<12} {mg:>8.1f} {mmol:>8.3f}")
        lines.append("─" * 30)
        for sym in ["Fe", "Mn", "Zn", "Cu", "B", "Mo"]:
            mg = result.ion_mg.get(sym, 0)
            mmol = result.ion_mmol.get(sym, 0)
            if mg > 0.001:
                display = ION_BY_SYMBOL[sym].display if sym in ION_BY_SYMBOL else sym
                lines.append(f"{display:<12} {mg:>8.3f} {mmol:>8.4f}")
        lines.append(f"\n{t('c.ec_estimated')}: {result.ec_estimated:.2f} mS/cm")
        if result.warnings:
            for w in result.warnings:
                lines.append(w)
        self._set_tb(self.result_tb, "\n".join(lines))

        # Ratios
        ratio_lines = []
        for r in result.ratios:
            ratio_lines.append(
                f"{r.status_icon} {r.name:<12} "
                f"{t('b.actual')}: {r.actual:>5.2f}:1  {t('b.target')}: {r.target_str}")
        self._set_tb(self.ratios_tb, "\n".join(ratio_lines))

        # Rezept-Matching
        matches = find_matching_recipe(result)
        match_lines = []
        for name, sim in matches[:5]:
            bar = "█" * int(sim / 5) + "░" * (20 - int(sim / 5))
            match_lines.append(f"{bar} {sim:>5.1f}%  {name}")
        self._set_tb(self.match_tb, "\n".join(match_lines))

        # Schritte
        self._set_tb(self.steps_tb, "\n".join(f"→ {s}" for s in result.steps))
