"""
Pflanzen-Guide: Welches Rezept passt zu welcher Pflanze.
Jetzt mit Möglichkeit eigene Pflanzen hinzuzufügen.
"""

import customtkinter as ctk
from ui.views.base_view import BaseView
from database.data_manager import load_all_recipes, load_all_plants, save_custom_plant, delete_custom_plant, DEFAULT_PLANTS
from ui.locales import t, td, td


class PlantGuideView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("plants.title"),
                         subtitle=t("plants.subtitle"))

        self.content.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        ctk.CTkEntry(toolbar, placeholder_text=t("c.search_plant"), width=250,
                     textvariable=self.search_var).pack(side="left")

        self.filter_dropdown = ctk.CTkOptionMenu(
            toolbar, values=[t("plants.filter_all"), t("plants.filter_fruit"), t("plants.filter_leafy"), t("plants.filter_herbs"), t("plants.filter_brassica"), t("plants.filter_other")],
            width=140, command=self._on_search)
        self.filter_dropdown.pack(side="left", padx=(10, 0))

        ctk.CTkButton(toolbar, text=t("plants.btn_add"), width=160,
                      command=self._add_plant_dialog).pack(side="right")

        self.plant_scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.plant_scroll.grid(row=1, column=0, sticky="nswe")
        self.plant_scroll.grid_columnconfigure(0, weight=1)
        self._populate_list()

    def refresh_data(self):
        self._populate_list()

    def _on_search(self, *args):
        self._populate_list()

    def _populate_list(self):
        for w in self.plant_scroll.winfo_children():
            w.destroy()
        search = self.search_var.get().lower()
        filt = self.filter_dropdown.get()
        recipes = load_all_recipes()
        plants = load_all_plants()
        default_names = {p["name"] for p in DEFAULT_PLANTS}

        for plant in plants:
            if filt != t("plants.filter_all"):
                # Map translated filter to stored category
                cat_map = {t("plants.filter_fruit"): "Fruchtgemüse", t("plants.filter_leafy"): "Blattgemüse",
                           t("plants.filter_herbs"): "Kräuter", t("plants.filter_brassica"): "Kohlgemüse",
                           t("plants.filter_other"): "Sonstiges"}
                if plant.get("category", "") != cat_map.get(filt, filt):
                    continue
            if search:
                matches = search in plant["name"].lower() or any(search in kw for kw in plant.get("keywords", []))
                if not matches:
                    continue
            matching = []
            for rname, recipe in recipes.items():
                for kw in plant.get("keywords", []):
                    if any(kw in p.lower() for p in recipe.suitable_plants):
                        matching.append(rname)
                        break
                if "Universell" in recipe.suitable_plants and rname not in matching:
                    matching.append(rname)

            is_custom = plant["name"] not in default_names
            self._add_plant_card(plant, matching, is_custom)

    def _add_plant_card(self, plant, matching_recipes, is_custom):
        card = ctk.CTkFrame(self.plant_scroll, corner_radius=10, fg_color=("gray92", "gray17"))
        card.pack(fill="x", pady=4)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
        inner.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(inner, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_frame, text=plant["name"],
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(title_frame, text=f"  [{td(plant.get('category', ''))}]",
                     font=ctk.CTkFont(size=11), text_color="gray50").pack(side="left")
        if is_custom:
            ctk.CTkLabel(title_frame, text="  " + t("c.custom_tag_f"),
                         font=ctk.CTkFont(size=11), text_color="#e8a838").pack(side="left")

        ctk.CTkLabel(inner, text=f"EC: {plant.get('ec_min',0)}–{plant.get('ec_max',0)} mS/cm  |  pH: {plant.get('ph_min',0)}–{plant.get('ph_max',0)}",
                     font=ctk.CTkFont(size=12), text_color="#4CAF50", anchor="w").grid(row=1, column=0, sticky="w", pady=(2, 2))

        if matching_recipes:
            ctk.CTkLabel(inner, text="📋 " + ", ".join(matching_recipes[:4]),
                         font=ctk.CTkFont(size=11), text_color="#e8a838", anchor="w",
                         wraplength=400).grid(row=2, column=0, sticky="w")

        ctk.CTkLabel(inner, text=td(plant.get("notes", "")),
                     font=ctk.CTkFont(size=11), text_color="gray50", anchor="w",
                     wraplength=450).grid(row=3, column=0, sticky="w", pady=(2, 0))

        if is_custom:
            ctk.CTkButton(inner, text="🗑", width=30, height=28, fg_color="transparent",
                          border_width=1, border_color="#c0392b", text_color="#e74c3c",
                          command=lambda n=plant["name"]: self._delete_plant(n)
                          ).grid(row=0, column=1, rowspan=2, padx=(10, 0))

    def _delete_plant(self, name):
        delete_custom_plant(name)
        self._populate_list()

    def _add_plant_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title(t("plants.add_title"))
        win.geometry("420x520")
        win.grab_set()

        fields = {}
        for label, key, ph in [("Name (mit Emoji):", "name", "🌿 Petersilie"),
                                (t("plants.category"), "category", t("plants.filter_herbs")),
                                ("EC min:", "ec_min", "1.0"),
                                ("EC max:", "ec_max", "2.0"),
                                ("pH min:", "ph_min", "5.5"),
                                ("pH max:", "ph_max", "6.5"),
                                (t("plants.notes_label"), "notes", t("plants.notes_ph")),
                                ("Suchbegriffe:", "keywords", "petersilie, parsley")]:
            ctk.CTkLabel(win, text=label, font=ctk.CTkFont(size=12)).pack(padx=20, pady=(8, 2), anchor="w")
            e = ctk.CTkEntry(win, placeholder_text=ph, width=360)
            e.pack(padx=20)
            fields[key] = e

        status = ctk.CTkLabel(win, text="", font=ctk.CTkFont(size=12))
        status.pack(pady=5)

        def _save():
            name = fields["name"].get().strip()
            if not name:
                status.configure(text="⚠️ Name fehlt!", text_color="#e8a838")
                return
            kw_str = fields["keywords"].get().strip()
            plant = {
                "name": name,
                "category": fields["category"].get().strip() or t("plants.filter_other"),
                "ec_min": float(fields["ec_min"].get() or 1.0),
                "ec_max": float(fields["ec_max"].get() or 2.0),
                "ph_min": float(fields["ph_min"].get() or 5.5),
                "ph_max": float(fields["ph_max"].get() or 6.5),
                "notes": fields["notes"].get().strip(),
                "keywords": [k.strip() for k in kw_str.split(",") if k.strip()],
            }
            save_custom_plant(plant)
            self._populate_list()
            win.destroy()

        ctk.CTkButton(win, text=t("plants.btn_save"), height=38, command=_save).pack(fill="x", padx=20, pady=15)
