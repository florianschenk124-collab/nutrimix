"""Salz-Datenbank: Übersicht aller Düngesalze + eigene Salze hinzufügen."""

import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.salts import DEFAULT_SALTS, Salt
from chemistry.ions import ION_BY_SYMBOL
from ui.locales import t, salt_name, salt_note, warn_fmt
from database.data_manager import save_custom_salt, delete_custom_salt, load_custom_salts

AVAILABLE_IONS = [
    "Ca", "Mg", "K", "NO3", "NH4", "H2PO4", "SO4",
    "Fe", "Mn", "Zn", "Cu", "B", "Mo", "Cl", "Na",
]


class SaltDatabaseView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("salts.title"), subtitle=t("salts.subtitle"))
        self.content.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        ctk.CTkEntry(toolbar, placeholder_text=t("c.search_salt"), width=300,
                     textvariable=self.search_var).pack(side="left")

        self.filter_tank = ctk.CTkOptionMenu(
            toolbar, values=[t("salts.filter_all"), "Tank A", "Tank B",
                             t("salts.filter_macro"), t("salts.filter_chelate"),
                             t("salts.filter_micro"), t("salts.filter_premix"),
                             t("salts.filter_custom")],
            width=130, command=self._on_search)
        self.filter_tank.pack(side="left", padx=(10, 0))

        ctk.CTkButton(toolbar, text=t("salts.btn_add"), width=140, height=28,
                      font=ctk.CTkFont(size=12),
                      command=self._open_add_dialog).pack(side="right", padx=(10, 0))

        ctk.CTkLabel(toolbar, text=warn_fmt("salts.count", len(DEFAULT_SALTS)),
                     font=ctk.CTkFont(size=11), text_color="gray50").pack(side="right")

        self.table_frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nswe")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self._populate_table()

    def _on_search(self, *args):
        self._populate_table()

    def _populate_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        search = self.search_var.get().lower()
        tank_filter = self.filter_tank.get()
        custom_formulas = {s.formula for s in load_custom_salts()}

        header = ctk.CTkFrame(self.table_frame, fg_color=("gray80", "gray25"), corner_radius=6)
        header.pack(fill="x", pady=(0, 6))
        for name, w in [(t("salts.col_name"), 190), (t("salts.col_formula"), 140),
                        (t("salts.col_molar"), 80), (t("salts.col_tank"), 50),
                        (t("salts.col_sol"), 80)]:
            ctk.CTkLabel(header, text=name, width=w,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         anchor="w").pack(side="left", padx=(8, 4), pady=8)

        for formula, salt in DEFAULT_SALTS.items():
            is_custom = formula in custom_formulas
            filt = tank_filter
            if filt == "Tank A" and "A" not in salt.tank: continue
            if filt == "Tank B" and "B" not in salt.tank: continue
            if filt == t("salts.filter_macro") and salt.category != "macro": continue
            if filt == t("salts.filter_chelate") and salt.category != "chelate": continue
            if filt == t("salts.filter_micro") and salt.category != "micro": continue
            if filt == t("salts.filter_premix") and salt.category != "premix": continue
            if filt == t("salts.filter_custom") and not is_custom: continue
            if search and search not in salt.name.lower() and \
               search not in salt_name(salt.name).lower() and \
               search not in salt.formula.lower(): continue

            row = ctk.CTkFrame(self.table_frame, corner_radius=6,
                               fg_color=("gray92", "gray17"), height=36)
            row.pack(fill="x", pady=1)

            dn = ("⭐ " if is_custom else "") + salt_name(salt.name)
            for val, w in [(dn, 190), (salt.formula, 140), (f"{salt.molar_mass:.2f}", 80),
                           (salt.tank, 50), (f"{salt.solubility_20:.0f}", 80)]:
                ctk.CTkLabel(row, text=val, width=w, font=ctk.CTkFont(size=11),
                             anchor="w").pack(side="left", padx=(8, 4), pady=6)

            bf = ctk.CTkFrame(row, fg_color="transparent")
            bf.pack(side="right", padx=8)
            ctk.CTkButton(bf, text=t("c.details"), width=65, height=24,
                          font=ctk.CTkFont(size=10), fg_color="transparent",
                          border_width=1, border_color="gray40",
                          command=lambda s=salt: self._show_detail(s)).pack(side="left", padx=2)
            if is_custom:
                ctk.CTkButton(bf, text="✏️", width=30, height=24, font=ctk.CTkFont(size=10),
                              fg_color="transparent", border_width=1, border_color="gray40",
                              command=lambda s=salt: self._open_salt_editor(s)).pack(side="left", padx=2)
                ctk.CTkButton(bf, text="🗑", width=30, height=24, font=ctk.CTkFont(size=10),
                              fg_color="transparent", border_width=1, border_color="#e74c3c",
                              command=lambda s=salt: self._delete_salt(s)).pack(side="left", padx=2)

    def _show_detail(self, salt: Salt):
        win = ctk.CTkToplevel(self)
        win.title(salt_name(salt.name))
        win.geometry("400x420")
        win.grab_set()

        tb = ctk.CTkTextbox(win, font=ctk.CTkFont(family="Consolas", size=12))
        tb.pack(fill="both", expand=True, padx=15, pady=15)

        lines = [
            f"═══ {salt_name(salt.name)} ═══",
            f"{t('salts.det_formula')}      {salt.formula}",
            f"{t('salts.det_molar')}    {salt.molar_mass:.2f} g/mol",
            f"{t('salts.det_sol')} {salt.solubility_20:.0f} g/L (20°C)",
            f"Tank:        {salt.tank}",
        ]
        if salt.is_chelate:
            lines.append(f"Fe:          {salt.fe_content_pct:.1f}%")
        if salt.notes:
            lines.append(f"{t('salts.note_label')}     {salt_note(salt.notes)}")
        lines.extend(["", t("salts.ion_contrib")])
        mg_per_g = salt.mg_ion_per_gram()
        for ion_sym, stoich in salt.ion_contribution.items():
            ion = ION_BY_SYMBOL.get(ion_sym)
            display = ion.display if ion else ion_sym
            mg = mg_per_g.get(ion_sym, 0)
            lines.append(f"  {display:<10} {stoich:.0f}× → {mg:.2f} {t('salts.mg_per_g_salt')}")
        tb.insert("1.0", "\n".join(lines))
        tb.configure(state="disabled")

    def _delete_salt(self, salt: Salt):
        delete_custom_salt(salt.formula)
        if salt.formula in DEFAULT_SALTS:
            del DEFAULT_SALTS[salt.formula]
        self._populate_table()

    def _open_add_dialog(self):
        self._open_salt_editor(None)

    def _open_salt_editor(self, salt):
        is_edit = salt is not None
        win = ctk.CTkToplevel(self)
        win.title(t("salts.edit_title") if is_edit else t("salts.add_title"))
        win.geometry("520x600")
        win.grab_set()

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        # ── Grunddaten ──
        ctk.CTkLabel(scroll, text=t("salts.section_basic"),
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 8))

        fields = {}
        for key, label, default in [
            ("name", t("salts.field_name"), salt.name if salt else ""),
            ("formula", t("salts.field_formula"), salt.formula if salt else ""),
            ("molar_mass", t("salts.field_molar"), str(salt.molar_mass) if salt else ""),
            ("solubility_20", t("salts.field_sol"), str(salt.solubility_20) if salt else "300"),
        ]:
            r = ctk.CTkFrame(scroll, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=label, width=180, anchor="w").pack(side="left")
            e = ctk.CTkEntry(r, width=280)
            e.pack(side="left", padx=(5, 0))
            if default: e.insert(0, default)
            fields[key] = e

        # Tank
        r = ctk.CTkFrame(scroll, fg_color="transparent")
        r.pack(fill="x", pady=2)
        ctk.CTkLabel(r, text="Tank:", width=180, anchor="w").pack(side="left")
        tank_var = ctk.StringVar(value=salt.tank if salt else "B")
        ctk.CTkOptionMenu(r, values=["A", "B", "AB"], variable=tank_var, width=100).pack(side="left", padx=(5, 0))

        # Kategorie
        r = ctk.CTkFrame(scroll, fg_color="transparent")
        r.pack(fill="x", pady=2)
        ctk.CTkLabel(r, text=t("salts.field_category"), width=180, anchor="w").pack(side="left")
        cat_var = ctk.StringVar(value=salt.category if salt else "macro")
        ctk.CTkOptionMenu(r, values=["macro", "micro", "chelate"], variable=cat_var,
                          width=140).pack(side="left", padx=(5, 0))

        # Notizen
        r = ctk.CTkFrame(scroll, fg_color="transparent")
        r.pack(fill="x", pady=2)
        ctk.CTkLabel(r, text=t("salts.field_notes"), width=180, anchor="w").pack(side="left")
        notes_entry = ctk.CTkEntry(r, width=280)
        notes_entry.pack(side="left", padx=(5, 0))
        if salt and salt.notes: notes_entry.insert(0, salt.notes)

        # ── Ionenbeitrag ──
        ctk.CTkLabel(scroll, text=t("salts.section_ions"),
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(15, 4))
        ctk.CTkLabel(scroll, text=t("salts.ions_hint"),
                     font=ctk.CTkFont(size=11), text_color="gray50").pack(anchor="w")

        ion_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        ion_frame.pack(fill="x", pady=(5, 0))
        ion_rows = []

        def _add_ion_row(ion_sym="", stoich_val=""):
            r = ctk.CTkFrame(ion_frame, fg_color="transparent")
            r.pack(fill="x", pady=2)
            iv = ctk.StringVar(value=ion_sym)
            ctk.CTkOptionMenu(r, values=AVAILABLE_IONS, variable=iv, width=120).pack(side="left")
            se = ctk.CTkEntry(r, width=80, placeholder_text="1.0")
            se.pack(side="left", padx=(8, 0))
            if stoich_val: se.insert(0, stoich_val)
            ctk.CTkButton(r, text="✕", width=28, height=28, fg_color="transparent",
                          border_width=1, command=lambda: (r.destroy(), ion_rows.remove((iv, se)))
                          ).pack(side="left", padx=(5, 0))
            ion_rows.append((iv, se))

        if salt:
            for sym, stoich in salt.ion_contribution.items():
                _add_ion_row(sym, str(stoich))
        else:
            _add_ion_row()

        ctk.CTkButton(scroll, text=t("salts.btn_add_ion"), width=160, height=28,
                      font=ctk.CTkFont(size=11), command=lambda: _add_ion_row()
                      ).pack(anchor="w", pady=(5, 0))

        status = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12))
        status.pack(anchor="w", pady=(10, 0))

        def _save():
            name = fields["name"].get().strip()
            formula = fields["formula"].get().strip()
            if not name or not formula:
                status.configure(text=t("salts.err_required"), text_color="#e74c3c"); return
            try:
                molar = float(fields["molar_mass"].get())
                sol = float(fields["solubility_20"].get())
            except ValueError:
                status.configure(text=t("salts.err_numbers"), text_color="#e74c3c"); return
            ions = {}
            for iv, se in ion_rows:
                sym = iv.get(); val = se.get().strip()
                if sym and val:
                    try: ions[sym] = float(val)
                    except ValueError: pass
            if not ions:
                status.configure(text=t("salts.err_ions"), text_color="#e74c3c"); return

            new_salt = Salt(name=name, formula=formula, molar_mass=molar,
                            solubility_20=sol, tank=tank_var.get(),
                            ion_contribution=ions, notes=notes_entry.get().strip(),
                            category=cat_var.get())
            save_custom_salt(new_salt)
            DEFAULT_SALTS[formula] = new_salt
            self._populate_table()
            status.configure(text=t("salts.saved"), text_color="#4CAF50")
            win.after(800, win.destroy)

        ctk.CTkButton(scroll, text=t("salts.btn_save"), height=36,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=_save).pack(fill="x", pady=(15, 5))
