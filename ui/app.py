"""
Hauptfenster der Applikation mit Sidebar-Navigation.
"""

import customtkinter as ctk
from ui.locales import t
from ui.views.recipe_browser import RecipeBrowserView
from ui.views.recipe_editor import RecipeEditorView
from ui.views.calculator import CalculatorView
from ui.views.water_profiles import WaterProfilesView
from ui.views.plant_guide import PlantGuideView
from ui.views.salt_database import SaltDatabaseView
from ui.views.cost_manager import CostManagerView
from ui.views.label_printer import LabelPrinterView
from ui.views.ph_calculator import PhCalculatorView
from ui.views.dilution_calculator import DilutionCalculatorView
from ui.views.reverse_calculator import ReverseCalculatorView
from ui.views.recipe_compare import RecipeCompareView
from ui.views.compatibility_view import CompatibilityView
from ui.views.growth_timeline import GrowthTimelineView
from ui.views.export_import import ExportImportView
from ui.views.settings import SettingsView


class NutrientMixerApp(ctk.CTk):
    """Hauptfenster mit Sidebar und Content-Bereich."""

    APP_NAME = "NutrientMixer"
    APP_VERSION = "0.5.0"
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 800
    SIDEBAR_WIDTH = 220

    # Navigation: (locale_key, icon, ViewClass)
    NAV_ITEMS = [
        ("nav.recipes",         "📋", RecipeBrowserView),
        ("nav.new_recipe",      "➕", RecipeEditorView),
        ("nav.recipe_compare",  "⚖️", RecipeCompareView),
        ("nav.calculator",      "🧮", CalculatorView),
        ("nav.ph_correction",   "🧪", PhCalculatorView),
        ("nav.dilution",        "🔬", DilutionCalculatorView),
        ("nav.reverse",         "🔄", ReverseCalculatorView),
        ("nav.water_profiles",  "💧", WaterProfilesView),
        ("nav.plants",          "🌱", PlantGuideView),
        ("nav.growth_phases",   "📅", GrowthTimelineView),
        ("nav.salt_database",   "🧂", SaltDatabaseView),
        ("nav.compatibility",   "🔬", CompatibilityView),
        ("nav.costs",           "💰", CostManagerView),
        ("nav.labels",          "🏷️", LabelPrinterView),
        ("nav.export_import",   "📦", ExportImportView),
        ("nav.settings",        "⚙️", SettingsView),
    ]

    # Gruppen-Separatoren (nach Index → locale_key)
    NAV_SEPARATORS = {
        3: "nav.group.calculation",
        7: "nav.group.data",
        12: "nav.group.tools",
    }

    def __init__(self):
        super().__init__()

        self.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(900, 600)

        # Grid-Layout: Sidebar links, Content rechts
        self.grid_columnconfigure(0, weight=0)  # Sidebar fest
        self.grid_columnconfigure(1, weight=1)  # Content flexibel
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # Views erstellen und cachen
        self.views: dict[str, ctk.CTkFrame] = {}
        self._init_views()

        # Startansicht
        self._select_nav("nav.calculator")

    # ─── Sidebar ─────────────────────────────────────────────────────

    def _build_sidebar(self):
        """Erstellt die Sidebar mit Logo, Navigation und Appearance-Toggle."""

        self.sidebar = ctk.CTkFrame(self, width=self.SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1)  # Scrollable nav

        # ── Logo / Titel ──
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=15, pady=(15, 3), sticky="ew")

        ctk.CTkLabel(
            logo_frame,
            text="🌿 NutrientMixer",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            logo_frame,
            text=t("app.title"),
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            anchor="w",
        ).pack(fill="x")

        # ── Trennlinie ──
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30")
        separator.grid(row=1, column=0, padx=15, pady=(8, 5), sticky="ew")

        # ── Scrollable Nav ──
        self.nav_scroll = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent", width=self.SIDEBAR_WIDTH - 20,
            scrollbar_button_color="gray30", scrollbar_button_hover_color="gray40")
        self.nav_scroll.grid(row=2, column=0, sticky="nswe", padx=0, pady=0)

        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        for idx, (key, icon, _) in enumerate(self.NAV_ITEMS):
            # Gruppen-Separator
            if idx in self.NAV_SEPARATORS:
                sep_frame = ctk.CTkFrame(self.nav_scroll, fg_color="transparent")
                sep_frame.pack(fill="x", padx=10, pady=(8, 2))
                ctk.CTkLabel(sep_frame, text=t(self.NAV_SEPARATORS[idx]),
                             font=ctk.CTkFont(size=10), text_color="gray45",
                             anchor="w").pack(fill="x")

            btn = ctk.CTkButton(
                self.nav_scroll,
                text=f" {icon}  {t(key)}",
                font=ctk.CTkFont(size=12),
                anchor="w",
                height=32,
                corner_radius=8,
                fg_color="transparent",
                text_color="gray80",
                hover_color=("gray25", "gray25"),
                command=lambda k=key: self._select_nav(k),
            )
            btn.pack(fill="x", padx=8, pady=1)
            self.nav_buttons[key] = btn

        # ── Bottom: Appearance + Version ──
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, padx=15, pady=(5, 10), sticky="sew")

        self.appearance_menu = ctk.CTkSegmentedButton(
            bottom_frame,
            values=["Dark", "Light"],
            command=self._change_appearance,
            font=ctk.CTkFont(size=10),
            height=26,
        )
        self.appearance_menu.set("Dark")
        self.appearance_menu.pack(fill="x", pady=(0, 0))

        ctk.CTkLabel(
            bottom_frame,
            text=f"v{self.APP_VERSION}",
            font=ctk.CTkFont(size=9),
            text_color="gray40",
        ).pack(anchor="w", pady=(4, 0))

    # ─── Content Area ────────────────────────────────────────────────

    def _build_content_area(self):
        """Container für die wechselnden Views."""
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nswe", padx=0, pady=0)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

    # ─── Views ───────────────────────────────────────────────────────

    def _init_views(self):
        """Erstellt alle Views und versteckt sie."""
        for key, _, view_class in self.NAV_ITEMS:
            view = view_class(self.content_area)
            view.grid(row=0, column=0, sticky="nswe")
            view.grid_remove()
            self.views[key] = view

    def _select_nav(self, key: str):
        """Wechselt die aktive View und aktualisiert die Sidebar."""
        for view in self.views.values():
            view.grid_remove()

        self.views[key].grid()

        view = self.views[key]
        if hasattr(view, 'refresh_data'):
            view.refresh_data()

        for name, btn in self.nav_buttons.items():
            if name == key:
                btn.configure(
                    fg_color=("green", "#2a6e3f"),
                    text_color="white",
                    font=ctk.CTkFont(size=12, weight="bold"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="gray80",
                    font=ctk.CTkFont(size=12),
                )

    # ─── Callbacks ───────────────────────────────────────────────────

    def _change_appearance(self, mode: str):
        ctk.set_appearance_mode(mode.lower())
