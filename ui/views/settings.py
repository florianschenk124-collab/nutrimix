"""
Einstellungen: Allgemeine App-Konfiguration, Regelwerk, Datenbank-Tools.
Verknüpft mit Daten-Manager für Persistenz.
"""

import customtkinter as ctk
from ui.views.base_view import BaseView
from database.data_manager import load_settings, save_settings
from ui.locales import t


class SettingsView(BaseView):
    def __init__(self, parent):
        super().__init__(
            parent,
            title=t("settings.title"),
            subtitle=t("settings.subtitle"),
        )

        self.settings = load_settings()

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)

        left = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))

        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))

        self._build_general(left)
        self._build_salt_options(left)
        self._build_rules(right)
        self._build_db_tools(right)

    def _build_general(self, parent):
        card = self._create_card(parent, title=t("settings.card_general"))
        card.pack(fill="x", pady=(0, 8))

        self.default_unit = self._create_labeled_dropdown(
            card, label=t("settings.default_unit"),
            values=["mg/L (ppm)", "mmol/L"],
            default=self.settings.get("default_unit", "mg/L (ppm)"),
        )
        self.default_concentrate = self._create_labeled_entry(
            card, label=t("settings.default_conc"), placeholder="100",
        )
        self.default_concentrate.insert(0, str(self.settings.get("default_concentrate_factor", 100)))

        self.default_volume = self._create_labeled_entry(
            card, label=t("settings.default_vol"), placeholder="1000",
        )
        self.default_volume.insert(0, str(self.settings.get("default_volume", 1000)))

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

        # EC-Methode
        card_ec = self._create_card(parent, title=t("settings.card_ec"))
        card_ec.pack(fill="x", pady=(0, 8))

        self.ec_method = self._create_labeled_dropdown(
            card_ec, label=t("settings.ec_method"),
            values=["ionic", "simple"],
            default=self.settings.get("ec_method", "ionic"),
        )

        ctk.CTkLabel(card_ec,
                     text=t("settings.ec_hint"),
                     font=ctk.CTkFont(size=11), text_color="gray50",
                     justify="left").pack(padx=15, pady=(5, 12), anchor="w")

        # Sprache / Language
        card_lang = self._create_card(parent, title=t("settings.card_lang"))
        card_lang.pack(fill="x", pady=(0, 8))

        self.language_dd = self._create_labeled_dropdown(
            card_lang, label=t("settings.language"),
            values=["Deutsch", "English"],
            default="Deutsch" if self.settings.get("language", "de") == "de" else "English",
        )

        ctk.CTkLabel(card_lang,
                     text=t("settings.lang_hint"),
                     font=ctk.CTkFont(size=11), text_color="gray50",
                     justify="left").pack(padx=15, pady=(5, 12), anchor="w")

    def _build_salt_options(self, parent):
        card = self._create_card(parent, title=t("settings.card_salts"))
        card.pack(fill="x", pady=(0, 8))

        self.fe_chelate = self._create_labeled_dropdown(
            card, label=t("calc.fe_chelate"),
            values=["Fe-DTPA", "Fe-EDTA", "Fe-EDDHA", "Fe-HBED"],
            default=self.settings.get("fe_chelate", "Fe-DTPA"),
        )
        self.nh4_source = self._create_labeled_dropdown(
            card, label=t("calc.nh4_source"),
            values=["NH4NO3", "MAP", "DAP"],
            default=self.settings.get("nh4_source", "NH4NO3"),
        )
        self.p_source = self._create_labeled_dropdown(
            card, label=t("calc.p_source"),
            values=["KH2PO4", "MAP", "H3PO4"],
            default=self.settings.get("p_source", "KH2PO4"),
        )

        from chemistry.salts import get_premixes
        premix_names = ["individual"] + [p.formula for p in get_premixes()]
        self.micro_source = self._create_labeled_dropdown(
            card, label=t("settings.micro_nutrients"),
            values=premix_names,
            default=self.settings.get("micro_source", "individual"),
        )

        self.dose_ratio = self._create_labeled_entry(
            card, label=t("c.dose_ratio"), placeholder="1:1",
        )
        dr = self.settings.get("dose_ratio", "1:1")
        if dr:
            self.dose_ratio.insert(0, dr)

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

        # Speichern-Button
        self.status_label = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(padx=15, pady=(0, 5))

        ctk.CTkButton(parent, text=t("settings.btn_save"),
                      font=ctk.CTkFont(size=13, weight="bold"), height=40,
                      command=self._save).pack(fill="x", pady=(0, 8))

    def _build_rules(self, parent):
        card = self._create_card(parent, title=t("settings.card_rules"))
        card.pack(fill="x", pady=(0, 8))

        rules_text = t("settings.rules_text")

        ctk.CTkLabel(card, text=rules_text,
                     font=ctk.CTkFont(size=11), text_color="gray60",
                     justify="left", wraplength=380,
                     ).pack(padx=15, pady=15, anchor="nw")

    def _build_db_tools(self, parent):
        card = self._create_card(parent, title=t("settings.card_db"))
        card.pack(fill="x", pady=(0, 8))

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(btn_frame,
                     text=t("settings.db_hint"),
                     font=ctk.CTkFont(size=11), text_color="gray50",
                     justify="left").pack(anchor="w", pady=(0, 8))

        ctk.CTkButton(btn_frame, text=t("settings.btn_reset"), height=35,
                      font=ctk.CTkFont(size=12), fg_color="transparent",
                      border_width=1, border_color="#c0392b", text_color="#e74c3c",
                      command=self._reset_all).pack(fill="x")

    def _get_float(self, entry, default=0):
        try:
            return float(entry.get().strip())
        except (ValueError, TypeError):
            return default

    def _save(self):
        dr = self.dose_ratio.get().strip() or "1:1"
        lang = "en" if self.language_dd.get() == "English" else "de"
        self.settings = {
            "default_unit": self.default_unit.get(),
            "default_concentrate_factor": self._get_float(self.default_concentrate, 100),
            "default_volume": self._get_float(self.default_volume, 1000),
            "ec_method": self.ec_method.get(),
            "fe_chelate": self.fe_chelate.get(),
            "nh4_source": self.nh4_source.get(),
            "p_source": self.p_source.get(),
            "micro_source": self.micro_source.get(),
            "dose_ratio": dr,
            "language": lang,
        }
        save_settings(self.settings)

        # Sprache sofort setzen
        from ui.locales import set_language
        set_language(lang)

        restart_hint = ""
        if lang != ("en" if self.language_dd.get() == "English" else "de"):
            restart_hint = t("settings.restart_hint")
        self.status_label.configure(
            text=f"{t('settings.saved')}{restart_hint}",
            text_color="#4CAF50")

    def _reset_all(self):
        import os, shutil
        from database.data_manager import _get_data_dir
        data_dir = _get_data_dir()
        for f in data_dir.iterdir():
            if f.suffix == ".json":
                f.unlink()
        self.status_label.configure(text=t("settings.reset_done"),
                                    text_color="#e8a838")
