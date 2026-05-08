#!/usr/bin/env python3
"""
NutrientMixer – Pflanzenernährungs-Rezept-Tool
Einstiegspunkt der Applikation
"""

import customtkinter as ctk
from ui.app import NutrientMixerApp


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    # Sprache aus Settings laden
    from ui.locales import init_language
    init_language()

    # Eigene Salze & Preise laden
    from database.data_manager import register_custom_salts, apply_costs_to_salts
    register_custom_salts()
    apply_costs_to_salts()

    app = NutrientMixerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
