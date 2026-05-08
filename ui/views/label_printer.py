"""
Etikettendruck: PDF-Labels für Stammlösungs-Tanks generieren.

Erstellt druckbare Etiketten mit:
- Rezeptname, Datum
- Tank A / Tank B Inhalt (Salze + Einwaagen)
- Dosierhinweise, EC, pH-Bereich
- Warnhinweise
"""

import customtkinter as ctk
from datetime import datetime
from pathlib import Path
from ui.views.base_view import BaseView
from database.data_manager import (
    load_all_recipes, load_all_water_profiles, load_settings, apply_costs_to_salts,
)
from chemistry.solver import solve
from chemistry.water import subtract_water
from chemistry.ec_estimator import estimate_ec
from chemistry.ratios import check_ratios
from ui.locales import t, salt_name, warn_fmt


class LabelPrinterView(BaseView):
    def __init__(self, parent):
        super().__init__(parent, title=t("labels.title"),
                         subtitle=t("labels.subtitle"))

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)

        left = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))

        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))

        self._build_settings(left)
        self._build_preview(right)

    def refresh_data(self):
        recipes = load_all_recipes()
        self.recipe_dropdown.configure(values=list(recipes.keys()))
        water = load_all_water_profiles()
        self.water_dropdown.configure(values=list(water.keys()))

    def _build_settings(self, parent):
        card = self._create_card(parent, title=t("labels.card_settings"))
        card.pack(fill="x", pady=(0, 8))

        recipes = load_all_recipes()
        water_profiles = load_all_water_profiles()

        self.recipe_dropdown = self._create_labeled_dropdown(
            card, label=t("c.recipe"), values=list(recipes.keys()),
            default=list(recipes.keys())[0] if recipes else "")
        self.water_dropdown = self._create_labeled_dropdown(
            card, label=t("c.water_profile"), values=list(water_profiles.keys()),
            default="Osmosewasser")
        self.entry_volume = self._create_labeled_entry(
            card, label=t("c.volume_l"), placeholder="1000")
        self.entry_factor = self._create_labeled_entry(
            card, label=t("c.conc_factor"), placeholder="100")
        self.entry_tank_vol = self._create_labeled_entry(
            card, label=t("labels.tank_vol"), placeholder="10")

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

        card2 = self._create_card(parent, title=t("labels.card_options"))
        card2.pack(fill="x", pady=(0, 8))

        self.entry_author = self._create_labeled_entry(
            card2, label=t("labels.author"), placeholder="")
        self.entry_note = self._create_labeled_entry(
            card2, label=t("labels.note"), placeholder=t("labels.note_ph"))

        self.label_size = self._create_labeled_dropdown(
            card2, label=t("labels.format"), values=["A6 (105×148mm)", "A5 (148×210mm)", "A4 (210×297mm)"],
            default="A6 (105×148mm)")

        ctk.CTkFrame(card2, fg_color="transparent", height=8).pack()

        ctk.CTkButton(parent, text=t("labels.btn_preview"),
                      font=ctk.CTkFont(size=13), height=38,
                      command=self._update_preview).pack(fill="x", pady=(5, 5))

        ctk.CTkButton(parent, text=t("labels.btn_print"),
                      font=ctk.CTkFont(size=14, weight="bold"), height=45,
                      command=self._generate_pdf).pack(fill="x", pady=(0, 5))

        self.status_label = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(5, 0))

    def _build_preview(self, parent):
        card_a = self._create_card(parent, title=t("labels.preview_a"))
        card_a.pack(fill="x", pady=(0, 8))

        self.preview_a = ctk.CTkTextbox(card_a, height=280,
                                        font=ctk.CTkFont(family="Consolas", size=11),
                                        state="disabled", fg_color=("gray85", "gray20"),
                                        corner_radius=8)
        self.preview_a.pack(fill="x", padx=15, pady=(5, 12))

        card_b = self._create_card(parent, title=t("labels.preview_b"))
        card_b.pack(fill="x", pady=(0, 8))

        self.preview_b = ctk.CTkTextbox(card_b, height=280,
                                        font=ctk.CTkFont(family="Consolas", size=11),
                                        state="disabled", fg_color=("gray85", "gray20"),
                                        corner_radius=8)
        self.preview_b.pack(fill="x", padx=15, pady=(5, 12))

    def _get_float(self, entry, default):
        try:
            v = entry.get().strip()
            return float(v) if v else default
        except ValueError:
            return default

    def _set_tb(self, tb, text):
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.insert("1.0", text)
        tb.configure(state="disabled")

    def _compute(self):
        """Berechnung durchführen und Daten für Labels zurückgeben."""
        recipes = load_all_recipes()
        water_profiles = load_all_water_profiles()
        settings = load_settings()

        recipe = recipes.get(self.recipe_dropdown.get())
        water = water_profiles.get(self.water_dropdown.get())
        if not recipe or not water:
            return None

        volume = self._get_float(self.entry_volume, 1000)
        factor = self._get_float(self.entry_factor, 100)
        tank_vol = self._get_float(self.entry_tank_vol, volume / factor)

        target = recipe.as_mg_dict()
        adjusted, _ = subtract_water(target, water)
        result = solve(adjusted, volume, factor,
                       fe_chelate=settings.get("fe_chelate", "Fe-DTPA"),
                       nh4_source=settings.get("nh4_source", "NH4NO3"),
                       p_source=settings.get("p_source", "KH2PO4"),
                       micro_source=settings.get("micro_source", "individual"))

        ec = estimate_ec(result.achieved_mg, method=settings.get("ec_method", "ionic"))
        date = datetime.now().strftime("%d.%m.%Y")
        author = self.entry_author.get().strip()
        note = self.entry_note.get().strip()

        return {
            "recipe": recipe, "water": water, "result": result,
            "volume": volume, "factor": factor, "tank_vol": tank_vol,
            "ec": ec, "date": date, "author": author, "note": note,
        }

    def _format_tank_label(self, data, tank_letter):
        """Formatiert ein Tank-Label als Text."""
        r = data["result"]
        recipe = data["recipe"]
        salts = r.tank_a if tank_letter == "A" else r.tank_b

        lines = []
        lines.append(f"{'═' * 40}")
        lines.append(f"  {t('labels.stock_solution')} – TANK {tank_letter}")
        lines.append(f"{'═' * 40}")
        lines.append(f"  {t('labels.recipe_label')}     {recipe.name}")
        lines.append(f"  {t('labels.water_label')}     {data['water'].name}")
        lines.append(f"  Datum:      {data['date']}")
        if data["author"]:
            lines.append(f"  {t('labels.created_label')}   {data['author']}")
        lines.append(f"{'─' * 40}")
        lines.append(f"  Endvolumen:   {data['volume']:.0f} L")
        lines.append(f"  Konz.-Faktor: {data['factor']:.0f}x")
        lines.append(f"  Tankvolumen:  {data['tank_vol']:.1f} L")
        lines.append(f"{'─' * 40}")
        lines.append(f"  EINWAAGEN:")
        lines.append(f"  {t('labels.salt_col'):<28} {t('labels.grams_col'):>8}")
        lines.append(f"  {'─' * 38}")

        for sr in salts:
            g = sr.g_concentrate
            if g >= 1:
                lines.append(f"  {salt_name(sr.salt.name):<28} {g:>8.1f} g")
            elif g >= 0.01:
                lines.append(f"  {salt_name(sr.salt.name):<28} {g:>8.2f} g")
            else:
                lines.append(f"  {salt_name(sr.salt.name):<28} {g*1000:>7.1f} mg")

        lines.append(f"{'─' * 40}")
        lines.append(f"  {warn_fmt('labels.fill_up', f'{data['tank_vol']:.1f}')}")
        lines.append(f"{'─' * 40}")
        lines.append(f"  {t('c.ec_estimated')}: {data['ec']:.2f} mS/cm")
        lines.append(f"  pH-Bereich:     {recipe.ph_min}–{recipe.ph_max}")

        if tank_letter == "A":
            lines.append(f"  {t('labels.content_a')}")
        else:
            lines.append(f"  {t('labels.tank_content_b')}")

        lines.append(f"{'─' * 40}")
        lines.append(f"  ⚠️  Nicht Tank A und B mischen!")
        lines.append(f"  {t('labels.dose_first')}")
        if data["note"]:
            lines.append(f"  📝 {data['note']}")
        lines.append(f"{'═' * 40}")

        return "\n".join(lines)

    def _update_preview(self):
        data = self._compute()
        if not data:
            self._set_tb(self.preview_a, t("d.recipe_not_found2"))
            return
        self._set_tb(self.preview_a, self._format_tank_label(data, "A"))
        self._set_tb(self.preview_b, self._format_tank_label(data, "B"))

    def _generate_pdf(self):
        """Generiert ein PDF mit beiden Tank-Labels."""
        data = self._compute()
        if not data:
            self.status_label.configure(text=t("labels.calc_failed"), text_color="#e8a838")
            return

        try:
            self._create_pdf(data)
        except ImportError:
            # Fallback: Textdatei erstellen
            self._create_text_labels(data)

    def _create_pdf(self, data):
        """PDF mit reportlab erstellen."""
        from reportlab.lib.pagesizes import A4, A5, A6
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors

        size_map = {
            "A6 (105×148mm)": A6,
            "A5 (148×210mm)": A5,
            "A4 (210×297mm)": A4,
        }
        page_size = size_map.get(self.label_size.get(), A6)
        w, h = page_size

        # Ausgabepfad
        safe_name = data["recipe"].name.replace(" ", "_").replace("/", "-")
        filename = f"Label_{safe_name}_{data['date'].replace('.', '')}.pdf"
        out_dir = Path(__file__).parent.parent.parent / "user_data"
        out_dir.mkdir(exist_ok=True)
        filepath = out_dir / filename

        c = canvas.Canvas(str(filepath), pagesize=page_size)

        for tank_letter in ["A", "B"]:
            salts = data["result"].tank_a if tank_letter == "A" else data["result"].tank_b
            recipe = data["recipe"]

            margin = 8 * mm
            y = h - margin
            x = margin
            line_h = 3.5 * mm

            # Titel
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x, y, f"TANK {tank_letter} – {t('labels.stock_solution')}")
            y -= line_h * 2

            c.setFont("Helvetica", 9)
            c.drawString(x, y, f"{t('labels.recipe_label')} {recipe.name}")
            y -= line_h
            c.drawString(x, y, f"{t('labels.water_label')} {data['water'].name}")
            y -= line_h
            c.drawString(x, y, f"Datum: {data['date']}   Vol: {data['volume']:.0f}L   Faktor: {data['factor']:.0f}x   Tank: {data['tank_vol']:.1f}L")
            y -= line_h * 1.5

            # Trennlinie
            c.setStrokeColor(colors.grey)
            c.line(x, y, w - margin, y)
            y -= line_h

            # Einwaagen
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y, t("labels.weights"))
            y -= line_h * 1.2

            c.setFont("Helvetica", 9)
            for sr in salts:
                g = sr.g_concentrate
                if g >= 1:
                    txt = f"{salt_name(sr.salt.name)}: {g:.1f} g"
                elif g >= 0.01:
                    txt = f"{sr.salt.name}: {g:.2f} g"
                else:
                    txt = f"{sr.salt.name}: {g*1000:.1f} mg"
                c.drawString(x + 2*mm, y, txt)
                y -= line_h
                if y < margin + 20 * mm:
                    break

            y -= line_h * 0.5
            c.line(x, y, w - margin, y)
            y -= line_h

            c.setFont("Helvetica", 9)
            c.drawString(x, y, warn_fmt("labels.fill_up", f"{data['tank_vol']:.1f}"))
            y -= line_h
            c.drawString(x, y, f"EC ≈ {data['ec']:.2f} mS/cm  |  pH: {recipe.ph_min}–{recipe.ph_max}")
            y -= line_h * 1.5

            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.red)
            c.drawString(x, y, "⚠  Tank A und B NICHT direkt mischen!")
            c.setFillColor(colors.black)

            if data["note"]:
                y -= line_h
                c.setFont("Helvetica", 8)
                c.drawString(x, y, f"{t('labels.note_label')} {data['note']}")

            if data["author"]:
                y -= line_h
                c.setFont("Helvetica", 7)
                c.drawString(x, y, f"{t('labels.created_label')} {data['author']}")

            c.showPage()

        c.save()
        self.status_label.configure(
            text=warn_fmt("labels.pdf_saved", filepath.name), text_color="#4CAF50")

    def _create_text_labels(self, data):
        """Fallback: Textdatei wenn reportlab nicht verfügbar."""
        safe_name = data["recipe"].name.replace(" ", "_").replace("/", "-")
        filename = f"Label_{safe_name}_{data['date'].replace('.', '')}.txt"
        out_dir = Path(__file__).parent.parent.parent / "user_data"
        out_dir.mkdir(exist_ok=True)
        filepath = out_dir / filename

        content = self._format_tank_label(data, "A")
        content += "\n\n\n"
        content += self._format_tank_label(data, "B")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        self.status_label.configure(
            text=warn_fmt("labels.txt_saved", filepath.name),
            text_color="#e8a838")
