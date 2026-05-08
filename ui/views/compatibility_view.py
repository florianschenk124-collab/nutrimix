"""Mischbarkeitsmatrix View: Welche Salze dürfen zusammen in einen Tank?"""
import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.compatibility import (
    check_pair, get_key_salts, SEVERITY_ICONS, build_matrix,
)
from chemistry.salts import DEFAULT_SALTS
from ui.locales import t, salt_name


class CompatibilityView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("compat.title"),
                         subtitle=t("compat.subtitle"))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        # Toolbar
        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.view_mode = ctk.CTkSegmentedButton(
            toolbar, values=[t("compat.tab_matrix"), t("compat.tab_single")],
            command=self._switch_mode)
        self.view_mode.set("Matrix")
        self.view_mode.pack(side="left")

        # Content area
        self.main_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nswe")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self._build_matrix_view()
        self._build_pair_view()
        self._show_matrix()

    def refresh_data(self):
        pass

    def _switch_mode(self, mode):
        if mode == t("compat.tab_matrix"):
            self._show_matrix()
        else:
            self._show_pair()

    # ─── Matrix View ──────────────────────────────────────────────────

    def _build_matrix_view(self):
        self.matrix_frame = ctk.CTkScrollableFrame(
            self.main_frame, fg_color="transparent")
        self.matrix_frame.grid(row=0, column=0, sticky="nswe")

        salts = get_key_salts()
        matrix = build_matrix(salts)

        # Legende
        legend = ctk.CTkFrame(self.matrix_frame, fg_color=("gray92", "gray17"),
                               corner_radius=8)
        legend.pack(fill="x", pady=(0, 10), padx=5)
        ctk.CTkLabel(legend, text=t("compat.legend"),
                     font=ctk.CTkFont(size=11)).pack(padx=10, pady=6)

        # Header
        n = len(salts)
        grid = ctk.CTkFrame(self.matrix_frame, fg_color="transparent")
        grid.pack(fill="x", padx=5)

        # Spaltenbreite
        col_w = 40
        name_w = 180

        # Header-Row mit Nummern
        hdr = ctk.CTkFrame(grid, fg_color="transparent")
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="", width=name_w).pack(side="left")
        for j in range(n):
            ctk.CTkLabel(hdr, text=str(j+1), width=col_w,
                         font=ctk.CTkFont(size=10, weight="bold")).pack(side="left")

        # Matrix-Reihen
        for i, salt in enumerate(salts):
            row_frame = ctk.CTkFrame(grid, fg_color="transparent")
            row_frame.pack(fill="x")

            short = f"{i+1}. {salt_name(salt.name)[:22]}"
            ctk.CTkLabel(row_frame, text=short, width=name_w,
                         font=ctk.CTkFont(size=10), anchor="w"
                         ).pack(side="left")

            for j in range(n):
                check = matrix[i][j]
                icon = SEVERITY_ICONS.get(check.severity, "?")
                if i == j:
                    icon = "─"

                lbl = ctk.CTkLabel(row_frame, text=icon, width=col_w,
                                   font=ctk.CTkFont(size=12))
                lbl.pack(side="left")

                # Tooltip-ähnlich: Klick zeigt Details
                if i != j:
                    lbl.bind("<Button-1>",
                             lambda e, c=check: self._show_detail(c))

        # Detail-Bereich
        detail_card = ctk.CTkFrame(self.matrix_frame, fg_color=("gray92", "gray17"),
                                    corner_radius=8)
        detail_card.pack(fill="x", pady=(10, 5), padx=5)
        ctk.CTkLabel(detail_card, text=t("compat.click_detail"),
                     font=ctk.CTkFont(size=11), text_color="gray50"
                     ).pack(padx=10, pady=3, anchor="w")
        self.detail_label = ctk.CTkLabel(
            detail_card, text="", font=ctk.CTkFont(size=11),
            wraplength=600, justify="left")
        self.detail_label.pack(padx=10, pady=(0, 8), anchor="w")

    def _show_detail(self, check):
        icon = SEVERITY_ICONS.get(check.severity, "?")
        text = (f"{icon}  {salt_name(check.salt_a.name)}  ×  {salt_name(check.salt_b.name)}\n"
                f"{t('compat.status')}: {check.severity.upper()}")
        if check.precipitate:
            text += f"\n{t('compat.precipitate')}: {check.precipitate}"
        text += f"\n{check.reason}"
        self.detail_label.configure(text=text)

    # ─── Einzelprüfung ────────────────────────────────────────────────

    def _build_pair_view(self):
        self.pair_frame = ctk.CTkScrollableFrame(
            self.main_frame, fg_color="transparent")
        self.pair_frame.grid(row=0, column=0, sticky="nswe")

        card = self._create_card(self.pair_frame, title=t("compat.card_check"))
        card.pack(fill="x", pady=(0, 8))

        salt_names = [f"{salt_name(s.name)}" for s in DEFAULT_SALTS.values()]
        self.pair_dd_a = self._create_labeled_dropdown(
            card, label=t("compat.salt_a"), values=salt_names,
            default=salt_names[0] if salt_names else "")
        self.pair_dd_b = self._create_labeled_dropdown(
            card, label=t("compat.salt_b"), values=salt_names,
            default=salt_names[3] if len(salt_names) > 3 else salt_names[0] if salt_names else "")
        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

        ctk.CTkButton(card, text=t("compat.btn_check"), height=35,
                      command=self._check_pair).pack(fill="x", padx=15, pady=(0, 12))

        card2 = self._create_card(self.pair_frame, title=t("compat.card_result"))
        card2.pack(fill="x", pady=(0, 8))
        self.pair_result = ctk.CTkTextbox(
            card2, height=180, font=ctk.CTkFont(size=12),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.pair_result.pack(fill="x", padx=15, pady=(5, 12))

    def _check_pair(self):
        name_a = self.pair_dd_a.get()
        name_b = self.pair_dd_b.get()
        salt_a = next((s for s in DEFAULT_SALTS.values() if salt_name(s.name) == name_a), None)
        salt_b = next((s for s in DEFAULT_SALTS.values() if salt_name(s.name) == name_b), None)
        if not salt_a or not salt_b:
            self._set_pair_result(t("compat.salt_not_found"))
            return

        check = check_pair(salt_a, salt_b)
        icon = SEVERITY_ICONS.get(check.severity, "?")
        lines = [f"{icon}  {salt_name(salt_a.name)}  ×  {salt_name(salt_b.name)}", ""]
        lines.append(f"Tank A: {salt_a.tank}  |  Tank B: {salt_b.tank}")
        lines.append(f"{t('compat.compatible_label')} {t('compat.yes') if check.compatible else t('compat.no')}")
        lines.append(f"{t('compat.status')}: {check.severity.upper()}")
        if check.precipitate:
            lines.append(f"{t('compat.precipitate')}: {check.precipitate}")
        lines.append(f"\n{check.reason}")
        self._set_pair_result("\n".join(lines))

    def _set_pair_result(self, text):
        self.pair_result.configure(state="normal")
        self.pair_result.delete("1.0", "end")
        self.pair_result.insert("1.0", text)
        self.pair_result.configure(state="disabled")

    # ─── Ansicht-Wechsel ──────────────────────────────────────────────

    def _show_matrix(self):
        self.pair_frame.grid_remove()
        self.matrix_frame.grid()

    def _show_pair(self):
        self.matrix_frame.grid_remove()
        self.pair_frame.grid()
