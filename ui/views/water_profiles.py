"""
Wasserprofile: Verwaltung der Wasseranalysen.
Verknüpft mit Chemistry-Backend und Daten-Manager.
"""

import customtkinter as ctk
from ui.views.base_view import BaseView
from chemistry.water import WaterProfile
from database.data_manager import (
    load_all_water_profiles, save_custom_water_profile, delete_custom_water_profile,
)
from ui.locales import t, warn_fmt


WATER_ION_FIELDS = [
    ("Ca²⁺", "ca"), ("Mg²⁺", "mg"), ("Na⁺", "na"), ("K⁺", "k"),
    ("Cl⁻", "cl"), ("SO₄²⁻ (als S)", "so4"), ("HCO₃⁻", "hco3"),
    ("NO₃⁻ (als N)", "no3"), ("Fe", "fe"),
]


class WaterProfilesView(BaseView):
    def __init__(self, parent):
        super().__init__(
            parent,
            title=t("water.title"),
            subtitle=t("water.subtitle"),
        )

        self.profiles = load_all_water_profiles()
        self.selected_name = None

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Links: Profil-Liste
        left = ctk.CTkFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        card_list = self._create_card(left, title=t("water.card_list"))
        card_list.pack(fill="both", expand=True)

        self.profile_list = ctk.CTkScrollableFrame(card_list, fg_color="transparent")
        self.profile_list.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        btn_frame = ctk.CTkFrame(card_list, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkButton(btn_frame, text=t("water.btn_new"), height=32,
                      font=ctk.CTkFont(size=12),
                      command=self._new_profile).pack(fill="x", pady=(0, 4))
        ctk.CTkButton(btn_frame, text=t("water.btn_delete"), height=32,
                      font=ctk.CTkFont(size=12), fg_color="transparent",
                      border_width=1, border_color="#c0392b", text_color="#e74c3c",
                      command=self._delete_profile).pack(fill="x")

        # Rechts: Profil-Editor
        right = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe", padx=(8, 0))

        card_edit = self._create_card(right, title=t("water.card_edit"))
        card_edit.pack(fill="x")

        self.entry_name = self._create_labeled_entry(
            card_edit, label=t("water.name"), placeholder=t("water.name_ph"))
        self.entry_ec = self._create_labeled_entry(
            card_edit, label=t("water.ec"), placeholder="0.00")
        self.entry_ph = self._create_labeled_entry(
            card_edit, label=t("water.ph"), placeholder="7.0")

        ctk.CTkFrame(card_edit, height=1, fg_color="gray30").pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(card_edit, text=t("water.ions_header"),
                     font=ctk.CTkFont(size=12, weight="bold")).pack(padx=15, anchor="w")

        self.ion_entries = {}
        for label, key in WATER_ION_FIELDS:
            entry = self._create_labeled_entry(card_edit, label=f"{label}:", placeholder="0.0")
            self.ion_entries[key] = entry

        ctk.CTkFrame(card_edit, fg_color="transparent", height=8).pack()

        self.status_label = ctk.CTkLabel(card_edit, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(padx=15, pady=(5, 5))

        ctk.CTkButton(card_edit, text=t("water.btn_save"),
                      font=ctk.CTkFont(size=13, weight="bold"), height=38,
                      command=self._save_profile).pack(fill="x", padx=15, pady=(0, 12))

        self._populate_list()

    def refresh_data(self):
        """Wird aufgerufen wenn die View sichtbar wird."""
        self._populate_list()

    def _populate_list(self):
        for w in self.profile_list.winfo_children():
            w.destroy()

        self.profiles = load_all_water_profiles()

        for name, profile in self.profiles.items():
            item = ctk.CTkFrame(self.profile_list, corner_radius=8,
                                fg_color=("gray85", "gray20"), height=45, cursor="hand2")
            item.pack(fill="x", pady=3)

            ctk.CTkLabel(item, text=name, font=ctk.CTkFont(size=12, weight="bold"),
                         anchor="w").pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(item, text=f"EC: {profile.ec:.2f} mS/cm",
                         font=ctk.CTkFont(size=11), text_color="gray50",
                         ).pack(side="right", padx=12, pady=8)

            # Klick-Event
            item.bind("<Button-1>", lambda e, n=name: self._select_profile(n))
            for child in item.winfo_children():
                child.bind("<Button-1>", lambda e, n=name: self._select_profile(n))

    def _select_profile(self, name):
        self.selected_name = name
        profile = self.profiles.get(name)
        if not profile:
            return

        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, profile.name)
        self.entry_ec.delete(0, "end")
        self.entry_ec.insert(0, str(profile.ec))
        self.entry_ph.delete(0, "end")
        self.entry_ph.insert(0, str(profile.ph))

        vals = {"ca": profile.ca, "mg": profile.mg, "na": profile.na, "k": profile.k,
                "cl": profile.cl, "so4": profile.so4, "hco3": profile.hco3,
                "no3": profile.no3, "fe": profile.fe}

        for key, entry in self.ion_entries.items():
            entry.delete(0, "end")
            entry.insert(0, str(vals.get(key, 0.0)))

        self.status_label.configure(text=warn_fmt("d.profile_loaded", name), text_color="gray50")

    def _new_profile(self):
        self.selected_name = None
        self.entry_name.delete(0, "end")
        self.entry_ec.delete(0, "end")
        self.entry_ph.delete(0, "end")
        for entry in self.ion_entries.values():
            entry.delete(0, "end")
        self.status_label.configure(text=t("water.new_hint"), text_color="gray50")

    def _get_float(self, entry, default=0.0):
        try:
            return float(entry.get().strip())
        except (ValueError, TypeError):
            return default

    def _save_profile(self):
        name = self.entry_name.get().strip()
        if not name:
            self.status_label.configure(text=t("d.enter_profile_name"), text_color="#e8a838")
            return

        profile = WaterProfile(
            name=name,
            ca=self._get_float(self.ion_entries["ca"]),
            mg=self._get_float(self.ion_entries["mg"]),
            na=self._get_float(self.ion_entries["na"]),
            k=self._get_float(self.ion_entries["k"]),
            cl=self._get_float(self.ion_entries["cl"]),
            so4=self._get_float(self.ion_entries["so4"]),
            hco3=self._get_float(self.ion_entries["hco3"]),
            no3=self._get_float(self.ion_entries["no3"]),
            fe=self._get_float(self.ion_entries["fe"]),
            ec=self._get_float(self.entry_ec),
            ph=self._get_float(self.entry_ph, 7.0),
        )

        save_custom_water_profile(profile)
        self.status_label.configure(text=warn_fmt("d.saved", name), text_color="#4CAF50")
        self._populate_list()

    def _delete_profile(self):
        if self.selected_name:
            delete_custom_water_profile(self.selected_name)
            self._new_profile()
            self._populate_list()
            self.status_label.configure(text=t("water.deleted"), text_color="gray50")
