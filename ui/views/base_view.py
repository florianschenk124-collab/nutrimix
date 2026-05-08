"""
Basis-Klasse für alle Views mit einheitlichem Header und Layout.
"""

import customtkinter as ctk


class BaseView(ctk.CTkFrame):
    """Basis-View mit Titel-Header und scrollbarem Content-Bereich."""

    def __init__(self, parent, title: str, subtitle: str = ""):
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Content-Bereich dehnbar

        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 5))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        if subtitle:
            ctk.CTkLabel(
                header,
                text=subtitle,
                font=ctk.CTkFont(size=12),
                text_color="gray60",
                anchor="w",
            ).grid(row=1, column=0, sticky="w")

        # Trennlinie
        ctk.CTkFrame(self, height=2, fg_color="gray30").grid(
            row=0, column=0, sticky="sew", padx=25
        )

        # ── Content Container ──
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nswe", padx=25, pady=(15, 15))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _create_card(self, parent, title: str = "", padx=0, pady=5) -> ctk.CTkFrame:
        """Erstellt eine abgerundete Karte (Card-Element) für Gruppierungen."""
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=("gray92", "gray17"))
        card.grid_columnconfigure(0, weight=1)

        if title:
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
            ).pack(fill="x", padx=15, pady=(12, 5))

        return card

    def _create_labeled_entry(
        self, parent, label: str, placeholder: str = "", width: int = 200
    ) -> ctk.CTkEntry:
        """Erstellt ein Label + Entry-Feld."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=4)

        ctk.CTkLabel(
            frame, text=label, font=ctk.CTkFont(size=12), anchor="w", width=150
        ).pack(side="left")

        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, width=width)
        entry.pack(side="left", padx=(10, 0))

        return entry

    def _create_labeled_dropdown(
        self, parent, label: str, values: list[str], default: str = ""
    ) -> ctk.CTkOptionMenu:
        """Erstellt ein Label + Dropdown-Menü."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=4)

        ctk.CTkLabel(
            frame, text=label, font=ctk.CTkFont(size=12), anchor="w", width=150
        ).pack(side="left")

        dropdown = ctk.CTkOptionMenu(frame, values=values, width=200)
        if default:
            dropdown.set(default)
        dropdown.pack(side="left", padx=(10, 0))

        return dropdown
