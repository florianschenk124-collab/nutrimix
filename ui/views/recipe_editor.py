"""
Rezept-Editor: Neues Rezept erstellen oder bestehendes bearbeiten.
Verknüpft mit Daten-Manager für Persistenz.
"""

import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.recipes import NutrientRecipe
from database.data_manager import load_all_recipes, save_custom_recipe
from ui.locales import t, salt_name, warn_fmt


MACRO_FIELDS = [
    ("NO₃-N", "no3_n"), ("NH₄-N", "nh4_n"), ("P", "p"),
    ("K", "k"), ("Ca", "ca"), ("Mg", "mg"), ("S", "s"),
]
MICRO_FIELDS = [
    ("Fe", "fe"), ("Mn", "mn"), ("Zn", "zn"),
    ("Cu", "cu"), ("B", "b"), ("Mo", "mo"),
]


class RecipeEditorView(BaseView):
    def __init__(self, parent):
        super().__init__(
            parent,
            title=t("editor.title"),
            subtitle=t("editor.subtitle"),
        )

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))

        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))

        self._build_meta_section(left)
        self._build_macro_section(left)
        self._build_micro_section(right)
        self._build_extra_section(right)
        self._build_actions(right)

    def refresh_data(self):
        """Wird aufgerufen wenn die View sichtbar wird."""
        recipes = load_all_recipes()
        self.template_dropdown.configure(values=["(Leer)"] + list(recipes.keys()))

    def _build_meta_section(self, parent):
        card = self._create_card(parent, title=t("editor.card_info"))
        card.pack(fill="x", pady=(0, 8))

        self.entry_name = self._create_labeled_entry(
            card, label=t("editor.name"), placeholder=t("editor.name_ph"))
        self.entry_desc = self._create_labeled_entry(
            card, label=t("editor.desc"), placeholder=t("editor.desc_ph"))
        self.entry_plants = self._create_labeled_entry(
            card, label=t("editor.plants"), placeholder=t("editor.plants_ph"))
        self.entry_source = self._create_labeled_entry(
            card, label=t("editor.source"), placeholder=t("editor.source_ph"))

        # Vorlage laden
        card_template = self._create_card(parent, title=t("editor.card_template"))
        card_template.pack(fill="x", pady=(0, 8))

        recipes = load_all_recipes()
        self.template_dropdown = self._create_labeled_dropdown(
            card_template, label=t("editor.template"),
            values=["(Leer)"] + list(recipes.keys()),
            default="(Leer)",
        )
        ctk.CTkButton(card_template, text=t("editor.apply"), height=30,
                      font=ctk.CTkFont(size=11),
                      command=self._load_template).pack(padx=15, pady=(5, 12))

        ctk.CTkFrame(card_template, fg_color="transparent", height=4).pack()

    def _build_macro_section(self, parent):
        card = self._create_card(parent, title=t("editor.card_macros"))
        card.pack(fill="x", pady=(0, 8))
        self.macro_entries = {}
        for label, key in MACRO_FIELDS:
            entry = self._create_labeled_entry(card, label=f"{label}:", placeholder="0.0")
            self.macro_entries[key] = entry
        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _build_micro_section(self, parent):
        card = self._create_card(parent, title=t("editor.card_micros"))
        card.pack(fill="x", pady=(0, 8))

        # Premix-Schnellauswahl
        from chemistry.salts import get_premixes
        premixes = get_premixes()
        premix_names = [t("editor.premix_manual")] + [salt_name(p.name) for p in premixes]

        self.premix_dropdown = self._create_labeled_dropdown(
            card, label=t("editor.premix"),
            values=premix_names, default=t("editor.premix_manual"),
        )
        self.premix_dropdown.configure(command=self._on_premix_selected)

        self.premix_info = ctk.CTkLabel(
            card, text="", font=ctk.CTkFont(size=10), text_color="gray50",
            wraplength=320, justify="left",
        )
        self.premix_info.pack(padx=15, pady=(0, 5), anchor="w")

        ctk.CTkFrame(card, height=1, fg_color="gray30").pack(fill="x", padx=15, pady=4)

        self.micro_entries = {}
        for label, key in MICRO_FIELDS:
            entry = self._create_labeled_entry(card, label=f"{label}:", placeholder="0.0")
            self.micro_entries[key] = entry
        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _on_premix_selected(self, name):
        """Premix gewählt → Mikrowerte automatisch befüllen."""
        if name == t("editor.premix_manual"):
            self.premix_info.configure(text="")
            return

        from chemistry.salts import get_premixes
        premixes = get_premixes()
        premix = next((p for p in premixes if salt_name(p.name) == name), None)
        if not premix:
            return

        # Typische Dosierung berechnen: 0.05 g/L für Ziel ~2 mg/L Fe
        fe_target = 2.5  # mg/L – typischer Wert
        fe_per_g = premix.premix_mg_per_g.get("Fe", 0)
        if fe_per_g > 0:
            g_per_l = fe_target / fe_per_g
        else:
            g_per_l = 0.05  # Fallback

        # Felder befüllen
        field_map = {"fe": "Fe", "mn": "Mn", "zn": "Zn", "cu": "Cu", "b": "B", "mo": "Mo"}
        info_parts = [f"{name} @ {g_per_l:.4f} g/L:"]
        for field_key, ion_sym in field_map.items():
            mg_per_g = premix.premix_mg_per_g.get(ion_sym, 0)
            mg_per_l = g_per_l * mg_per_g
            entry = self.micro_entries[field_key]
            entry.delete(0, "end")
            if mg_per_l > 0:
                entry.insert(0, f"{mg_per_l:.3f}")
                info_parts.append(f"{ion_sym}: {mg_per_l:.3f} mg/L")

        self.premix_info.configure(text="  |  ".join(info_parts))

    def _build_extra_section(self, parent):
        card = self._create_card(parent, title=t("editor.card_extra"))
        card.pack(fill="x", pady=(0, 8))
        self.entry_ec = self._create_labeled_entry(
            card, label=t("editor.ec_target"), placeholder="0.0")
        self.entry_ph_min = self._create_labeled_entry(
            card, label=t("editor.ph_min"), placeholder="5.5")
        self.entry_ph_max = self._create_labeled_entry(
            card, label=t("editor.ph_max"), placeholder="6.5")
        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _build_actions(self, parent):
        card = self._create_card(parent, title=t("editor.card_actions"))
        card.pack(fill="x", pady=(0, 8))

        self.status_label = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(padx=15, pady=(8, 0))

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=12)

        ctk.CTkButton(btn_frame, text=t("editor.btn_save"),
                      font=ctk.CTkFont(size=13, weight="bold"), height=40,
                      command=self._on_save).pack(fill="x", pady=(0, 6))
        ctk.CTkButton(btn_frame, text=t("editor.btn_reset"),
                      font=ctk.CTkFont(size=13), height=35,
                      fg_color="transparent", border_width=1, border_color="gray40",
                      command=self._on_reset).pack(fill="x")

    def _get_float(self, entry, default=0.0):
        try:
            return float(entry.get().strip())
        except (ValueError, TypeError):
            return default

    def _load_template(self):
        name = self.template_dropdown.get()
        if name == "(Leer)":
            self._on_reset()
            return
        recipes = load_all_recipes()
        recipe = recipes.get(name)
        if not recipe:
            return

        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, f"{recipe.name} ({t('c.copy')})")
        self.entry_desc.delete(0, "end")
        self.entry_desc.insert(0, recipe.description)
        self.entry_plants.delete(0, "end")
        self.entry_plants.insert(0, ", ".join(recipe.suitable_plants))
        self.entry_source.delete(0, "end")
        self.entry_source.insert(0, recipe.source)
        self.entry_ec.delete(0, "end")
        self.entry_ec.insert(0, str(recipe.ec_target))
        self.entry_ph_min.delete(0, "end")
        self.entry_ph_min.insert(0, str(recipe.ph_min))
        self.entry_ph_max.delete(0, "end")
        self.entry_ph_max.insert(0, str(recipe.ph_max))

        vals = {"no3_n": recipe.no3_n, "nh4_n": recipe.nh4_n, "p": recipe.p,
                "k": recipe.k, "ca": recipe.ca, "mg": recipe.mg, "s": recipe.s,
                "fe": recipe.fe, "mn": recipe.mn, "zn": recipe.zn,
                "cu": recipe.cu, "b": recipe.b, "mo": recipe.mo}

        for key, entry in {**self.macro_entries, **self.micro_entries}.items():
            entry.delete(0, "end")
            entry.insert(0, str(vals.get(key, 0.0)))

        self.status_label.configure(text=warn_fmt("d.recipe_loaded", name), text_color="#4CAF50")

    def _on_save(self):
        name = self.entry_name.get().strip()
        if not name:
            self.status_label.configure(text=t("d.enter_name"), text_color="#e8a838")
            return

        plants_str = self.entry_plants.get().strip()
        plants = [p.strip() for p in plants_str.split(",") if p.strip()] if plants_str else []

        recipe = NutrientRecipe(
            name=name,
            description=self.entry_desc.get().strip(),
            no3_n=self._get_float(self.macro_entries["no3_n"]),
            nh4_n=self._get_float(self.macro_entries["nh4_n"]),
            p=self._get_float(self.macro_entries["p"]),
            k=self._get_float(self.macro_entries["k"]),
            ca=self._get_float(self.macro_entries["ca"]),
            mg=self._get_float(self.macro_entries["mg"]),
            s=self._get_float(self.macro_entries["s"]),
            fe=self._get_float(self.micro_entries["fe"]),
            mn=self._get_float(self.micro_entries["mn"]),
            zn=self._get_float(self.micro_entries["zn"]),
            cu=self._get_float(self.micro_entries["cu"]),
            b=self._get_float(self.micro_entries["b"]),
            mo=self._get_float(self.micro_entries["mo"]),
            ph_min=self._get_float(self.entry_ph_min, 5.5),
            ph_max=self._get_float(self.entry_ph_max, 6.5),
            ec_target=self._get_float(self.entry_ec),
            suitable_plants=plants,
            source=self.entry_source.get().strip(),
            is_custom=True,
        )

        save_custom_recipe(recipe)
        self.status_label.configure(text=warn_fmt("d.saved", name), text_color="#4CAF50")

        # Template-Dropdown aktualisieren
        recipes = load_all_recipes()
        self.template_dropdown.configure(values=["(Leer)"] + list(recipes.keys()))

    def _on_reset(self):
        for entry in [self.entry_name, self.entry_desc, self.entry_plants,
                      self.entry_source, self.entry_ec, self.entry_ph_min,
                      self.entry_ph_max]:
            entry.delete(0, "end")
        for entry in {**self.macro_entries, **self.micro_entries}.values():
            entry.delete(0, "end")
        self.status_label.configure(text="")
