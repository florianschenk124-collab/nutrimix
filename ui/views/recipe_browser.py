"""
Rezept-Browser: Übersicht aller gespeicherten Rezepte.
Verknüpft mit Chemistry-Backend und Daten-Manager.
"""

import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.ions import ION_BY_SYMBOL
from database.data_manager import load_all_recipes, delete_custom_recipe
from ui.locales import t, td


class RecipeBrowserView(BaseView):
    def __init__(self, parent):
        super().__init__(
            parent,
            title=t("recipes.title"),
            subtitle=t("recipes.subtitle"),
        )

        self.recipes = load_all_recipes()

        self.content.grid_rowconfigure(1, weight=1)

        # Toolbar
        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        self.search_entry = ctk.CTkEntry(
            toolbar, placeholder_text=t("c.search_recipe"), width=300,
            textvariable=self.search_var,
        )
        self.search_entry.pack(side="left")

        self.filter_dropdown = ctk.CTkOptionMenu(
            toolbar, values=[t("recipes.filter_all"), t("recipes.filter_standard"), t("recipes.filter_custom")],
            width=160, command=self._on_filter,
        )
        self.filter_dropdown.pack(side="left", padx=(10, 0))

        ctk.CTkButton(
            toolbar, text=t("recipes.refresh"), width=130,
            command=self._refresh,
        ).pack(side="right")

        # Rezeptliste
        self.recipe_scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.recipe_scroll.grid(row=1, column=0, sticky="nswe")
        self.recipe_scroll.grid_columnconfigure(0, weight=1)

        self._populate_list()

    def refresh_data(self):
        """Wird aufgerufen wenn die View sichtbar wird."""
        self._refresh()

    def _refresh(self):
        self.recipes = load_all_recipes()
        self._populate_list()

    def _on_search(self, *args):
        self._populate_list()

    def _on_filter(self, *args):
        self._populate_list()

    def _populate_list(self):
        # Alte Karten entfernen
        for widget in self.recipe_scroll.winfo_children():
            widget.destroy()

        search = self.search_var.get().lower()
        filt = self.filter_dropdown.get()

        for name, recipe in self.recipes.items():
            # Filter
            if filt == t("recipes.filter_standard") and recipe.is_custom:
                continue
            if filt == t("recipes.filter_custom") and not recipe.is_custom:
                continue
            # Suche
            if search and search not in name.lower() and search not in recipe.description.lower():
                matching_plant = any(search in p.lower() for p in recipe.suitable_plants)
                if not matching_plant:
                    continue

            self._add_recipe_card(recipe)

    def _add_recipe_card(self, recipe):
        mg = recipe.as_mg_dict()
        ion_parts = []
        for sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4"]:
            val = mg.get(sym, 0)
            if val > 0:
                ion_parts.append(f"{ION_BY_SYMBOL[sym].display}: {val:.0f}")
        ion_summary = " | ".join(ion_parts)

        card = ctk.CTkFrame(self.recipe_scroll, corner_radius=10,
                            fg_color=("gray92", "gray17"))
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
        inner.grid_columnconfigure(0, weight=1)

        # Titel + Custom-Badge
        title_frame = ctk.CTkFrame(inner, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(title_frame, text=recipe.name,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        if recipe.is_custom:
            ctk.CTkLabel(title_frame, text="  " + t("c.custom_tag"),
                         font=ctk.CTkFont(size=11), text_color="#e8a838").pack(side="left")

        # Beschreibung
        ctk.CTkLabel(inner, text=td(recipe.description),
                     font=ctk.CTkFont(size=11), text_color="gray60",
                     anchor="w").grid(row=1, column=0, sticky="w", pady=(2, 2))

        # Pflanzen
        if recipe.suitable_plants:
            ctk.CTkLabel(inner, text="🌱 " + ", ".join(recipe.suitable_plants),
                         font=ctk.CTkFont(size=11), text_color="#4CAF50",
                         anchor="w").grid(row=2, column=0, sticky="w")

        # Ionenübersicht
        ctk.CTkLabel(inner, text=ion_summary,
                     font=ctk.CTkFont(family="Consolas", size=10),
                     text_color="gray50", anchor="w",
                     wraplength=450).grid(row=3, column=0, sticky="w", pady=(2, 0))

        # EC + pH
        info_parts = []
        if recipe.ec_target > 0:
            info_parts.append(f"EC: {recipe.ec_target:.1f}")
        info_parts.append(f"pH: {recipe.ph_min}–{recipe.ph_max}")
        if recipe.source:
            info_parts.append(recipe.source)
        ctk.CTkLabel(inner, text=" | ".join(info_parts),
                     font=ctk.CTkFont(size=10), text_color="gray40",
                     anchor="w").grid(row=4, column=0, sticky="w", pady=(2, 0))

        # Detail-Button
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.grid(row=0, column=1, rowspan=5, padx=(15, 0))

        ctk.CTkButton(btn_frame, text=t("c.details"), width=80, height=28,
                      font=ctk.CTkFont(size=11), fg_color="transparent",
                      border_width=1, border_color="gray40",
                      command=lambda r=recipe: self._show_detail(r)).pack(pady=(0, 4))

        if recipe.is_custom:
            ctk.CTkButton(btn_frame, text=t("c.delete"), width=80, height=28,
                          font=ctk.CTkFont(size=11), fg_color="transparent",
                          border_width=1, border_color="#c0392b", text_color="#e74c3c",
                          command=lambda r=recipe: self._delete_recipe(r)).pack()

    def _show_detail(self, recipe):
        """Zeigt Rezeptdetails in einem Popup."""
        win = ctk.CTkToplevel(self)
        win.title(f"{t('c.recipe')} {recipe.name}")
        win.geometry("450x500")
        win.grab_set()

        tb = ctk.CTkTextbox(win, font=ctk.CTkFont(family="Consolas", size=12))
        tb.pack(fill="both", expand=True, padx=15, pady=15)

        mg = recipe.as_mg_dict()
        mmol = recipe.as_mmol_dict()

        lines = [f"═══ {recipe.name} ═══", f"{recipe.description}", ""]
        lines.append(f"{'Ion':<10} {'mg/L':>8} {'mmol/L':>8}")
        lines.append("─" * 28)
        for sym in ["NO3", "NH4", "H2PO4", "K", "Ca", "Mg", "SO4",
                     "Fe", "Mn", "Zn", "Cu", "B", "Mo"]:
            m = mg.get(sym, 0)
            mm = mmol.get(sym, 0)
            if m > 0:
                lines.append(f"{ION_BY_SYMBOL[sym].display:<10} {m:>8.2f} {mm:>8.4f}")

        lines.extend(["", f"{t('growth.ec_target')}: {recipe.ec_target:.1f} mS/cm",
                       f"pH: {recipe.ph_min}–{recipe.ph_max}",
                       f"{t('compare.plants')}: {', '.join(recipe.suitable_plants)}",
                       f"{t('growth.source_label')}: {recipe.source}"])

        tb.insert("1.0", "\n".join(lines))
        tb.configure(state="disabled")

    def _delete_recipe(self, recipe):
        delete_custom_recipe(recipe.name)
        self._refresh()
