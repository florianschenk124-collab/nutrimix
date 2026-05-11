"""
Lokalisierung: Deutsch / Englisch Sprachunterstützung.
Verwendung:
    from ui.locales import t, set_language, get_language
    label = t("nav.calculator")  # → "Rechner" oder "Calculator"
"""
_current_language = "de"
TRANSLATIONS = {
    "app.title": {"de": "Pflanzenernährungs-Rechner", "en": "Plant Nutrition Calculator"},
    "nav.recipes": {"de": "Rezepte", "en": "Recipes"},
    "nav.new_recipe": {"de": "Neues Rezept", "en": "New Recipe"},
    "nav.recipe_compare": {"de": "Rezeptvergleich", "en": "Recipe Compare"},
    "nav.calculator": {"de": "Rechner", "en": "Calculator"},
    "nav.ph_correction": {"de": "pH-Korrektur", "en": "pH Correction"},
    "nav.dilution": {"de": "Verdünnung", "en": "Dilution"},
    "nav.reverse": {"de": "Rückwärtsrechner", "en": "Reverse Calc"},
    "nav.water_profiles": {"de": "Wasserprofile", "en": "Water Profiles"},
    "nav.plants": {"de": "Pflanzen", "en": "Plants"},
    "nav.growth_phases": {"de": "Wachstumsphasen", "en": "Growth Phases"},
    "nav.salt_database": {"de": "Salz-Datenbank", "en": "Salt Database"},
    "nav.compatibility": {"de": "Mischbarkeit", "en": "Compatibility"},
    "nav.costs": {"de": "Kosten", "en": "Costs"},
    "nav.labels": {"de": "Etiketten", "en": "Labels"},
    "nav.export_import": {"de": "Export/Import", "en": "Export/Import"},
    "nav.settings": {"de": "Einstellungen", "en": "Settings"},
    "nav.group.calculation": {"de": "Berechnung", "en": "Calculation"},
    "nav.group.data": {"de": "Daten", "en": "Data"},
    "nav.group.tools": {"de": "Werkzeuge", "en": "Tools"},
    # ── Common ──
    "c.recipe": {"de": "Rezept:", "en": "Recipe:"},
    "c.water_profile": {"de": "Wasserprofil:", "en": "Water Profile:"},
    "c.water": {"de": "Wasser:", "en": "Water:"},
    "c.volume_l": {"de": "Volumen (L):", "en": "Volume (L):"},
    "c.conc_factor": {"de": "Konz.-Faktor:", "en": "Conc. Factor:"},
    "c.dose_ratio": {"de": "Dosierverhältnis A:B:", "en": "Dosing Ratio A:B:"},
    "c.details": {"de": "Details", "en": "Details"},
    "c.delete": {"de": "Löschen", "en": "Delete"},
    "c.search_recipe": {"de": "🔍 Rezept suchen...", "en": "🔍 Search recipe..."},
    "c.search_salt": {"de": "🔍 Salz suchen...", "en": "🔍 Search salt..."},
    "c.search_plant": {"de": "🔍 Pflanze suchen...", "en": "🔍 Search plant..."},
    "c.custom_tag": {"de": "[Eigenes]", "en": "[Custom]"},
    "c.custom_tag_f": {"de": "[Eigene]", "en": "[Custom]"},
    "c.manual": {"de": "(Manuell)", "en": "(Manual)"},
    "c.all": {"de": "(Alle)", "en": "(All)"},
    "c.profile_load": {"de": "Profil laden:", "en": "Load Profile:"},
    "c.no_warnings": {"de": "✅ Keine Warnungen", "en": "✅ No warnings"},
    # ── Calculator ──
    "calc.title": {"de": "🧮 Stammlösungs-Rechner", "en": "🧮 Stock Solution Calculator"},
    "calc.subtitle": {"de": "Berechne Einwaagen für deine Nährlösung (8-Schritt-Verfahren)", "en": "Calculate salt weights for your nutrient solution (8-step method)"},
    "calc.card_recipe": {"de": "Rezept", "en": "Recipe"},
    "calc.units": {"de": "Einheiten:", "en": "Units:"},
    "calc.card_water": {"de": "Wasserprofil", "en": "Water Profile"},
    "calc.profile": {"de": "Profil:", "en": "Profile:"},
    "calc.card_params": {"de": "Parameter", "en": "Parameters"},
    "calc.target_vol": {"de": "Zielvolumen (L):", "en": "Target Volume (L):"},
    "calc.conc_factor": {"de": "Konzentratfaktor:", "en": "Concentrate Factor:"},
    "calc.card_salts": {"de": "Salzauswahl", "en": "Salt Options"},
    "calc.fe_chelate": {"de": "Fe-Chelat:", "en": "Fe Chelate:"},
    "calc.nh4_source": {"de": "NH₄-Quelle:", "en": "NH₄ Source:"},
    "calc.p_source": {"de": "P-Quelle:", "en": "P Source:"},
    "calc.micro_source": {"de": "Mikros:", "en": "Micros:"},
    "calc.btn": {"de": "⚗️  Berechnen", "en": "⚗️  Calculate"},
    "calc.tank_a": {"de": "Tank A – Calcium / Eisen", "en": "Tank A – Calcium / Iron"},
    "calc.tank_b": {"de": "Tank B – Sulfate / Phosphate / Mikro", "en": "Tank B – Sulfate / Phosphate / Micro"},
    "calc.target_actual": {"de": "Soll/Ist-Vergleich", "en": "Target/Actual Comparison"},
    "calc.summary": {"de": "Zusammenfassung", "en": "Summary"},
    "calc.ratios": {"de": "Nährstoff-Verhältnisse", "en": "Nutrient Ratios"},
    "calc.warnings": {"de": "Hinweise & Warnungen", "en": "Notes & Warnings"},
    "calc.protocol": {"de": "Berechnungsschritte (Protokoll)", "en": "Calculation Steps (Protocol)"},
    "calc.ec_est": {"de": "EC (geschätzt):", "en": "EC (estimated):"},
    "calc.ph_range": {"de": "pH-Bereich:", "en": "pH Range:"},
    "calc.solubility": {"de": "Löslichkeit:", "en": "Solubility:"},
    "calc.max_factor": {"de": "Max. Konz.-Faktor:", "en": "Max Conc. Factor:"},
    "calc.costs": {"de": "Kosten:", "en": "Costs:"},
    "calc.dose_label": {"de": "Dosierung A:B:", "en": "Dosing A:B:"},
    "calc.all_soluble": {"de": "✅ Alle Salze löslich", "en": "✅ All salts soluble"},
    "calc.no_prices": {"de": "– (keine Preise hinterlegt)", "en": "– (no prices set)"},
    "calc.micros_via": {"de": "📦 Mikros via:", "en": "📦 Micros via:"},
    # ── Recipes Browser ──
    "recipes.title": {"de": "📋 Rezepte", "en": "📋 Recipes"},
    "recipes.subtitle": {"de": "Übersicht aller Nährlösungs-Rezepte", "en": "Overview of all nutrient solution recipes"},
    "recipes.filter_all": {"de": "Alle Rezepte", "en": "All Recipes"},
    "recipes.filter_standard": {"de": "Standard", "en": "Standard"},
    "recipes.filter_custom": {"de": "Eigene Rezepte", "en": "Custom Recipes"},
    "recipes.refresh": {"de": "🔄 Aktualisieren", "en": "🔄 Refresh"},
    # ── Recipe Editor ──
    "editor.title": {"de": "➕ Neues Rezept", "en": "➕ New Recipe"},
    "editor.subtitle": {"de": "Erstelle ein eigenes Nährlösungs-Rezept (Werte in mg/L)", "en": "Create a custom nutrient solution recipe (values in mg/L)"},
    "editor.card_info": {"de": "Rezept-Info", "en": "Recipe Info"},
    "editor.name": {"de": "Rezeptname:", "en": "Recipe Name:"},
    "editor.name_ph": {"de": "z.B. Mein Tomaten-Rezept", "en": "e.g. My Tomato Recipe"},
    "editor.desc": {"de": "Beschreibung:", "en": "Description:"},
    "editor.desc_ph": {"de": "Kurze Beschreibung...", "en": "Short description..."},
    "editor.plants": {"de": "Pflanzen:", "en": "Plants:"},
    "editor.plants_ph": {"de": "z.B. Tomate, Paprika (kommagetrennt)", "en": "e.g. Tomato, Pepper (comma separated)"},
    "editor.source": {"de": "Quelle:", "en": "Source:"},
    "editor.source_ph": {"de": "z.B. Eigene Erfahrung", "en": "e.g. Own experience"},
    "editor.card_template": {"de": "Vorlage laden", "en": "Load Template"},
    "editor.template": {"de": "Vorlage:", "en": "Template:"},
    "editor.apply": {"de": "Werte übernehmen", "en": "Apply Values"},
    "editor.card_macros": {"de": "Makronährstoffe (mg/L)", "en": "Macronutrients (mg/L)"},
    "editor.card_micros": {"de": "Mikronährstoffe (mg/L)", "en": "Micronutrients (mg/L)"},
    "editor.premix": {"de": "Premix verwenden:", "en": "Use Premix:"},
    "editor.premix_manual": {"de": "(Manuell eingeben)", "en": "(Enter manually)"},
    "editor.card_extra": {"de": "Zusatzparameter", "en": "Additional Parameters"},
    "editor.ec_target": {"de": "EC-Ziel (mS/cm):", "en": "EC Target (mS/cm):"},
    "editor.ph_min": {"de": "pH min:", "en": "pH min:"},
    "editor.ph_max": {"de": "pH max:", "en": "pH max:"},
    "editor.card_actions": {"de": "Aktionen", "en": "Actions"},
    "editor.btn_save": {"de": "💾 Rezept speichern", "en": "💾 Save Recipe"},
    "editor.btn_reset": {"de": "🔄 Zurücksetzen", "en": "🔄 Reset"},
    "editor.saved": {"de": "✅ Rezept gespeichert!", "en": "✅ Recipe saved!"},
    "editor.err_name": {"de": "⚠️ Bitte Rezeptname eingeben!", "en": "⚠️ Please enter a recipe name!"},
    # ── Compare ──
    "compare.title": {"de": "⚖️ Rezeptvergleich", "en": "⚖️ Recipe Comparison"},
    "compare.subtitle": {"de": "Zwei Rezepte Seite an Seite vergleichen", "en": "Compare two recipes side by side"},
    "compare.recipe_a": {"de": "Rezept A:", "en": "Recipe A:"},
    "compare.recipe_b": {"de": "Rezept B:", "en": "Recipe B:"},
    "compare.btn": {"de": "⚖️ Vergleichen", "en": "⚖️ Compare"},
    "compare.card_ions": {"de": "Ionenvergleich (mg/L)", "en": "Ion Comparison (mg/L)"},
    "compare.card_ratios": {"de": "Verhältnisse", "en": "Ratios"},
    "compare.card_summary": {"de": "Zusammenfassung", "en": "Summary"},
    # ── pH ──
    "ph.title": {"de": "🧪 pH-Korrektur", "en": "🧪 pH Correction"},
    "ph.subtitle": {"de": "Säure-/Basenbedarf zur pH-Einstellung berechnen", "en": "Calculate acid/base needed for pH adjustment"},
    "ph.card_water": {"de": "Wasserquelle", "en": "Water Source"},
    "ph.card_params": {"de": "Parameter", "en": "Parameters"},
    "ph.hco3": {"de": "HCO₃⁻ (mg/L):", "en": "HCO₃⁻ (mg/L):"},
    "ph.water_ph": {"de": "Wasser-pH:", "en": "Water pH:"},
    "ph.target_ph": {"de": "Ziel-pH:", "en": "Target pH:"},
    "ph.card_acid_base": {"de": "Säure / Base", "en": "Acid / Base"},
    "ph.acid": {"de": "Säure:", "en": "Acid:"},
    "ph.base": {"de": "Base:", "en": "Base:"},
    "ph.btn": {"de": "⚗️  Berechnen", "en": "⚗️  Calculate"},
    "ph.card_result": {"de": "Ergebnis", "en": "Result"},
    "ph.card_steps": {"de": "Berechnungsschritte", "en": "Calculation Steps"},
    "ph.card_notes": {"de": "Hinweise", "en": "Notes"},
    "ph.extra_ions": {"de": "Zusätzliche Ionen:", "en": "Additional ions:"},
    "ph.ion_note": {"de": "⚠️  Diese Ionen im Rechner berücksichtigen!", "en": "⚠️  Account for these ions in the calculator!"},
    # ── Dilution ──
    "dil.title": {"de": "🔬 Verdünnungsrechner", "en": "🔬 Dilution Calculator"},
    "dil.subtitle": {"de": "Stammlösung → Gebrauchslösung mit Ziel-EC", "en": "Stock solution → Working solution with target EC"},
    "dil.card_stock": {"de": "Stammlösung", "en": "Stock Solution"},
    "dil.card_dilution": {"de": "Verdünnung", "en": "Dilution"},
    "dil.target_ec": {"de": "Ziel-EC (mS/cm):", "en": "Target EC (mS/cm):"},
    "dil.water_ec": {"de": "Wasser-EC:", "en": "Water EC:"},
    "dil.btn": {"de": "🔬  Berechnen", "en": "🔬  Calculate"},
    "dil.btn_table": {"de": "📊  Verdünnungstabelle", "en": "📊  Dilution Table"},
    "dil.card_dosing": {"de": "Dosierung", "en": "Dosing"},
    "dil.card_ions": {"de": "Ionenkonzentrationen (verdünnt)", "en": "Ion Concentrations (diluted)"},
    "dil.card_table": {"de": "Verdünnungstabelle", "en": "Dilution Table"},
    "dil.select_first": {"de": "⚠️ Erst Stammlösung wählen", "en": "⚠️ Select stock solution first"},
    # ── Reverse ──
    "rev.title": {"de": "🔄 Rückwärtsrechner", "en": "🔄 Reverse Calculator"},
    "rev.subtitle": {"de": "Salzeinwaagen eingeben → Ionenkonzentrationen berechnen", "en": "Enter salt weights → Calculate ion concentrations"},
    "rev.card_volume": {"de": "Volumen", "en": "Volume"},
    "rev.end_volume": {"de": "Endvolumen (L):", "en": "Final Volume (L):"},
    "rev.card_add": {"de": "Salz hinzufügen", "en": "Add Salt"},
    "rev.salt": {"de": "Salz:", "en": "Salt:"},
    "rev.grams": {"de": "Einwaage (g):", "en": "Weight (g):"},
    "rev.btn_add": {"de": "➕ Hinzufügen", "en": "➕ Add"},
    "rev.card_list": {"de": "Eingewogene Salze", "en": "Weighed Salts"},
    "rev.btn_clear": {"de": "🗑 Alle entfernen", "en": "🗑 Remove All"},
    "rev.btn": {"de": "🔄  Berechnen", "en": "🔄  Calculate"},
    "rev.card_ions": {"de": "Ionenkonzentrationen", "en": "Ion Concentrations"},
    "rev.card_ratios": {"de": "Nährstoff-Verhältnisse & EC", "en": "Nutrient Ratios & EC"},
    "rev.card_match": {"de": "Ähnlichstes Rezept", "en": "Closest Recipe Match"},
    "rev.card_steps": {"de": "Berechnungsschritte", "en": "Calculation Steps"},
    "rev.no_salts": {"de": "⚠️ Keine Salze eingetragen", "en": "⚠️ No salts entered"},
    # ── Water Profiles ──
    "water.title": {"de": "💧 Wasserprofile", "en": "💧 Water Profiles"},
    "water.subtitle": {"de": "Wasseranalysen verwalten – werden bei der Berechnung berücksichtigt", "en": "Manage water analyses – used in calculations"},
    "water.card_list": {"de": "Gespeicherte Profile", "en": "Saved Profiles"},
    "water.btn_new": {"de": "➕ Neues Profil", "en": "➕ New Profile"},
    "water.btn_delete": {"de": "🗑 Löschen", "en": "🗑 Delete"},
    "water.card_edit": {"de": "Profil bearbeiten", "en": "Edit Profile"},
    "water.name": {"de": "Profilname:", "en": "Profile Name:"},
    "water.name_ph": {"de": "z.B. Leitungswasser Berlin", "en": "e.g. Tap water Berlin"},
    "water.ec": {"de": "EC (mS/cm):", "en": "EC (mS/cm):"},
    "water.ph": {"de": "pH:", "en": "pH:"},
    "water.ions_header": {"de": "Ionenkonzentrationen (mg/L)", "en": "Ion Concentrations (mg/L)"},
    "water.btn_save": {"de": "💾 Profil speichern", "en": "💾 Save Profile"},
    "water.saved": {"de": "✅ Profil gespeichert!", "en": "✅ Profile saved!"},
    "water.new_hint": {"de": "Neues Profil – Werte eintragen", "en": "New profile – enter values"},
    "water.deleted": {"de": "🗑 Profil gelöscht", "en": "🗑 Profile deleted"},
    # ── Plants ──
    "plants.title": {"de": "🌱 Pflanzen-Guide", "en": "🌱 Plant Guide"},
    "plants.subtitle": {"de": "Empfohlene Nährlösungs-Rezepte nach Pflanzenart", "en": "Recommended nutrient recipes by plant type"},
    "plants.btn_add": {"de": "➕ Pflanze hinzufügen", "en": "➕ Add Plant"},
    "plants.add_title": {"de": "Pflanze hinzufügen", "en": "Add Plant"},
    "plants.name": {"de": "Name:", "en": "Name:"},
    "plants.name_ph": {"de": "z.B. Basilikum", "en": "e.g. Basil"},
    "plants.category": {"de": "Kategorie:", "en": "Category:"},
    "plants.btn_save": {"de": "💾 Speichern", "en": "💾 Save"},
    # ── Growth ──
    "growth.title": {"de": "📅 Wachstumsphasen", "en": "📅 Growth Phases"},
    "growth.subtitle": {"de": "Wochenbasierte Nährstoffanpassung über die Kulturperiode", "en": "Week-based nutrient adjustment over the crop cycle"},
    "growth.card_select": {"de": "Wachstumsplan auswählen", "en": "Select Growth Plan"},
    "growth.plan": {"de": "Plan:", "en": "Plan:"},
    "growth.card_phases": {"de": "Phasenübersicht", "en": "Phase Overview"},
    "growth.card_timeline": {"de": "Wochenplan (Zeitstrahl)", "en": "Weekly Schedule (Timeline)"},
    "growth.card_week": {"de": "Wochendetail", "en": "Week Detail"},
    "growth.week": {"de": "Woche:", "en": "Week:"},
    "growth.no_recipe": {"de": "⚠️ Basisrezept nicht gefunden", "en": "⚠️ Base recipe not found"},
    "growth.transition": {"de": "Übergang", "en": "Transition"},
    # ── Salts ──
    "salts.title": {"de": "🧂 Salz-Datenbank", "en": "🧂 Salt Database"},
    "salts.subtitle": {"de": "Verfügbare Düngesalze und ihre Eigenschaften", "en": "Available fertilizer salts and their properties"},
    # ── Compatibility ──
    "compat.title": {"de": "🔬 Mischbarkeitsmatrix", "en": "🔬 Compatibility Matrix"},
    "compat.subtitle": {"de": "Welche Salze dürfen zusammen gelöst werden?", "en": "Which salts can be mixed together?"},
    "compat.matrix": {"de": "Matrix", "en": "Matrix"},
    "compat.pair_check": {"de": "Einzelprüfung", "en": "Pair Check"},
    "compat.legend": {"de": "✅ OK  |  ℹ️ Hinweis  |  ⚠️ Vorsicht  |  ⛔ NICHT mischen", "en": "✅ OK  |  ℹ️ Note  |  ⚠️ Caution  |  ⛔ DO NOT mix"},
    "compat.click_detail": {"de": "Klicke auf ein Feld für Details", "en": "Click a cell for details"},
    "compat.card_check": {"de": "Zwei Salze prüfen", "en": "Check Two Salts"},
    "compat.salt_a": {"de": "Salz A:", "en": "Salt A:"},
    "compat.salt_b": {"de": "Salz B:", "en": "Salt B:"},
    "compat.btn_check": {"de": "🔍 Prüfen", "en": "🔍 Check"},
    "compat.compatible": {"de": "Kompatibel", "en": "Compatible"},
    "compat.severity": {"de": "Schweregrad", "en": "Severity"},
    "compat.precipitate": {"de": "Ausfällung", "en": "Precipitate"},
    "compat.card_result": {"de": "Ergebnis", "en": "Result"},
    # ── Costs ──
    "costs.title": {"de": "💰 Kosten-Manager", "en": "💰 Cost Manager"},
    "costs.subtitle": {"de": "Salzpreise pflegen und Rezeptkosten berechnen", "en": "Manage salt prices and calculate recipe costs"},
    "costs.card_prices": {"de": "Salzpreise (EUR/kg)", "en": "Salt Prices (EUR/kg)"},
    "costs.prices_hint": {"de": "Trage hier deine Einkaufspreise ein:", "en": "Enter your purchase prices here:"},
    "costs.btn_save": {"de": "💾 Preise speichern", "en": "💾 Save Prices"},
    "costs.saved": {"de": "✅ Preise gespeichert!", "en": "✅ Prices saved!"},
    "costs.card_calc": {"de": "Rezeptkosten berechnen", "en": "Calculate Recipe Costs"},
    "costs.btn_calc": {"de": "💰 Kosten berechnen", "en": "💰 Calculate Costs"},
    "costs.card_result": {"de": "Kostenaufstellung", "en": "Cost Breakdown"},
    "costs.card_compare": {"de": "Rezept-Kostenvergleich", "en": "Recipe Cost Comparison"},
    "costs.btn_compare": {"de": "📊 Alle Rezepte vergleichen", "en": "📊 Compare All Recipes"},
    # ── Labels ──
    "labels.title": {"de": "🏷️ Etikettendruck", "en": "🏷️ Label Printing"},
    "labels.subtitle": {"de": "PDF-Etiketten für Stammlösungs-Tanks erstellen", "en": "Create PDF labels for stock solution tanks"},
    "labels.card_settings": {"de": "Etikett-Einstellungen", "en": "Label Settings"},
    "labels.tank_vol": {"de": "Tankvolumen (L):", "en": "Tank Volume (L):"},
    "labels.card_options": {"de": "Label-Optionen", "en": "Label Options"},
    "labels.author": {"de": "Erstellt von:", "en": "Created by:"},
    "labels.note": {"de": "Zusatzhinweis:", "en": "Additional Note:"},
    "labels.note_ph": {"de": "z.B. Für Gewächshaus 3", "en": "e.g. For Greenhouse 3"},
    "labels.format": {"de": "Format:", "en": "Format:"},
    "labels.btn_preview": {"de": "👁 Vorschau aktualisieren", "en": "👁 Update Preview"},
    "labels.btn_print": {"de": "🖨️ PDF erstellen & speichern", "en": "🖨️ Create & Save PDF"},
    "labels.preview_a": {"de": "Vorschau: Tank A", "en": "Preview: Tank A"},
    "labels.preview_b": {"de": "Vorschau: Tank B", "en": "Preview: Tank B"},
    # ── Export/Import ──
    "export.title": {"de": "📦 Export / Import", "en": "📦 Export / Import"},
    "export.subtitle": {"de": "Rezepte und Wasserprofile als JSON-Dateien teilen", "en": "Share recipes and water profiles as JSON files"},
    "export.card_recipes": {"de": "Rezepte exportieren", "en": "Export Recipes"},
    "export.card_water": {"de": "Wasserprofile exportieren", "en": "Export Water Profiles"},
    "export.profile": {"de": "Profil:", "en": "Profile:"},
    "export.btn_recipe": {"de": "💾 Rezept(e) exportieren", "en": "💾 Export Recipe(s)"},
    "export.btn_water": {"de": "💾 Profil(e) exportieren", "en": "💾 Export Profile(s)"},
    "export.card_preview": {"de": "Vorschau / Manuelle Eingabe", "en": "Preview / Manual Entry"},
    "import.card": {"de": "JSON importieren", "en": "Import JSON"},
    "import.hint": {"de": "Datei auswählen oder JSON unten einfügen:", "en": "Select a file or paste JSON below:"},
    "import.btn_open": {"de": "📂 Datei öffnen...", "en": "📂 Open File..."},
    "import.btn": {"de": "📥 Importieren", "en": "📥 Import"},
    "import.card_result": {"de": "Import-Ergebnis", "en": "Import Result"},
    "import.no_json": {"de": "⚠️ Kein JSON eingegeben", "en": "⚠️ No JSON entered"},
    # ── Settings ──
    "settings.title": {"de": "⚙️ Einstellungen", "en": "⚙️ Settings"},
    "settings.subtitle": {"de": "Allgemeine Konfiguration und Regelwerk", "en": "General configuration and calculation rules"},
    "settings.card_general": {"de": "Allgemein", "en": "General"},
    "settings.default_unit": {"de": "Standard-Einheit:", "en": "Default Unit:"},
    "settings.default_conc": {"de": "Standard Konz.-Faktor:", "en": "Default Conc. Factor:"},
    "settings.default_vol": {"de": "Standard Volumen (L):", "en": "Default Volume (L):"},
    "settings.card_ec": {"de": "EC-Schätzung", "en": "EC Estimation"},
    "settings.ec_method": {"de": "Methode:", "en": "Method:"},
    "settings.ec_hint": {"de": "'ionic' = ionenspezifisch (genauer)\n'simple' = TDS-basiert (schnell)", "en": "'ionic' = ion-specific (accurate)\n'simple' = TDS-based (fast)"},
    "settings.card_lang": {"de": "Sprache / Language", "en": "Language / Sprache"},
    "settings.language": {"de": "Sprache / Language:", "en": "Language / Sprache:"},
    "settings.lang_hint": {"de": "🔄 Änderung wird nach Neustart wirksam\n🔄 Change takes effect after restart", "en": "🔄 Change takes effect after restart\n🔄 Änderung wird nach Neustart wirksam"},
    "settings.card_salts": {"de": "Standard-Salzauswahl", "en": "Default Salt Options"},
    "settings.micro_nutrients": {"de": "Mikronährstoffe:", "en": "Micronutrients:"},
    "settings.btn_save": {"de": "💾 Einstellungen speichern", "en": "💾 Save Settings"},
    "settings.saved": {"de": "✅ Einstellungen gespeichert!", "en": "✅ Settings saved!"},
    "settings.card_rules": {"de": "Regelwerk (8-Schritt-Verfahren)", "en": "Rules (8-Step Method)"},
    "settings.card_db": {"de": "Datenbank", "en": "Database"},
    "settings.db_hint": {"de": "Benutzerdaten werden unter\n./user_data/ gespeichert (JSON)", "en": "User data is stored in\n./user_data/ (JSON)"},
    "settings.btn_reset": {"de": "🔄 Auf Standard zurücksetzen", "en": "🔄 Reset to Defaults"},
    "settings.reset_done": {"de": "🔄 Datenbank zurückgesetzt (Neustart empfohlen)", "en": "🔄 Database reset (restart recommended)"},

    # ═══ Web-Frontend zusätzliche Keys ═══

    # ── Calculator ──
    "calc.fe_label": {"de": "Fe-Chelat", "en": "Fe Chelate"},
    "calc.nh4_label": {"de": "NH₄-Quelle", "en": "NH₄ Source"},
    "calc.p_label": {"de": "P-Quelle", "en": "P Source"},
    "calc.auto_info": {"de": "Ca-Quelle: Ca(NO₃)₂ · Mg-Quelle: MgSO₄ · K-Rest: K₂SO₄/KNO₃ · NO₃-Rest: KNO₃ – werden automatisch vom Solver gewählt.", "en": "Ca source: Ca(NO₃)₂ · Mg source: MgSO₄ · K remainder: K₂SO₄/KNO₃ · NO₃ remainder: KNO₃ – chosen automatically by the solver."},
    "calc.col_ion": {"de": "Ion", "en": "Ion"},
    "calc.col_salt": {"de": "Salz", "en": "Salt"},
    "calc.col_g_l": {"de": "g/L", "en": "g/L"},
    "calc.col_g_total": {"de": "g gesamt", "en": "g total"},
    "calc.col_water": {"de": "Wasser", "en": "Water"},
    "calc.col_delta": {"de": "Δ mg/L", "en": "Δ mg/L"},
    "calc.col_g_conc": {"de": "g/L Konz.", "en": "g/L conc."},
    "calc.col_solubility": {"de": "Löslichkeit", "en": "Solubility"},
    "calc.col_saturation": {"de": "Sättigung", "en": "Saturation"},
    "calc.col_status": {"de": "Status", "en": "Status"},
    "calc.ab_ok": {"de": "✅ A/B-Trennung korrekt", "en": "✅ A/B separation correct"},

    # ── Compatibility ──
    "compat.stat_salts": {"de": "Salze", "en": "Salts"},
    "compat.stat_ok": {"de": "Kompatibel", "en": "Compatible"},
    "compat.stat_warn": {"de": "Warnung", "en": "Warning"},
    "compat.stat_critical": {"de": "Kritisch", "en": "Critical"},
    "compat.filter_all": {"de": "Alle", "en": "All"},
    "compat.col_salt_a": {"de": "Salz A", "en": "Salt A"},
    "compat.col_salt_b": {"de": "Salz B", "en": "Salt B"},
    "compat.col_precip": {"de": "Niederschlag", "en": "Precipitate"},
    "compat.col_desc": {"de": "Beschreibung", "en": "Description"},

    # ── Costs ──
    "costs.cat_macro": {"de": "Makro", "en": "Macro"},
    "costs.cat_chelate": {"de": "Chelate", "en": "Chelates"},
    "costs.cat_micro": {"de": "Mikro", "en": "Micro"},
    "costs.stat_total": {"de": "Gesamtkosten", "en": "Total Cost"},
    "costs.stat_per_l": {"de": "Pro Liter", "en": "Per Liter"},
    "costs.err": {"de": "Fehler", "en": "Error"},

    # ── Dilution ──
    "dil.tank_a_per_l": {"de": "Tank A pro Liter", "en": "Tank A per Liter"},
    "dil.tank_b_per_l": {"de": "Tank B pro Liter", "en": "Tank B per Liter"},
    "dil.tank_a_total": {"de": "Tank A gesamt", "en": "Tank A total"},
    "dil.tank_b_total": {"de": "Tank B gesamt", "en": "Tank B total"},
    "dil.ec_achieved": {"de": "EC erreicht", "en": "EC achieved"},
    "dil.factor": {"de": "Verdünnungsfaktor", "en": "Dilution factor"},
    "dil.col_diluted": {"de": "mg/L (verdünnt)", "en": "mg/L (diluted)"},

    # ── Export/Import ──
    "export.card_full": {"de": "📦 Vollständiger Export", "en": "📦 Full Export"},
    "export.full_desc": {"de": "Alle Rezepte und Wasserprofile in einer Datei.", "en": "All recipes and water profiles in one file."},
    "export.btn_full": {"de": "Alles exportieren", "en": "Export all"},
    "export.card_import": {"de": "📥 Import", "en": "📥 Import"},
    "export.import_desc": {"de": "JSON-Datei hochladen oder einfügen.", "en": "Upload or paste a JSON file."},
    "export.file_label": {"de": "Datei auswählen", "en": "Choose file"},
    "export.paste_label": {"de": "Oder JSON einfügen", "en": "Or paste JSON"},
    "export.btn_import": {"de": "📥 Importieren", "en": "📥 Import"},
    "export.card_format": {"de": "ℹ️ Format-Hilfe", "en": "ℹ️ Format Help"},
    "export.import_hint": {"de": "JSON-Datei hochladen oder einfügen.", "en": "Upload or paste a JSON file."},
    "export.msg_recipes": {"de": "Rezept(e) exportiert", "en": "recipe(s) exported"},
    "export.msg_water": {"de": "Wasserprofil(e) exportiert", "en": "water profile(s) exported"},
    "export.msg_full": {"de": "Vollständiger Export erstellt", "en": "Full export created"},
    "export.msg_imported": {"de": "Importiert", "en": "Imported"},
    "export.msg_errors": {"de": "Fehler", "en": "error(s)"},
    "export.msg_nothing": {"de": "Nichts importiert", "en": "Nothing imported"},
    "export.msg_bad_json": {"de": "Ungültiges JSON", "en": "Invalid JSON"},
    "export.msg_no_data": {"de": "Keine Daten", "en": "No data"},

    # ── Growth Phases ──
    "growth.auto": {"de": "(Auto)", "en": "(Auto)"},
    "growth.adjusted_mg": {"de": "Angepasste mg/L", "en": "Adjusted mg/L"},
    "growth.schedule_err": {"de": "Schedule-Fehler", "en": "Schedule error"},

    # ── Labels ──
    "labels.tank_a_desc": {"de": "Calcium / Eisen", "en": "Calcium / Iron"},
    "labels.tank_b_desc": {"de": "Sulfate / Phosphate", "en": "Sulfates / Phosphates"},
    "labels.dosing": {"de": "Dosierung", "en": "Dosing"},
    "labels.no_mix": {"de": "⚠️ Nicht mischen! Tank A und B getrennt ins Wasser geben.", "en": "⚠️ Do not mix! Add Tank A and B separately to water."},
    "labels.btn_generate": {"de": "🔬 Etiketten erstellen", "en": "🔬 Generate Labels"},
    "labels.concentrate": {"de": "Konzentrat", "en": "Concentrate"},

    # ── pH Correction ──
    "ph.buf_title": {"de": "🧫 Pufferkapazitäts-Analyse (rezeptbasiert)", "en": "🧫 Buffer Capacity Analysis (recipe-based)"},
    "ph.buf_desc": {"de": "Berechnet die Pufferkapazität der Nährlösung anhand der Ionenkonzentrationen aus einem Rezept. H₂PO₄⁻/HPO₄²⁻ ist der wichtigste Puffer in hydroponischen Systemen (pKa 7.2).", "en": "Calculates the buffer capacity of the nutrient solution based on ion concentrations from a recipe. H₂PO₄⁻/HPO₄²⁻ is the most important buffer in hydroponic systems (pKa 7.2)."},
    "ph.buf_btn": {"de": "🧫 Pufferkapazität berechnen", "en": "🧫 Calculate Buffer Capacity"},
    "ph.buf_select": {"de": "– auswählen –", "en": "– select –"},
    "ph.buf_total": {"de": "Gesamt-Pufferkapazität", "en": "Total Buffer Capacity"},
    "ph.buf_rating": {"de": "Bewertung", "en": "Rating"},
    "ph.buf_good": {"de": "Gut gepuffert", "en": "Well buffered"},
    "ph.buf_moderate": {"de": "Moderat", "en": "Moderate"},
    "ph.buf_weak": {"de": "Schwach gepuffert", "en": "Weakly buffered"},
    "ph.buf_col_system": {"de": "Puffersystem", "en": "Buffer System"},
    "ph.buf_col_contrib": {"de": "Beitrag", "en": "Contribution"},
    "ph.buf_hint": {"de": "β = Pufferkapazität bei pH {ph}. Je höher β, desto stabiler der pH. Der H₂PO₄⁻/HPO₄²⁻-Puffer (pKa 7.2) ist bei pH 5.5–6.5 der dominante Puffer. Höhere P-Konzentrationen → stabilerer pH, aber Vorsicht bei Ca-Ausfällung.", "en": "β = Buffer capacity at pH {ph}. The higher β, the more stable the pH. The H₂PO₄⁻/HPO₄²⁻ buffer (pKa 7.2) is the dominant buffer at pH 5.5–6.5. Higher P concentrations → more stable pH, but watch for Ca precipitation."},
    "ph.col_total": {"de": "Gesamt", "en": "Total"},
    "ph.col_addition": {"de": "mg/L Zusatz", "en": "mg/L added"},

    # ── Placeholder ──
    "ui.coming_soon": {"de": "Kommt bald…", "en": "Coming soon…"},

    # ── Plants ──
    "plants.no_match": {"de": "Keine passenden Rezepte", "en": "No matching recipes"},
    "plants.matching": {"de": "Passende Rezepte:", "en": "Matching recipes:"},

    # ── RecipeCompare ──
    "compare.card_ions": {"de": "Ionenkonzentrationen (mg/L)", "en": "Ion Concentrations (mg/L)"},
    "compare.card_visual": {"de": "Visueller Vergleich", "en": "Visual Comparison"},

    # ── RecipeEditor ──
    "editor.empty": {"de": "(Leer)", "en": "(Empty)"},
    "editor.err_name": {"de": "⚠ Name erforderlich", "en": "⚠ Name required"},

    # ── Water Profiles ──
    "water.btn_edit": {"de": "✏️ Bearbeiten", "en": "✏️ Edit"},
    "water.btn_delete": {"de": "🗑 Löschen", "en": "🗑 Delete"},
    "water.cancel": {"de": "Abbrechen", "en": "Cancel"},
    "water.new": {"de": "Neues Profil", "en": "New Profile"},

    # ── General ──
    "gen.error": {"de": "Fehler", "en": "Error"},
    "gen.ion": {"de": "Ion", "en": "Ion"},
    "gen.mg_l": {"de": "mg/L", "en": "mg/L"},
    "gen.mmol_l": {"de": "mmol/L", "en": "mmol/L"},

    # ── Alpha Banner ──
    "alpha.disclaimer": {"de": "Dies ist eine Alpha-Version. Berechnungen können Fehler enthalten. Ergebnisse immer unabhängig prüfen, bevor sie in der Praxis eingesetzt werden.", "en": "This is an alpha version. Calculations may contain errors. Always verify results independently before use in production."},

    # ── Additional EN keys for views ──
    "recipes.stat_n_total": {"de": "N gesamt", "en": "Total N"},
    "recipes.stat_source": {"de": "Quelle", "en": "Source"},
    "recipes.card_macros": {"de": "Makronährstoffe (mg/L)", "en": "Macronutrients (mg/L)"},
    "recipes.card_micros": {"de": "Mikronährstoffe (mg/L)", "en": "Micronutrients (mg/L)"},
    "settings.ec_ionic_label": {"de": "Ionenspezifisch (genauer)", "en": "Ion-specific (accurate)"},
    "settings.ec_simple_label": {"de": "TDS-basiert (schnell)", "en": "TDS-based (fast)"},
    "settings.fe_label": {"de": "Fe-Chelat:", "en": "Fe Chelate:"},
    "settings.nh4_label": {"de": "NH₄-Quelle:", "en": "NH₄ Source:"},
    "settings.p_label": {"de": "P-Quelle:", "en": "P Source:"},
    "settings.dose_label": {"de": "Dosierverhältnis A:B:", "en": "Dosing Ratio A:B:"},
    "salts.count": {"de": "Salze", "en": "Salts"},
    "recipes.plants_label": {"de": "Geeignete Pflanzen", "en": "Suitable Plants"},
}

def t(key: str) -> str:
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(_current_language, entry.get("de", key))

def set_language(lang: str):
    global _current_language
    if lang in ("de", "en"):
        _current_language = lang

def get_language() -> str:
    return _current_language

def init_language():
    try:
        from database.data_manager import load_settings
        settings = load_settings()
        lang = settings.get("language", "de")
        set_language(lang)
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════
# Backend: Solver & Ratios
# ═══════════════════════════════════════════════════════════════
TRANSLATIONS.update({
    # Solver steps
    "b.step": {"de": "Schritt", "en": "Step"},
    "b.for_fe": {"de": "für Fe-Bedarf", "en": "for Fe demand"},
    "b.fe_via_premix": {"de": "Fe wird durch Premix ({}) in Schritt 7 gedeckt",
                        "en": "Fe covered by premix ({}) in step 7"},
    "b.ca_demand": {"de": "Ca-Bedarf decken", "en": "cover Ca demand"},
    "b.delivers": {"de": "liefert", "en": "delivers"},
    "b.delivers_also": {"de": "liefert auch", "en": "also delivers"},
    "b.simultaneous": {"de": "gleichzeitig", "en": "simultaneously"},
    "b.remaining": {"de": "restlicher", "en": "remaining"},
    "b.demand": {"de": "Bedarf", "en": "demand"},
    "b.pure_p": {"de": "reine P-Quelle", "en": "pure P source"},
    "b.rest": {"de": "Rest", "en": "remaining"},
    "b.excess_possible": {"de": "Überschuss möglich", "en": "excess possible"},
    "b.excess": {"de": "Überschuss", "en": "excess"},
    "b.covered_via": {"de": "über {} gedeckt", "en": "covered via {}"},
    "b.additional_needed": {"de": "Zusätzlich {} nötig", "en": "Additional {} needed"},
    "b.more_than_target": {"de": "mehr als Ziel", "en": "more than target"},
    "b.and_other_sources": {"de": "durch {} und andere {}-Quellen", "en": "from {} and other {} sources"},
    "b.micro_individual": {"de": "Mikros als Einzelsalze", "en": "micros as individual salts"},
    "b.micro_premix": {"de": "Mikros via Premix:", "en": "Micros via premix:"},

    # Solver warnings
    "b.warn_k_rest": {"de": "K-Restbedarf: {:.1f} mg/L K über K₂SO₄ gedeckt (SO₄-Überschuss möglich)",
                      "en": "K remaining: {:.1f} mg/L K covered via K₂SO₄ (SO₄ excess possible)"},
    "b.warn_no3_rest": {"de": "NO₃-Restbedarf: Zusätzlich KNO₃ nötig → K-Überschuss von {:.1f} mg/L",
                        "en": "NO₃ remaining: Additional KNO₃ needed → K excess of {:.1f} mg/L"},
    "b.warn_no3_excess": {"de": "NO₃-Überschuss: {:.1f} mg/L N mehr als Ziel (durch Ca(NO₃)₂ und andere NO₃-Quellen)",
                          "en": "NO₃ excess: {:.1f} mg/L N more than target (from Ca(NO₃)₂ and other NO₃ sources)"},

    # Ratio warnings
    "b.too_low": {"de": "zu niedrig", "en": "too low"},
    "b.too_high": {"de": "zu hoch", "en": "too high"},
    "b.ratio_warn.ca_mg_low": {"de": "Mg kann die Ca-Aufnahme hemmen. Ca erhöhen oder Mg reduzieren.",
                               "en": "Mg can inhibit Ca uptake. Increase Ca or reduce Mg."},
    "b.ratio_warn.ca_mg_high": {"de": "Ca-Überschuss kann Mg-Mangel verursachen.",
                                "en": "Ca excess can cause Mg deficiency."},
    "b.ratio_warn.k_camg_low": {"de": "K-Mangel relativ zu Ca+Mg. K erhöhen.",
                                "en": "K deficiency relative to Ca+Mg. Increase K."},
    "b.ratio_warn.k_camg_high": {"de": "K-Überschuss kann Ca/Mg-Aufnahme hemmen.",
                                 "en": "K excess can inhibit Ca/Mg uptake."},
    "b.ratio_warn.n_k_low": {"de": "Mehr N relativ zu K nötig für ausgeglichenes Wachstum.",
                             "en": "More N relative to K needed for balanced growth."},
    "b.ratio_warn.n_k_high": {"de": "Zu viel N relativ zu K → vegetatives Wachstum dominiert.",
                              "en": "Too much N relative to K → vegetative growth dominates."},
    "b.ratio_warn.ca_k_low": {"de": "K-Überschuss kann Ca-Aufnahme blockieren (Blütenendfäule!).",
                              "en": "K excess can block Ca uptake (blossom end rot!)."},
    "b.ratio_warn.ca_k_high": {"de": "Ca-Überschuss, K-Versorgung prüfen.",
                               "en": "Ca excess, check K supply."},
    "b.ratio_warn.s_n_low": {"de": "S-Mangel möglich, Aminosäure-Synthese beeinträchtigt.",
                             "en": "S deficiency possible, amino acid synthesis impaired."},
    "b.ratio_warn.s_n_high": {"de": "S-Überschuss, kann Wachstum hemmen.",
                              "en": "S excess, may inhibit growth."},

    # Ratio descriptions
    "b.ratio_desc.ca_mg": {"de": "Verhindert Mg-induzierte Ca-Mangelerscheinung",
                           "en": "Prevents Mg-induced Ca deficiency"},
    "b.ratio_desc.k_camg": {"de": "Erhält das Kationen-Gleichgewicht",
                            "en": "Maintains cation balance"},
    "b.ratio_desc.n_k": {"de": "Balanciert Protein- vs. Kohlenhydrat-Synthese",
                         "en": "Balances protein vs. carbohydrate synthesis"},
    "b.ratio_desc.ca_k": {"de": "Vermeidet K-induzierte Ca-Blockade",
                          "en": "Prevents K-induced Ca blockade"},
    "b.ratio_desc.s_n": {"de": "Sichert S für Aminosäuren, verhindert Überschuss",
                         "en": "Ensures S for amino acids, prevents excess"},

    # Ratio summary
    "b.ratios_header": {"de": "Kritische Nährstoff-Verhältnisse:", "en": "Critical Nutrient Ratios:"},
    "b.actual": {"de": "Ist", "en": "Actual"},
    "b.target": {"de": "Soll", "en": "Target"},
})

def step(n, detail=""):
    """Format a solver step: 'Schritt N: detail' / 'Step N: detail'"""
    prefix = f"{t('b.step')} {n}"
    return f"{prefix}: {detail}" if detail else prefix

def warn_fmt(key, *args):
    """Format a backend warning with arguments."""
    template = t(key)
    try:
        return template.format(*args)
    except (IndexError, KeyError):
        return template

TRANSLATIONS.update({
    "calc.col_salt": {"de": "Salz", "en": "Salt"},
    "calc.col_g_total": {"de": "g ges.", "en": "g total"},
    "calc.col_g_tank": {"de": "g/Tank", "en": "g/Tank"},
    "calc.salts_exceed": {"de": "Salz(e) überschritten!", "en": "salt(s) exceeded!"},
})

TRANSLATIONS.update({
    "compare.not_found": {"de": "⚠️ Rezept nicht gefunden", "en": "⚠️ Recipe not found"},
    "compare.ratio": {"de": "Verhältnis", "en": "Ratio"},
    "compare.ec_est": {"de": "EC (geschätzt)", "en": "EC (estimated)"},
    "compare.ec_target": {"de": "EC-Ziel", "en": "EC target"},
    "compare.ph_range_label": {"de": "pH-Bereich", "en": "pH range"},
    "compare.plants": {"de": "Pflanzen", "en": "Plants"},
    "growth.culture_label": {"de": "Kultur", "en": "Crop"},
    "growth.base_label": {"de": "Basis", "en": "Base"},
    "growth.source_label": {"de": "Quelle", "en": "Source"},
    "growth.modifiers": {"de": "Modifikatoren", "en": "Modifiers"},
    "growth.phase_label": {"de": "Phase", "en": "Phase"},
    "growth.week_header": {"de": "Woche", "en": "Week"},
})

TRANSLATIONS.update({
    "growth.weeks": {"de": "Wochen", "en": "weeks"},
    "growth.phases": {"de": "Phasen", "en": "phases"},
})

# ═══════════════════════════════════════════════════════════════
# Salt Names (DE → EN)
# ═══════════════════════════════════════════════════════════════
SALT_NAMES = {
    "Calciumnitrat-Tetrahydrat": {"en": "Calcium Nitrate Tetrahydrate"},
    "Calciumnitrat (wasserfrei)": {"en": "Calcium Nitrate (anhydrous)"},
    "Kaliumnitrat": {"en": "Potassium Nitrate"},
    "Ammoniumnitrat": {"en": "Ammonium Nitrate"},
    "Magnesiumnitrat-Hexahydrat": {"en": "Magnesium Nitrate Hexahydrate"},
    "Harnstoff": {"en": "Urea"},
    "Ammoniumsulfat": {"en": "Ammonium Sulfate"},
    "Kaliumdihydrogenphosphat": {"en": "Potassium Dihydrogen Phosphate"},
    "Monoammoniumphosphat (MAP)": {"en": "Monoammonium Phosphate (MAP)"},
    "Diammoniumphosphat (DAP)": {"en": "Diammonium Phosphate (DAP)"},
    "Phosphorsäure (85%)": {"en": "Phosphoric Acid (85%)"},
    "Dikaliumhydrogenphosphat": {"en": "Dipotassium Hydrogen Phosphate"},
    "Kaliumsulfat": {"en": "Potassium Sulfate"},
    "Kaliumchlorid": {"en": "Potassium Chloride"},
    "Kaliumcarbonat (Pottasche)": {"en": "Potassium Carbonate (Potash)"},
    "Kaliumhydroxid": {"en": "Potassium Hydroxide"},
    "Calciumchlorid-Dihydrat": {"en": "Calcium Chloride Dihydrate"},
    "Calciumsulfat-Dihydrat (Gips)": {"en": "Calcium Sulfate Dihydrate (Gypsum)"},
    "Magnesiumsulfat-Heptahydrat": {"en": "Magnesium Sulfate Heptahydrate"},
    "Magnesiumsulfat (wasserfrei)": {"en": "Magnesium Sulfate (anhydrous)"},
    "Magnesiumchlorid-Hexahydrat": {"en": "Magnesium Chloride Hexahydrate"},
    "Schwefelsäure (konz.)": {"en": "Sulfuric Acid (conc.)"},
    "Salpetersäure (65%)": {"en": "Nitric Acid (65%)"},
    "Eisen-DTPA (11% Fe)": {"en": "Iron-DTPA (11% Fe)"},
    "Eisen-EDDHA (6% Fe)": {"en": "Iron-EDDHA (6% Fe)"},
    "Eisen-EDTA (13% Fe)": {"en": "Iron-EDTA (13% Fe)"},
    "Eisen-HBED (9% Fe)": {"en": "Iron-HBED (9% Fe)"},
    "Mangansulfat-Monohydrat": {"en": "Manganese Sulfate Monohydrate"},
    "Mangan-EDTA (13% Mn)": {"en": "Manganese-EDTA (13% Mn)"},
    "Zinksulfat-Heptahydrat": {"en": "Zinc Sulfate Heptahydrate"},
    "Zink-EDTA (15% Zn)": {"en": "Zinc-EDTA (15% Zn)"},
    "Kupfersulfat-Pentahydrat": {"en": "Copper Sulfate Pentahydrate"},
    "Kupfer-EDTA (15% Cu)": {"en": "Copper-EDTA (15% Cu)"},
    "Borsäure": {"en": "Boric Acid"},
    "Borax (Natriumborat)": {"en": "Borax (Sodium Borate)"},
    "Natriummolybdat-Dihydrat": {"en": "Sodium Molybdate Dihydrate"},
    "Ammoniummolybdat": {"en": "Ammonium Molybdate"},
    "Ferty 10S (Planta)": {"en": "Ferty 10S (Planta)"},
    "Rexolin ABC (Yara/Kemira)": {"en": "Rexolin ABC (Yara/Kemira)"},
    "Tenso Cocktail (ICL/Everris)": {"en": "Tenso Cocktail (ICL/Everris)"},
    "Fetrilon Combi (BASF)": {"en": "Fetrilon Combi (BASF)"},
    "Librel BMX (BASF)": {"en": "Librel BMX (BASF)"},
}

SALT_NOTES = {
    "Wird mikrobiell zu NH₄⁺ umgewandelt, nicht sofort pflanzenverfügbar":
        {"en": "Microbially converted to NH₄⁺, not immediately plant-available"},
    "Liefert NH₄ + P gleichzeitig":
        {"en": "Delivers NH₄ + P simultaneously"},
    "Liefert 2× NH₄ + P, pH-hebend":
        {"en": "Delivers 2× NH₄ + P, raises pH"},
    "Reine P-Quelle, pH-senkend":
        {"en": "Pure P source, lowers pH"},
    "Liefert 2× K + P, pH-hebend":
        {"en": "Delivers 2× K + P, raises pH"},
    "pH-hebend, CO₃ reagiert mit Säure":
        {"en": "Raises pH, CO₃ reacts with acid"},
    "Stark basisch, pH-Korrektur":
        {"en": "Strongly basic, pH correction"},
    "Sehr schlecht löslich – nur für geringe Mengen":
        {"en": "Very poorly soluble – only for small amounts"},
    "pH-Korrektur, Vorsicht: stark ätzend!":
        {"en": "pH correction, caution: highly corrosive!"},
    "pH-Korrektur + NO₃-Quelle":
        {"en": "pH correction + NO₃ source"},
    "Stabil pH 3–6.5": {"en": "Stable pH 3–6.5"},
    "Stabil pH 3–9, teurer": {"en": "Stable pH 3–9, more expensive"},
    "Stabil pH 3–6.0, günstig": {"en": "Stable pH 3–6.0, affordable"},
    "Stabil pH 3–8, neueres Chelat": {"en": "Stable pH 3–8, newer chelate"},
    "Alternative zu Borsäure, pH-hebend":
        {"en": "Alternative to boric acid, raises pH"},
    "Weit verbreiteter Mikronährstoff-Mix für Hydrokultur":
        {"en": "Widely used micronutrient mix for hydroponics"},
    "Chelat-basierter Mikromix, alle Metalle als EDTA-Chelate":
        {"en": "Chelate-based micromix, all metals as EDTA chelates"},
    "Enthält Fe-EDDHA-Anteil → stabiler bei höherem pH":
        {"en": "Contains Fe-EDDHA fraction → more stable at higher pH"},
    "BASF Mikronährstoff-Mix, ähnlich Ferty 10S":
        {"en": "BASF micronutrient mix, similar to Ferty 10S"},
    "Gleichmäßige Verteilung aller Mikros, für Spezialkulturen":
        {"en": "Even distribution of all micros, for specialty crops"},
}

def salt_name(name_de: str) -> str:
    """Translate a salt name. Returns DE name if no translation or language is DE."""
    if _current_language == "de":
        return name_de
    entry = SALT_NAMES.get(name_de)
    return entry["en"] if entry else name_de

def salt_note(note_de: str) -> str:
    """Translate a salt note."""
    if _current_language == "de" or not note_de:
        return note_de
    entry = SALT_NOTES.get(note_de)
    return entry["en"] if entry else note_de

# ═══════════════════════════════════════════════════════════════
# Remaining UI strings
# ═══════════════════════════════════════════════════════════════
TRANSLATIONS.update({
    # Dynamic result/status strings
    "d.recipe_not_found": {"de": "⚠️ Rezept oder Wasserprofil nicht gefunden!", "en": "⚠️ Recipe or water profile not found!"},
    "d.recipe_not_found2": {"de": "⚠️ Rezept oder Wasserprofil nicht gefunden", "en": "⚠️ Recipe or water profile not found"},
    "d.recipe_loaded": {"de": "Vorlage '{}' geladen", "en": "Template '{}' loaded"},
    "d.profile_loaded": {"de": "Profil '{}' geladen", "en": "Profile '{}' loaded"},
    "d.saved": {"de": "✅ '{}' gespeichert!", "en": "✅ '{}' saved!"},
    "d.enter_name": {"de": "⚠️ Bitte Rezeptname eingeben!", "en": "⚠️ Please enter a recipe name!"},
    "d.enter_profile_name": {"de": "⚠️ Bitte Profilname eingeben!", "en": "⚠️ Please enter a profile name!"},
    "d.prices_saved": {"de": "✅ {} Preise gespeichert!", "en": "✅ {} prices saved!"},
    "d.exported": {"de": "✅ Exportiert: {}", "en": "✅ Exported: {}"},
    "d.imported": {"de": "✅ {} Rezepte, {} Profile importiert", "en": "✅ {} recipes, {} profiles imported"},

    # pH calculator result
    "ph.lower": {"de": "pH SENKEN", "en": "LOWER pH"},
    "ph.raise": {"de": "pH HEBEN", "en": "RAISE pH"},
    "ph.need_per_l": {"de": "Bedarf pro Liter:", "en": "Per liter:"},
    "ph.need_total": {"de": "Bedarf gesamt:", "en": "Total needed:"},
    "ph.oh_demand": {"de": "OH⁻-Bedarf:", "en": "OH⁻ demand:"},
    "ph.need_label": {"de": "Bedarf:", "en": "Needed:"},
    "ph.total_label": {"de": "gesamt", "en": "total"},

    # Dilution result
    "dil.dilution_to": {"de": "Verdünnung auf EC", "en": "Dilution to EC"},
    "dil.base_ec": {"de": "Basis-EC (100%):", "en": "Base EC (100%):"},
    "dil.dil_factor": {"de": "Verdünnungsfaktor:", "en": "Dilution factor:"},
    "dil.dosing_per_l": {"de": "Dosierung pro Liter:", "en": "Dosing per liter:"},
    "dil.diluted": {"de": "Verdünnt", "en": "Diluted"},
    "dil.not_found": {"de": "⚠️ Rezept/Wasser nicht gefunden", "en": "⚠️ Recipe/water not found"},
    "dil.select_first": {"de": "⚠️ Erst Stammlösung wählen", "en": "⚠️ Select stock solution first"},

    # Reverse calc
    "rev.no_salts": {"de": "⚠️ Keine Salze eingetragen", "en": "⚠️ No salts entered"},

    # Salt database
    "salts.count": {"de": "({} Salze)", "en": "({} salts)"},
    "salts.filter_all": {"de": "Alle", "en": "All"},
    "salts.filter_macro": {"de": "Makro", "en": "Macro"},
    "salts.filter_micro": {"de": "Mikro", "en": "Micro"},
    "salts.filter_chelate": {"de": "Chelate", "en": "Chelates"},
    "salts.filter_premix": {"de": "Premixe", "en": "Premixes"},
    "salts.note_label": {"de": "Hinweis:", "en": "Note:"},
    "salts.ion_contrib": {"de": "Ionenbeitrag pro mmol Salz:", "en": "Ion contribution per mmol salt:"},

    # Compatibility
    "compat.yes": {"de": "JA", "en": "YES"},
    "compat.no": {"de": "NEIN", "en": "NO"},
    "compat.compatible_label": {"de": "Kompatibel:", "en": "Compatible:"},

    # Cost manager
    "costs.salt_label": {"de": "Salz", "en": "Salt"},
    "costs.g_total": {"de": "g ges.", "en": "g total"},
    "costs.cost_label": {"de": "Kosten", "en": "Cost"},
    "costs.cost_per_l": {"de": "Kosten pro Liter:", "en": "Cost per liter:"},
    "costs.cost_for": {"de": "Kosten für {} L:", "en": "Cost for {} L:"},
    "costs.no_prices_hint": {"de": "⚠️ Keine Preise hinterlegt – bitte links Salzpreise eintragen!",
                             "en": "⚠️ No prices set – please enter salt prices on the left!"},
    "costs.macro_salts": {"de": "Makro-Salze", "en": "Macro Salts"},
    "costs.chelates": {"de": "Chelate", "en": "Chelates"},
    "costs.micro_nutrients": {"de": "Mikronährstoffe", "en": "Micronutrients"},
    "costs.premixes": {"de": "Premixe", "en": "Premixes"},
    "costs.recipe_col": {"de": "Rezept", "en": "Recipe"},

    # Label printer
    "labels.recipe_label": {"de": "Rezept:", "en": "Recipe:"},
    "labels.water_label": {"de": "Wasser:", "en": "Water:"},
    "labels.created_label": {"de": "Erstellt:", "en": "Created:"},
    "labels.salt_col": {"de": "Salz", "en": "Salt"},
    "labels.grams_col": {"de": "Gramm", "en": "Grams"},
    "labels.fill_up": {"de": "Auffüllen auf {} L mit Wasser", "en": "Fill up to {} L with water"},
    "labels.tank_content_b": {"de": "Inhalt: PO₄³⁻, SO₄²⁻, Mikro", "en": "Contents: PO₄³⁻, SO₄²⁻, Micro"},
    "labels.dose_first": {"de": "Erst ins Wasser dosieren!", "en": "Dose into water first!"},
    "labels.stock_solution": {"de": "Stammlösung", "en": "Stock Solution"},
    "labels.pdf_saved": {"de": "✅ PDF gespeichert: {}", "en": "✅ PDF saved: {}"},
    "labels.txt_saved": {"de": "✅ Textdatei gespeichert: {}\n(Für PDF: pip install reportlab)",
                         "en": "✅ Text file saved: {}\n(For PDF: pip install reportlab)"},
    "labels.note_label": {"de": "Hinweis:", "en": "Note:"},

    # Export/Import
    "export.all_label": {"de": "(Alle)", "en": "(All)"},
    "export.all_recipes_file": {"de": "alle_rezepte.json", "en": "all_recipes.json"},
    "export.recipe_result": {"de": "✅ Rezept: {}", "en": "✅ Recipe: {}"},
    "export.recipe_err": {"de": "⚠️ Rezept {}: {}", "en": "⚠️ Recipe {}: {}"},
    "export.profile_result": {"de": "✅ Profil: {}", "en": "✅ Profile: {}"},
    "export.profile_err": {"de": "⚠️ Profil {}: {}", "en": "⚠️ Profile {}: {}"},
    "export.json_label": {"de": "JSON", "en": "JSON"},
    "export.all_files": {"de": "Alle", "en": "All"},

    # Plant guide
    "plants.filter_all": {"de": "Alle", "en": "All"},
    "plants.filter_fruit": {"de": "Fruchtgemüse", "en": "Fruiting Vegetables"},
    "plants.filter_leafy": {"de": "Blattgemüse", "en": "Leafy Greens"},
    "plants.filter_herbs": {"de": "Kräuter", "en": "Herbs"},
    "plants.filter_brassica": {"de": "Kohlgemüse", "en": "Brassicas"},
    "plants.filter_other": {"de": "Sonstiges", "en": "Other"},
    "plants.notes_label": {"de": "Hinweise:", "en": "Notes:"},
    "plants.notes_ph": {"de": "Wichtige Anbautipps...", "en": "Important growing tips..."},

    # Settings rules text
    "settings.rules_text": {
        "de": ("Das Berechnungsverfahren folgt dem\n"
               "8-Schritt Sequential Salt Selection Process:\n\n"
               "1. Eisen zuerst (Fe-Chelat, chemisch inert)\n"
               "2. Nitrat-Quellen (Ca(NO₃)₂ für Ca)\n"
               "3. Stickstoff-Balance (NH₄NO₃/MAP/DAP)\n"
               "4. Phosphor-Quelle (immer Tank B)\n"
               "5. Schwefel-Steuerung (MgSO₄, K₂SO₄)\n"
               "6. Hauptelement-Check (K/NO₃ Rest)\n"
               "7. Mikronährstoffe (alle Tank B)\n"
               "8. Chlorid (optional, CaCl₂/KCl)\n\n"
               "Schlüsselprinzipien:\n"
               "• Chemische Kompatibilität: Ca↔P/SO₄ trennen\n"
               "• Limitierendes-Nährstoff-Prinzip\n"
               "• Mehrnährstoff-Effizienz\n"
               "• Sequenzielle Verfeinerung\n"
               "• Mikronährstoff-Stabilität\n\n"
               "5 Kritische Verhältnisse:\n"
               "• Ca:Mg        3–5:1   (Ca-Mangel verhindern)\n"
               "• K:(Ca+Mg)    0.5:1   (Kationen-Balance)\n"
               "• N:K          1.2:1   (Protein/Kohlenhydrat)\n"
               "• Ca:K         0.8:1   (Ca-Blockade vermeiden)\n"
               "• S:N          0.1:1   (Aminosäure-Synthese)"),
        "en": ("The calculation follows the\n"
               "8-Step Sequential Salt Selection Process:\n\n"
               "1. Iron first (Fe chelate, chemically inert)\n"
               "2. Nitrate sources (Ca(NO₃)₂ for Ca)\n"
               "3. Nitrogen balance (NH₄NO₃/MAP/DAP)\n"
               "4. Phosphorus source (always Tank B)\n"
               "5. Sulfur control (MgSO₄, K₂SO₄)\n"
               "6. Main element check (K/NO₃ remainder)\n"
               "7. Micronutrients (all Tank B)\n"
               "8. Chloride (optional, CaCl₂/KCl)\n\n"
               "Key Principles:\n"
               "• Chemical compatibility: separate Ca↔P/SO₄\n"
               "• Limiting nutrient principle\n"
               "• Multi-nutrient efficiency\n"
               "• Sequential refinement\n"
               "• Micronutrient stability\n\n"
               "5 Critical Ratios:\n"
               "• Ca:Mg        3–5:1   (prevent Ca deficiency)\n"
               "• K:(Ca+Mg)    0.5:1   (cation balance)\n"
               "• N:K          1.2:1   (protein/carbohydrate)\n"
               "• Ca:K         0.8:1   (avoid Ca blockade)\n"
               "• S:N          0.1:1   (amino acid synthesis)"),
    },
    "settings.restart_hint": {"de": " – Neustart für volle Wirkung", "en": " – restart for full effect"},

    # Calculator summary labels
    "calc.summary_labels": {
        "de": ["EC (geschätzt):", "pH-Bereich:", "Löslichkeit:", "Max. Konz.-Faktor:", "Kosten:", "Dosierung A:B:"],
        "en": ["EC (estimated):", "pH range:", "Solubility:", "Max conc. factor:", "Costs:", "Dosing A:B:"],
    },
})

TRANSLATIONS.update({
    # Salt database columns & detail
    "salts.col_name": {"de": "Bezeichnung", "en": "Name"},
    "salts.col_formula": {"de": "Formel", "en": "Formula"},
    "salts.col_molar": {"de": "M (g/mol)", "en": "M (g/mol)"},
    "salts.col_tank": {"de": "Tank", "en": "Tank"},
    "salts.col_sol": {"de": "Lösl. (g/L)", "en": "Sol. (g/L)"},
    "salts.det_formula": {"de": "Formel:", "en": "Formula:"},
    "salts.det_molar": {"de": "Molmasse:", "en": "Molar mass:"},
    "salts.det_sol": {"de": "Löslichkeit:", "en": "Solubility:"},
    "salts.det_fe": {"de": "Fe-Gehalt:", "en": "Fe content:"},
    "salts.mg_per_g_salt": {"de": "mg/g Salz", "en": "mg/g salt"},

    # Cost manager categories
    "costs.cat_chelates": {"de": "Chelate", "en": "Chelates"},
    "costs.cat_premixes": {"de": "Premixe", "en": "Premixes"},
})

# ═══════════════════════════════════════════════════════════════
# Backend: Remaining chemistry modules
# ═══════════════════════════════════════════════════════════════
TRANSLATIONS.update({
    # Concentrate check
    "b.conc_exceeds": {"de": "⛔ {}: {:.1f} g/L im Konzentrat überschreitet {:.0f}% der Löslichkeit ({:.0f} g/L)",
                       "en": "⛔ {}: {:.1f} g/L in concentrate exceeds {:.0f}% of solubility ({:.0f} g/L)"},
    "b.conc_reduce": {"de": "⛔ Löslichkeitsgrenzen überschritten! Konzentratfaktor reduzieren oder Tankvolumen erhöhen.",
                      "en": "⛔ Solubility limits exceeded! Reduce concentrate factor or increase tank volume."},

    # Dilution
    "b.dil_water_ec": {"de": "Wasser-EC: {} mS/cm", "en": "Water EC: {} mS/cm"},
    "b.dil_water_higher": {"de": "Wasser-EC ist bereits höher als Ziel-EC!", "en": "Water EC already exceeds target EC!"},
    "b.dil_effective": {"de": "Effektiver Ziel-EC (abzgl. Wasser): {} mS/cm",
                        "en": "Effective target EC (minus water): {} mS/cm"},
    "b.dil_base_zero": {"de": "Basis-EC = 0 – keine Verdünnung berechenbar",
                        "en": "Base EC = 0 – dilution cannot be calculated"},
    "b.dil_factor": {"de": "Verdünnungsfaktor: {} ({}%)", "en": "Dilution factor: {} ({}%)"},
    "b.dil_dosing": {"de": "Dosierung pro Liter:", "en": "Dosing per liter:"},
    "b.dil_strong": {"de": "Starke Verdünnung (<30%) – Mikronährstoffe könnten limitierend werden",
                     "en": "Strong dilution (<30%) – micronutrients may become limiting"},
    "b.dil_minimal": {"de": "Kaum Verdünnung nötig – volle Konzentration fast erreicht",
                      "en": "Minimal dilution needed – near full concentration"},

    # EC estimator
    "b.ec_very_low": {"de": "🔵 {} mS/cm – sehr niedrig", "en": "🔵 {} mS/cm – very low"},
    "b.ec_low": {"de": "✅ {} mS/cm – niedrig (Salat, Kräuter)", "en": "✅ {} mS/cm – low (lettuce, herbs)"},
    "b.ec_medium": {"de": "✅ {} mS/cm – mittel (die meisten Kulturen)",
                    "en": "✅ {} mS/cm – medium (most crops)"},
    "b.ec_high": {"de": "🟡 {} mS/cm – hoch (Tomate, Paprika)", "en": "🟡 {} mS/cm – high (tomato, pepper)"},
    "b.ec_very_high": {"de": "🔴 {} mS/cm – sehr hoch (Vorsicht!)", "en": "🔴 {} mS/cm – very high (caution!)"},

    # pH correction
    "b.ph_acid_label": {"de": "Säure:", "en": "Acid:"},
    "b.ph_need_ml": {"de": "Bedarf: {:.3f} mL/L = {:.1f} mL für {:.0f} L",
                     "en": "Needed: {:.3f} mL/L = {:.1f} mL for {:.0f} L"},
    "b.ph_hco3_in_water": {"de": "HCO₃⁻ im Wasser: {:.1f} mg/L = {:.2f} mmol/L",
                           "en": "HCO₃⁻ in water: {:.1f} mg/L = {:.2f} mmol/L"},
    "b.ph_no_hco3": {"de": "Kein HCO₃ zu neutralisieren – Wasser ist bereits gut gepuffert",
                     "en": "No HCO₃ to neutralize – water is already well buffered"},
    "b.ph_high_acid": {"de": "Hoher Säurebedarf ({:.1f} mmol/L) – hartes Wasser, ggf. Verschnitt mit Osmose",
                       "en": "High acid demand ({:.1f} mmol/L) – hard water, consider blending with RO"},
    "b.ph_oh_estimate": {"de": "Geschätzter OH⁻-Bedarf: {:.2f} mmol/L",
                         "en": "Estimated OH⁻ demand: {:.2f} mmol/L"},
    "b.ph_need_g": {"de": "Bedarf: {:.4f} g/L = {:.2f} g für {:.0f} L",
                    "en": "Needed: {:.4f} g/L = {:.2f} g for {:.0f} L"},

    # pH acid/base names
    "b.acid.hno3_65": {"de": "Salpetersäure 65%", "en": "Nitric Acid 65%"},
    "b.acid.hno3_38": {"de": "Salpetersäure 38%", "en": "Nitric Acid 38%"},
    "b.acid.h3po4": {"de": "Phosphorsäure 85%", "en": "Phosphoric Acid 85%"},
    "b.acid.h2so4_96": {"de": "Schwefelsäure 96%", "en": "Sulfuric Acid 96%"},
    "b.acid.h2so4_37": {"de": "Schwefelsäure 37%", "en": "Sulfuric Acid 37%"},
    "b.base.koh": {"de": "Kaliumhydroxid (Feststoff)", "en": "Potassium Hydroxide (solid)"},
    "b.base.k2co3": {"de": "Kaliumcarbonat (Pottasche)", "en": "Potassium Carbonate (Potash)"},
    "b.base.naoh": {"de": "Natronlauge (Feststoff)", "en": "Sodium Hydroxide (solid)"},
    "b.base.naoh_note": {"de": "Liefert Na⁺, hebt pH. Na-Überschuss vermeiden!",
                         "en": "Delivers Na⁺, raises pH. Avoid Na excess!"},

    # Compatibility descriptions
    "b.compat.caso4_desc": {"de": "Ca²⁺ + SO₄²⁻ bilden schwerlösliches CaSO₄. In Stammlösung bei hoher Konzentration Ausfällung möglich.",
                            "en": "Ca²⁺ + SO₄²⁻ form poorly soluble CaSO₄. Precipitation possible in stock solution at high concentration."},
    "b.compat.cap_desc": {"de": "Ca²⁺ + Phosphat bilden unlösliches Calciumphosphat. Immer getrennte Tanks!",
                          "en": "Ca²⁺ + phosphate form insoluble calcium phosphate. Always use separate tanks!"},
    "b.compat.fe_desc": {"de": "Fe-Chelate sind stabiler, aber getrennt ist sicherer.",
                         "en": "Fe chelates are more stable, but separate is safer."},
    "b.compat.ion_comp": {"de": "Ionenkonkurrenz", "en": "Ion competition"},
    "b.compat.chelate_desc": {"de": "Chelate und getrennte Tanks empfohlen.",
                              "en": "Chelates and separate tanks recommended."},

    # Water warnings
    "b.water_excess": {"de": "⚠️ {}: Wasser enthält {:.1f} mg/L, Ziel nur {:.1f} mg/L → Überschuss {:.1f} mg/L",
                       "en": "⚠️ {}: Water contains {:.1f} mg/L, target only {:.1f} mg/L → excess {:.1f} mg/L"},
    "b.water_na": {"de": "⚠️ Na im Wasser: {:.1f} mg/L – erhöhte Natriumbelastung",
                   "en": "⚠️ Na in water: {:.1f} mg/L – elevated sodium levels"},
    "b.water_cl": {"de": "⚠️ Cl im Wasser: {:.1f} mg/L – erhöhte Chloridbelastung",
                   "en": "⚠️ Cl in water: {:.1f} mg/L – elevated chloride levels"},
    "b.water_hco3": {"de": "⚠️ HCO₃ im Wasser: {:.1f} mg/L – ggf. pH-Korrektur nötig",
                     "en": "⚠️ HCO₃ in water: {:.1f} mg/L – pH correction may be needed"},

    # Reverse solver
    "b.rev_ec_high": {"de": "⚠️ EC sehr hoch ({:.1f} mS/cm) – Salzstress möglich",
                      "en": "⚠️ EC very high ({:.1f} mS/cm) – salt stress possible"},
    "b.rev_ec_low": {"de": "⚠️ EC sehr niedrig ({:.1f} mS/cm)",
                     "en": "⚠️ EC very low ({:.1f} mS/cm)"},

    # View leftovers
    "calc.no_steps": {"de": "Keine Berechnungsschritte", "en": "No calculation steps"},
    "labels.content_a": {"de": "Inhalt: Ca²⁺, Fe-Chelat", "en": "Contents: Ca²⁺, Fe chelate"},
    "labels.calc_failed": {"de": "⚠️ Berechnung fehlgeschlagen", "en": "⚠️ Calculation failed"},
    "labels.weights": {"de": "Einwaagen:", "en": "Weights:"},
})

TRANSLATIONS.update({
    "b.conc_saturation": {"de": "Sättigung – knapp!", "en": "saturation – close!"},
    "b.compat.ph_precip": {"de": "pH-abhängige Ausfällung", "en": "pH-dependent precipitation"},
})

# Fix CaP description to match actual source
TRANSLATIONS["b.compat.cap_desc"] = {
    "de": "Ca²⁺ + Phosphat bilden unlösliches Calciumphosphat. IMMER in getrennte Tanks!",
    "en": "Ca²⁺ + phosphate form insoluble calcium phosphate. ALWAYS use separate tanks!"
}

# Fix: full compatibility descriptions
TRANSLATIONS["b.compat.fe_full"] = {
    "de": "Fe³⁺ + Phosphat → FePO₄ (unlöslich). Fe-Chelate sind stabiler, aber getrennt ist sicherer.",
    "en": "Fe³⁺ + phosphate → FePO₄ (insoluble). Fe chelates are more stable, but separate is safer."
}
TRANSLATIONS["b.compat.ca_mg"] = {
    "de": "Ca²⁺ und Mg²⁺ konkurrieren an der Wurzel. Getrennte Tanks verbessern die Verfügbarkeit.",
    "en": "Ca²⁺ and Mg²⁺ compete at the root. Separate tanks improve availability."
}
TRANSLATIONS["b.compat.trace_full"] = {
    "de": "Spurenelemente können in Gegenwart von Ca bei höherem pH ausfallen. Chelate und getrennte Tanks empfohlen.",
    "en": "Trace elements may precipitate in presence of Ca at higher pH. Chelates and separate tanks recommended."
}

# ═══════════════════════════════════════════════════════════════
# Additional missing UI translations
# ═══════════════════════════════════════════════════════════════
TRANSLATIONS.update({
    "compat.tab_matrix": {"de": "Matrix", "en": "Matrix"},
    "compat.tab_single": {"de": "Einzelprüfung", "en": "Single Check"},
    "compat.precipitate": {"de": "Ausfällung", "en": "Precipitation"},
    "c.ec_estimated": {"de": "EC (geschätzt)", "en": "EC (estimated)"},
    "labels.stock_solution": {"de": "STAMMLÖSUNG", "en": "STOCK SOLUTION"},
    "dil.for_volume": {"de": "Für", "en": "For"},
})

# ═══════════════════════════════════════════════════════════════
# Final batch: remaining backend + UI strings
# ═══════════════════════════════════════════════════════════════
TRANSLATIONS.update({
    "b.warn_caso4": {"de": "CaSO₄-Ausfällung möglich!", "en": "CaSO₄ precipitation possible!"},
    "b.warn_ca3po4": {"de": "Bei hohem pH Ca₃(PO₄)₂-Ausfällung möglich!", "en": "Ca₃(PO₄)₂ precipitation possible at high pH!"},
    "b.compat_ok": {"de": "Keine bekannten Inkompatibilitäten", "en": "No known incompatibilities"},
    "b.compat_same": {"de": "Gleiches Salz", "en": "Same salt"},
    "b.total": {"de": "Gesamt", "en": "Total"},
    "b.warn_ca_p_precip": {"de": "⚠️ Ca und P gleichzeitig hoch – Ausfällungsgefahr prüfen!",
                           "en": "⚠️ Ca and P both high – check precipitation risk!"},
    "c.error": {"de": "Fehler", "en": "Error"},
    "c.imported": {"de": "Importiert", "en": "Imported"},
    "c.copy": {"de": "Kopie", "en": "Copy"},
    "compat.status": {"de": "Status", "en": "Status"},
    "compat.salt_not_found": {"de": "⚠️ Salz nicht gefunden", "en": "⚠️ Salt not found"},
    "calc.micros_via": {"de": "📦 Mikros via:", "en": "📦 Micros via:"},
})

# ═══════════════════════════════════════════════════════════════
# Data-level translations (recipes, phases, profiles, plants)
# ═══════════════════════════════════════════════════════════════
DATA_TRANSLATIONS = {
    # Recipe descriptions
    "Klassisches Universalrezept (volle Stärke)": {"en": "Classic universal recipe (full strength)"},
    "Halbe Konzentration – für empfindliche Kulturen": {"en": "Half strength – for sensitive crops"},
    "Ausgewogenes Ionenverhältnis nach Steiner (1961)": {"en": "Balanced ion ratio after Steiner (1961)"},
    "Optimiert für Nutrient Film Technique": {"en": "Optimized for Nutrient Film Technique"},
    "Spezialrezept für Tomatenkultur nach Sonneveld": {"en": "Tomato recipe after Sonneveld"},
    "Spezialrezept für Gurkenkultur nach Sonneveld": {"en": "Cucumber recipe after Sonneveld"},
    "Spezialrezept für Paprikakultur nach Sonneveld": {"en": "Pepper recipe after Sonneveld"},
    "Niedrige Konzentration für Blattgemüse": {"en": "Low concentration for leafy greens"},
    "Forschungsrezept, University of Bristol": {"en": "Research recipe, University of Bristol"},

    # Water profile names
    "Osmosewasser": {"en": "RO Water"},
    "Regenwasser": {"en": "Rainwater"},
    "Leitungswasser Dresden (Beispiel)": {"en": "Tap Water Dresden (example)"},
    "Leitungswasser Berlin (Beispiel)": {"en": "Tap Water Berlin (example)"},

    # Growth plan names
    "Tomate – Standard": {"en": "Tomato – Standard"},
    "Paprika – Standard": {"en": "Pepper – Standard"},
    "Gurke – Standard": {"en": "Cucumber – Standard"},
    "Salat – Standard": {"en": "Lettuce – Standard"},
    "Erdbeere – Standard": {"en": "Strawberry – Standard"},

    # Growth phase names
    "Keimling/Jungpflanze": {"en": "Seedling/Young Plant"},
    "Vegetativ": {"en": "Vegetative"},
    "Blüte/Fruchtansatz": {"en": "Flowering/Fruit Set"},
    "Fruchtreife/Ernte": {"en": "Fruit Ripening/Harvest"},
    "Jungpflanze": {"en": "Young Plant"},
    "Generativ": {"en": "Generative"},
    "Ernte": {"en": "Harvest"},
    "Fruchtbildung": {"en": "Fruit Formation"},
    "Dauernte": {"en": "Continuous Harvest"},
    "Keimling": {"en": "Seedling"},
    "Wachstum": {"en": "Growth"},
    "Pflanzung": {"en": "Planting"},
    "Blüte": {"en": "Flowering"},
    "Fruchtreife": {"en": "Fruit Ripening"},
    "Übergang": {"en": "Transition"},

    # Growth phase notes
    "Niedrige EC, viel Licht": {"en": "Low EC, lots of light"},
    "Starkes vegetatives Wachstum": {"en": "Strong vegetative growth"},
    "K steigt, Ca für Blütenendfäule-Prävention": {"en": "K increases, Ca for blossom end rot prevention"},
    "N:K ≈ 1:1.5, maximale Fruchtqualität": {"en": "N:K ≈ 1:1.5, maximum fruit quality"},
    "Gleichmäßiges Wachstum": {"en": "Steady growth"},
    "K-Betonung für Fruchtentwicklung": {"en": "K emphasis for fruit development"},
    "K leicht erhöht für Fruchtqualität": {"en": "K slightly increased for fruit quality"},
    "Sanfter Start, Fe-Chelat besonders wichtig": {"en": "Gentle start, Fe chelate especially important"},
    "K und Ca für Fruchtansatz": {"en": "K and Ca for fruit set"},

    # Growth plan descriptions
    "Klassischer 4-Phasen-Plan für Stabtomaten im Gewächshaus": {
        "en": "Classic 4-phase plan for greenhouse tomatoes"},
    "3-Phasen-Plan für Paprika": {"en": "3-phase plan for peppers"},
    "3-Phasen-Plan für Gewächshausgurken": {"en": "3-phase plan for greenhouse cucumbers"},
    "3-Phasen-Plan für Blattsalat (NFT/DWC)": {"en": "3-phase plan for lettuce (NFT/DWC)"},
    "4-Phasen-Plan für Erdbeeren": {"en": "4-phase plan for strawberries"},

    # Plant guide entries
    "Fruchtgemüse": {"en": "Fruiting Vegetables"},
    "Blattgemüse": {"en": "Leafy Greens"},
    "Kräuter": {"en": "Herbs"},
    "Kohlgemüse": {"en": "Brassicas"},
    "Hoher K-Bedarf in Fruchtphase, Ca wichtig gegen Blütenendfäule": {
        "en": "High K demand in fruiting phase, Ca important against blossom end rot"},
    "Empfindlich gegen hohe EC, gleichmäßige Nährstoffversorgung": {
        "en": "Sensitive to high EC, consistent nutrient supply"},
    "Moderater K-Bedarf, Ca-empfindlich": {"en": "Moderate K demand, Ca sensitive"},
    "Niedrige EC, hoher N-Bedarf, Tipburn bei Ca-Mangel": {
        "en": "Low EC, high N demand, tipburn with Ca deficiency"},
    "Leicht erhöhter K-Bedarf, gute Mg-Versorgung wichtig": {
        "en": "Slightly elevated K demand, good Mg supply important"},
    "Fe-empfindlich (Chlorose), K für Fruchtqualität": {
        "en": "Fe sensitive (chlorosis), K for fruit quality"},
    "Hoher Ca- und S-Bedarf, Bor wichtig": {"en": "High Ca and S demand, boron important"},
    "Verträgt höhere EC als Salat, Fe-Bedarf beachten": {
        "en": "Tolerates higher EC than lettuce, watch Fe demand"},
    # ── Acid/Base names (exact API strings) ──
    "Salpetersäure 65%": {"en": "Nitric Acid 65%"},
    "Salpetersäure 38%": {"en": "Nitric Acid 38%"},
    "Phosphorsäure 85%": {"en": "Phosphoric Acid 85%"},
    "Schwefelsäure 96%": {"en": "Sulfuric Acid 96%"},
    "Schwefelsäure 37%": {"en": "Sulfuric Acid 37%"},
    "Kaliumhydroxid (Feststoff)": {"en": "Potassium Hydroxide (solid)"},
    "Kaliumcarbonat (Pottasche)": {"en": "Potassium Carbonate (Potash)"},
    "Natronlauge (Feststoff)": {"en": "Sodium Hydroxide (solid)"},
    # ── Plant names with emojis ──
    "🍅 Tomate": {"en": "🍅 Tomato"},
    "🥒 Gurke": {"en": "🥒 Cucumber"},
    "🫑 Paprika": {"en": "🫑 Bell Pepper"},
    "🥬 Salat": {"en": "🥬 Lettuce"},
    "🌿 Basilikum": {"en": "🌿 Basil"},
    "🍓 Erdbeere": {"en": "🍓 Strawberry"},
    "🌶️ Chili": {"en": "🌶️ Chili"},
    "🥦 Brokkoli": {"en": "🥦 Broccoli"},
    "🍃 Spinat": {"en": "🍃 Spinach"},
    "🌱 Koriander": {"en": "🌱 Coriander"},
    # ── Plant category names ──
    "Fruchtgemüse": {"en": "Fruiting Vegetables"},
    "Blattgemüse": {"en": "Leafy Greens"},
    "Kohlgemüse": {"en": "Brassicas"},
    "Kräuter": {"en": "Herbs"},
    "Wurzelgemüse": {"en": "Root Vegetables"},
    "Beeren": {"en": "Berries"},
    "Sonstiges": {"en": "Other"},
    # ── Recipe plant tags ──
    "Universell": {"en": "Universal"},
    "Tomate": {"en": "Tomato"},
    "Gurke": {"en": "Cucumber"},
    "Paprika": {"en": "Pepper"},
    "Salat": {"en": "Lettuce"},
    "Spinat": {"en": "Spinach"},
    "Erdbeere": {"en": "Strawberry"},
    # ── Recipe names with German crops ──
    "Sonneveld – Tomate": {"en": "Sonneveld – Tomato"},
    "Sonneveld – Gurke": {"en": "Sonneveld – Cucumber"},
    "Sonneveld – Paprika": {"en": "Sonneveld – Pepper"},
    "Sonneveld – Salat": {"en": "Sonneveld – Lettuce"},
    "Niedrige Konzentration für Blattgemüse": {"en": "Low concentration for leafy greens"},
    # ── Compatibility descriptions (exact German output of t()) ──
    "Ca²⁺ + SO₄²⁻ bilden schwerlösliches CaSO₄. In Stammlösung bei hoher Konzentration Ausfällung möglich.": {
        "en": "Ca²⁺ + SO₄²⁻ form poorly soluble CaSO₄. Precipitation possible in stock solution at high concentration."},
    "Ca²⁺ + Phosphat bilden unlösliches Calciumphosphat. IMMER in getrennte Tanks!": {
        "en": "Ca²⁺ + phosphate form insoluble calcium phosphate. ALWAYS use separate tanks!"},
    "Fe³⁺ + Phosphat → FePO₄ (unlöslich). Fe-Chelate sind stabiler, aber getrennt ist sicherer.": {
        "en": "Fe³⁺ + phosphate → FePO₄ (insoluble). Fe chelates are more stable, but separate is safer."},
    "Ca²⁺ und Mg²⁺ konkurrieren an der Wurzel. Getrennte Tanks verbessern die Verfügbarkeit.": {
        "en": "Ca²⁺ and Mg²⁺ compete at the root. Separate tanks improve availability."},
    "Spurenelemente können in Gegenwart von Ca bei höherem pH ausfallen. Chelate und getrennte Tanks empfohlen.": {
        "en": "Trace elements may precipitate in presence of Ca at higher pH. Chelates and separate tanks recommended."},
    "Keine bekannten Inkompatibilitäten": {"en": "No known incompatibilities"},
    "Gleiches Salz": {"en": "Same salt"},
    "Ionenkonkurrenz": {"en": "Ion competition"},
    "pH-abhängige Ausfällung": {"en": "pH-dependent precipitation"},
    "Chelate und getrennte Tanks empfohlen.": {"en": "Chelates and separate tanks recommended."},
    "Fe-Chelate sind stabiler, aber getrennt ist sicherer.": {
        "en": "Fe chelates are more stable, but separate is safer."},
    # ── Compatibility combined descriptions (with | separator) ──
    "CaSO₄ (Gips)": {"en": "CaSO₄ (Gypsum)"},
    "CaSO₄ (Gips), Ionenkonkurrenz": {"en": "CaSO₄ (Gypsum), Ion competition"},
}

def td(text: str) -> str:
    """Translate data-level string (recipe names, phase names, etc.)."""
    if _current_language == "de" or not text:
        return text
    entry = DATA_TRANSLATIONS.get(text)
    return entry.get("en", text) if entry else text

TRANSLATIONS["growth.ec_target"] = {"de": "EC-Ziel", "en": "EC target"}

# Fix mismatched salt note keys
SALT_NOTES["Wird mikrobiell zu NH₄⁺ umgewandelt, nicht sofort verfügbar"] = {
    "en": "Microbially converted to NH₄⁺, not immediately available"}
SALT_NOTES["Weit verbreiteter Mikronährstoff-Mix für Hydrokultur (Planta Düngemittel)"] = {
    "en": "Widely used micronutrient mix for hydroponics (Planta Düngemittel)"}
SALT_NOTES["Gleichmäßige Verteilung aller Mikros, für Spezialkulturen"] = {
    "en": "Even distribution of all micros, for specialty crops"}

TRANSLATIONS["b.dil_factor_short"] = {"de": "Faktor", "en": "Factor"}

TRANSLATIONS["b.calc_ec"] = {"de": "Errechnete EC", "en": "Calculated EC"}

# ═══════════════════════════════════════════════════════════════
# Salt Editor translations
# ═══════════════════════════════════════════════════════════════
TRANSLATIONS.update({
    "salts.btn_add": {"de": "➕ Neues Salz", "en": "➕ New Salt"},
    "salts.filter_custom": {"de": "⭐ Eigene", "en": "⭐ Custom"},
    "salts.add_title": {"de": "Neues Salz hinzufügen", "en": "Add New Salt"},
    "salts.edit_title": {"de": "Salz bearbeiten", "en": "Edit Salt"},
    "salts.section_basic": {"de": "Grunddaten", "en": "Basic Info"},
    "salts.section_ions": {"de": "Ionenbeitrag (Stöchiometrie)", "en": "Ion Contribution (Stoichiometry)"},
    "salts.field_name": {"de": "Name:", "en": "Name:"},
    "salts.field_formula": {"de": "Summenformel:", "en": "Formula:"},
    "salts.field_molar": {"de": "Molmasse (g/mol):", "en": "Molar mass (g/mol):"},
    "salts.field_sol": {"de": "Löslichkeit (g/L, 20°C):", "en": "Solubility (g/L, 20°C):"},
    "salts.field_category": {"de": "Kategorie:", "en": "Category:"},
    "salts.field_notes": {"de": "Notizen:", "en": "Notes:"},
    "salts.ions_hint": {"de": "Ion auswählen + stöchiometrischen Faktor (pro mol Salz) eingeben",
                        "en": "Select ion + enter stoichiometric factor (per mol salt)"},
    "salts.btn_add_ion": {"de": "➕ Ion hinzufügen", "en": "➕ Add Ion"},
    "salts.btn_save": {"de": "💾 Salz speichern", "en": "💾 Save Salt"},
    "salts.saved": {"de": "✅ Salz gespeichert!", "en": "✅ Salt saved!"},
    "salts.err_required": {"de": "⚠️ Name und Formel erforderlich!", "en": "⚠️ Name and formula required!"},
    "salts.err_numbers": {"de": "⚠️ Molmasse/Löslichkeit müssen Zahlen sein!", "en": "⚠️ Molar mass/solubility must be numbers!"},
    "salts.err_ions": {"de": "⚠️ Mindestens ein Ion erforderlich!", "en": "⚠️ At least one ion required!"},
})
