"""Export/Import: Rezepte, Wasserprofile, Wachstumspläne teilen."""
import json
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog
from ui.views.base_view import BaseView
from chemistry.recipes import NutrientRecipe
from chemistry.water import WaterProfile
from database.data_manager import (
    load_all_recipes, save_custom_recipe,
    load_all_water_profiles, save_custom_water_profile,
)
from ui.locales import t, warn_fmt


class ExportImportView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("export.title"),
                         subtitle=t("export.subtitle"))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)

        left = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))

        self._build_export(left)
        self._build_import(right)

    def refresh_data(self):
        recipes = load_all_recipes()
        self.export_recipe_dd.configure(values=[t("export.all_label")] + list(recipes.keys()))
        water = load_all_water_profiles()
        self.export_water_dd.configure(values=[t("export.all_label")] + list(water.keys()))

    # ─── Export ───────────────────────────────────────────────────────

    def _build_export(self, parent):
        card_r = self._create_card(parent, title=t("export.card_recipes"))
        card_r.pack(fill="x", pady=(0, 8))

        recipes = load_all_recipes()
        self.export_recipe_dd = self._create_labeled_dropdown(
            card_r, label=t("c.recipe"),
            values=[t("export.all_label")] + list(recipes.keys()),
            default=t("export.all_label"))

        ctk.CTkButton(card_r, text=t("export.btn_recipe"), height=35,
                      command=self._export_recipes).pack(fill="x", padx=15, pady=(5, 12))

        card_w = self._create_card(parent, title=t("export.card_water"))
        card_w.pack(fill="x", pady=(0, 8))

        water = load_all_water_profiles()
        self.export_water_dd = self._create_labeled_dropdown(
            card_w, label=t("export.profile"),
            values=[t("export.all_label")] + list(water.keys()),
            default=t("export.all_label"))

        ctk.CTkButton(card_w, text=t("export.btn_water"), height=35,
                      command=self._export_water).pack(fill="x", padx=15, pady=(5, 12))

        # Preview
        card_p = self._create_card(parent, title=t("export.card_preview"))
        card_p.pack(fill="x", pady=(0, 8))
        self.export_tb = ctk.CTkTextbox(
            card_p, height=250, font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=("gray85", "gray20"), corner_radius=8)
        self.export_tb.pack(fill="x", padx=15, pady=(5, 12))

        self.export_status = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=12))
        self.export_status.pack(pady=(0, 5))

    # ─── Import ───────────────────────────────────────────────────────

    def _build_import(self, parent):
        card = self._create_card(parent, title=t("import.card"))
        card.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(card, text=t("import.hint"),
                     font=ctk.CTkFont(size=11), text_color="gray50"
                     ).pack(padx=15, pady=(8, 5), anchor="w")

        ctk.CTkButton(card, text=t("import.btn_open"), height=35,
                      command=self._import_file).pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

        self.import_tb = ctk.CTkTextbox(
            card, height=200, font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=("gray85", "gray20"), corner_radius=8)
        self.import_tb.pack(fill="x", padx=15, pady=(5, 5))

        ctk.CTkButton(card, text=t("import.btn"), height=38,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._import_json).pack(fill="x", padx=15, pady=(5, 12))

        self.import_status = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=12))
        self.import_status.pack(pady=(5, 5))

        # Import-Ergebnis
        card2 = self._create_card(parent, title=t("import.card_result"))
        card2.pack(fill="x", pady=(0, 8))
        self.import_result_tb = ctk.CTkTextbox(
            card2, height=150, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", fg_color=("gray85", "gray20"), corner_radius=8)
        self.import_result_tb.pack(fill="x", padx=15, pady=(5, 12))

    def _set_tb(self, tb, text, readonly=True):
        tb.configure(state="normal"); tb.delete("1.0", "end")
        tb.insert("1.0", text)
        if readonly: tb.configure(state="disabled")

    # ─── Export Logic ─────────────────────────────────────────────────

    def _recipe_to_dict(self, name, recipe):
        return {
            "type": "recipe",
            "name": name,
            "description": recipe.description,
            "source": recipe.source,
            "suitable_plants": recipe.suitable_plants,
            "ec_target": recipe.ec_target,
            "ph_min": recipe.ph_min,
            "ph_max": recipe.ph_max,
            "ions_mg": {
                "no3_n": recipe.no3_n, "nh4_n": recipe.nh4_n,
                "p": recipe.p, "k": recipe.k, "ca": recipe.ca,
                "mg": recipe.mg, "s": recipe.s,
                "fe": recipe.fe, "mn": recipe.mn, "zn": recipe.zn,
                "cu": recipe.cu, "b": recipe.b, "mo": recipe.mo,
            }
        }

    def _water_to_dict(self, name, profile):
        return {
            "type": "water_profile",
            "name": name,
            "ec": profile.ec, "ph": profile.ph,
            "ions_mg": {
                "ca": profile.ca, "mg": profile.mg, "na": profile.na,
                "k": profile.k, "cl": profile.cl, "so4": profile.so4,
                "hco3": profile.hco3, "no3": profile.no3, "fe": profile.fe,
            }
        }

    def _export_recipes(self):
        recipes = load_all_recipes()
        selected = self.export_recipe_dd.get()

        if selected == t("export.all_label"):
            data = [self._recipe_to_dict(n, r) for n, r in recipes.items()]
        else:
            r = recipes.get(selected)
            if not r: return
            data = [self._recipe_to_dict(selected, r)]

        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        self.export_tb.delete("1.0", "end")
        self.export_tb.insert("1.0", json_str)

        # Datei speichern
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[(t("export.json_label"), "*.json")],
            initialfile=f"rezepte_{selected.replace(' ', '_')}.json" if selected != t('c.all') else t("export.all_recipes_file"))
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
            self.export_status.configure(text=warn_fmt("d.exported", Path(path).name), text_color="#4CAF50")

    def _export_water(self):
        profiles = load_all_water_profiles()
        selected = self.export_water_dd.get()

        if selected == t("export.all_label"):
            data = [self._water_to_dict(n, p) for n, p in profiles.items()]
        else:
            p = profiles.get(selected)
            if not p: return
            data = [self._water_to_dict(selected, p)]

        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        self.export_tb.delete("1.0", "end")
        self.export_tb.insert("1.0", json_str)

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="wasserprofile.json")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
            self.export_status.configure(text=warn_fmt("d.exported", Path(path).name), text_color="#4CAF50")

    # ─── Import Logic ─────────────────────────────────────────────────

    def _import_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("CSV", "*.csv"), (t("export.all_files"), "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.import_tb.delete("1.0", "end")
            self.import_tb.insert("1.0", content)
            self.import_status.configure(text=f"📂 Geladen: {Path(path).name}", text_color="#4CAF50")
        except Exception as e:
            self.import_status.configure(text=f"⚠️ {t('c.error')}: {e}", text_color="#e74c3c")

    def _import_json(self):
        content = self.import_tb.get("1.0", "end").strip()
        if not content:
            self.import_status.configure(text="⚠️ Kein JSON eingegeben", text_color="#e8a838")
            return

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            self.import_status.configure(text=f"⚠️ JSON {t('c.error')}: {e}", text_color="#e74c3c")
            return

        if isinstance(data, dict):
            data = [data]

        imported_recipes = 0
        imported_water = 0
        results = []

        for item in data:
            item_type = item.get("type", "")
            name = item.get("name", "Unbenannt")

            if item_type == "recipe":
                try:
                    ions = item.get("ions_mg", {})
                    recipe = NutrientRecipe(
                        name=name,
                        description=item.get("description", t("c.imported")),
                        source=item.get("source", "Import"),
                        suitable_plants=item.get("suitable_plants", []),
                        ec_target=float(item.get("ec_target", 0)),
                        ph_min=float(item.get("ph_min", 5.5)),
                        ph_max=float(item.get("ph_max", 6.5)),
                        no3_n=float(ions.get("no3_n", 0)),
                        nh4_n=float(ions.get("nh4_n", 0)),
                        p=float(ions.get("p", 0)),
                        k=float(ions.get("k", 0)),
                        ca=float(ions.get("ca", 0)),
                        mg=float(ions.get("mg", 0)),
                        s=float(ions.get("s", 0)),
                        fe=float(ions.get("fe", 0)),
                        mn=float(ions.get("mn", 0)),
                        zn=float(ions.get("zn", 0)),
                        cu=float(ions.get("cu", 0)),
                        b=float(ions.get("b", 0)),
                        mo=float(ions.get("mo", 0)),
                    )
                    save_custom_recipe(recipe)
                    imported_recipes += 1
                    results.append(f"✅ {t('c.recipe')} {name}")
                except Exception as e:
                    results.append(f"⚠️ {t('c.recipe')} {name}: {e}")

            elif item_type == "water_profile":
                try:
                    ions = item.get("ions_mg", {})
                    profile = WaterProfile(
                        name=name,
                        ec=float(item.get("ec", 0)),
                        ph=float(item.get("ph", 7.0)),
                        ca=float(ions.get("ca", 0)),
                        mg=float(ions.get("mg", 0)),
                        na=float(ions.get("na", 0)),
                        k=float(ions.get("k", 0)),
                        cl=float(ions.get("cl", 0)),
                        so4=float(ions.get("so4", 0)),
                        hco3=float(ions.get("hco3", 0)),
                        no3=float(ions.get("no3", 0)),
                        fe=float(ions.get("fe", 0)),
                    )
                    save_custom_water_profile(profile)
                    imported_water += 1
                    results.append(f"✅ {t('export.profile')} {name}")
                except Exception as e:
                    results.append(f"⚠️ {t('export.profile')} {name}: {e}")
            else:
                results.append(f"⚠️ Unbekannter Typ: {item_type}")

        self.import_status.configure(
            text=warn_fmt("d.imported", imported_recipes, imported_water),
            text_color="#4CAF50")
        self._set_tb(self.import_result_tb, "\n".join(results))
