"""
Solver: Berechnung der Salzmengen aus Ziel-Ionenkonzentrationen.

Implementiert den 8-Schritt Sequential Salt Selection Process ("à la Nico"):

  1. Eisen zuerst       – Fe-Chelat, chemisch inert
  2. Nitrat-Quellen     – Ca(NO₃)₂, KNO₃, Mg(NO₃)₂ sequenziell
  3. Stickstoff-Balance – NH₄NO₃ oder MAP/DAP für NO₃:NH₄-Verhältnis
  4. Phosphor-Quelle    – KH₂PO₄, MAP oder H₃PO₄ → immer Tank B
  5. Schwefel-Steuerung – MgSO₄ → B, K₂SO₄ → B
  6. Hauptelement-Check – Restbedarf Ca, K, Mg prüfen und ausgleichen
  7. Mikronährstoffe    – MnSO₄, ZnSO₄, CuSO₄, H₃BO₃, Na₂MoO₄ → Tank B
  8. Chlorid (optional) – CaCl₂ oder KCl falls im Rezept gefordert

Schlüsselprinzipien:
- Chemische Kompatibilität: Ca (A) und P/SO₄ (B) getrennt
- Limitierendes-Nährstoff-Prinzip: Jedes Salz bis ein Ion das Ziel erreicht
- Mehrnährstoff-Effizienz: Salze bevorzugen, die mehrere Elemente liefern
- Sequenzielle Verfeinerung: Jeder Schritt reduziert die Restlücke
- Mikronährstoff-Stabilität: Spurenelemente weg von Calcium

Alle Berechnungen in mmol/L, Ausgabe in g/L und g/Gesamtvolumen.
"""

from dataclasses import dataclass, field
from ui.locales import t, step, warn_fmt
from chemistry.ions import mg_to_mmol, mmol_to_mg, ION_BY_SYMBOL
from chemistry.salts import (
    Salt, DEFAULT_SALTS,
    CALCIUM_NITRATE, POTASSIUM_NITRATE, POTASSIUM_DIHYDROGEN_PHOSPHATE,
    MAGNESIUM_SULFATE, POTASSIUM_SULFATE, AMMONIUM_NITRATE,
    CALCIUM_CHLORIDE, POTASSIUM_CHLORIDE, MAGNESIUM_NITRATE,
    MAP, DAP, PHOSPHORIC_ACID,
    FE_DTPA, FE_EDTA, FE_EDDHA, FE_HBED,
    MANGANESE_SULFATE, ZINC_SULFATE, COPPER_SULFATE,
    BORIC_ACID, SODIUM_MOLYBDATE,
)

FE_SALTS = {"Fe-DTPA": FE_DTPA, "Fe-EDTA": FE_EDTA, "Fe-EDDHA": FE_EDDHA, "Fe-HBED": FE_HBED}


@dataclass
class SaltResult:
    """Ergebnis für ein einzelnes Salz."""
    salt: Salt
    mmol_per_l: float       # mmol Salz pro Liter Endlösung
    g_per_l: float          # g pro Liter Endlösung
    g_total: float          # g für Gesamtvolumen
    g_concentrate: float    # g für Konzentrat-Tank (Stammlösung)
    tank: str               # "A" oder "B"

    @property
    def cost_total(self) -> float:
        """Gesamtkosten in EUR (0 wenn kein Preis hinterlegt)."""
        return self.g_total * self.salt.cost_per_gram()


@dataclass
class SolverResult:
    """Gesamtergebnis einer Berechnung."""
    tank_a: list[SaltResult] = field(default_factory=list)
    tank_b: list[SaltResult] = field(default_factory=list)
    achieved_mmol: dict[str, float] = field(default_factory=dict)
    achieved_mg: dict[str, float] = field(default_factory=dict)
    delta_mg: dict[str, float] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    # Dosierparameter
    dose_ratio_a: float = 1.0  # Dosierverhältnis A:B (z.B. 1:1 → beide 1.0)
    dose_ratio_b: float = 1.0
    volume_l: float = 1000.0
    concentrate_factor: float = 100.0

    @property
    def all_salts(self) -> list[SaltResult]:
        return self.tank_a + self.tank_b

    @property
    def total_cost(self) -> float:
        """Gesamtkosten aller Salze in EUR."""
        return sum(sr.cost_total for sr in self.all_salts)

    def cost_per_liter(self) -> float:
        """Kosten pro Liter Endlösung in EUR."""
        if self.volume_l > 0:
            return self.total_cost / self.volume_l
        return 0.0


def solve(
    target_mg: dict[str, float],
    volume_l: float = 1000.0,
    concentrate_factor: float = 100.0,
    fe_chelate: str = "Fe-DTPA",
    nh4_source: str = "NH4NO3",
    p_source: str = "KH2PO4",
    cl_target_mg: float = 0.0,
    cl_source: str = "none",
    micro_source: str = "individual",
    dose_ratio: str = "1:1",
) -> SolverResult:
    """
    Hauptberechnung nach dem 8-Schritt-Verfahren (à la Nico).

    Args:
        target_mg: Ziel-Ionenkonzentrationen in mg/L (nach Wasserabzug).
        volume_l: Gesamtvolumen der Endlösung in Liter
        concentrate_factor: Konzentrationsfaktor der Stammlösung
        fe_chelate: Fe-Chelat ("Fe-DTPA", "Fe-EDTA", "Fe-EDDHA")
        nh4_source: NH₄-Quelle ("NH4NO3", "MAP", "DAP")
        p_source: P-Quelle ("KH2PO4", "MAP", "H3PO4")
        cl_target_mg: Cl-Zielkonzentration in mg/L (0 = kein Cl)
        cl_source: Cl-Quelle ("CaCl2", "KCl", "none")
        micro_source: "individual" oder Premix-Formel (z.B. "Ferty10S")
        dose_ratio: Dosierverhältnis A:B als String (z.B. "1:1", "2:3")

    Returns:
        SolverResult mit allen Salzmengen und Bilanzen.
    """
    result = SolverResult()

    # Dosierverhältnis parsen
    try:
        parts = dose_ratio.split(":")
        ratio_a = float(parts[0])
        ratio_b = float(parts[1])
    except (ValueError, IndexError):
        ratio_a, ratio_b = 1.0, 1.0

    result.dose_ratio_a = ratio_a
    result.dose_ratio_b = ratio_b
    result.volume_l = volume_l
    result.concentrate_factor = concentrate_factor

    # ── Zielwerte in mmol/L umrechnen ──
    target_mmol = {}
    for ion_sym, mg_val in target_mg.items():
        if ion_sym in ION_BY_SYMBOL and mg_val > 0:
            target_mmol[ion_sym] = mg_to_mmol(mg_val, ION_BY_SYMBOL[ion_sym])

    # Arbeitskopie: verbleibender Bedarf in mmol/L
    remaining = dict(target_mmol)

    # Konzentrat-Tankvolumen mit Dosierverhältnis
    # Bei 1:1 → gleiche Tankvolumen. Bei 2:3 → A bekommt 2/5, B bekommt 3/5 des Gesamtvolumens
    total_ratio = ratio_a + ratio_b
    tank_vol_a = volume_l / concentrate_factor * (ratio_a / total_ratio) * total_ratio / ratio_a
    tank_vol_b = volume_l / concentrate_factor * (ratio_b / total_ratio) * total_ratio / ratio_b
    # Vereinfacht: Bei gleicher Dosierung pro Einheit Tank brauchen wir gleiche
    # Konzentration, aber unterschiedliche Dosiermengen. Die Tanks haben gleiches
    # Volumen, aber A wird mit ratio_a Teilen und B mit ratio_b Teilen dosiert.
    tank_vol = volume_l / concentrate_factor  # Basis-Tankvolumen

    # Sammlung der berechneten Salze
    salt_results: list[SaltResult] = []

    def _get_remaining(ion: str) -> float:
        """Gibt den Restbedarf eines Ions zurück (min 0)."""
        return max(0.0, remaining.get(ion, 0.0))

    def _use_salt(salt: Salt, primary_ion: str, mmol_needed: float, tank: str,
                  step_desc: str = ""):
        """
        Berechnet und registriert die Verwendung eines Salzes.
        Zieht alle gelieferten Ionen vom Restbedarf ab.
        """
        if mmol_needed <= 1e-6:
            return

        stoich = salt.ion_contribution.get(primary_ion, 0)
        if stoich == 0:
            return

        # mmol Salz pro Liter Endlösung
        mmol_salt = mmol_needed / stoich
        g_per_l = mmol_salt * salt.molar_mass / 1000.0

        sr = SaltResult(
            salt=salt,
            mmol_per_l=mmol_salt,
            g_per_l=g_per_l,
            g_total=g_per_l * volume_l,
            g_concentrate=g_per_l * concentrate_factor,
            tank=tank,
        )
        salt_results.append(sr)

        # Alle gelieferten Ionen vom Restbedarf abziehen
        for ion_sym, stoich_val in salt.ion_contribution.items():
            delivered = mmol_salt * stoich_val
            remaining[ion_sym] = remaining.get(ion_sym, 0.0) - delivered

        if step_desc:
            result.steps.append(step_desc)

    def _use_chelate(salt: Salt, fe_mmol: float, tank: str, step_desc: str = ""):
        """Spezialbehandlung für Fe-Chelate (Berechnung über Fe-Gehalt %)."""
        if fe_mmol <= 1e-6:
            return

        fe_mg = fe_mmol * ION_BY_SYMBOL["Fe"].molar_mass
        g_per_l = fe_mg / (salt.fe_content_pct * 10)
        mmol_salt = g_per_l * 1000.0 / salt.molar_mass

        sr = SaltResult(
            salt=salt,
            mmol_per_l=mmol_salt,
            g_per_l=g_per_l,
            g_total=g_per_l * volume_l,
            g_concentrate=g_per_l * concentrate_factor,
            tank=tank,
        )
        salt_results.append(sr)
        remaining["Fe"] = 0.0

        if step_desc:
            result.steps.append(step_desc)

    # ════════════════════════════════════════════════════════════════════
    # SCHRITT 1: Eisen zuerst
    # Chemisch inert, interagiert nicht mit anderen Nährstoffen.
    # Bei Premix-Auswahl → Fe wird vom Premix in Schritt 7 geliefert.
    # ════════════════════════════════════════════════════════════════════
    use_premix = micro_source != "individual" and DEFAULT_SALTS.get(micro_source, None)
    use_premix = use_premix and DEFAULT_SALTS[micro_source].is_premix if use_premix else False

    fe_need = _get_remaining("Fe")
    if fe_need > 0 and not use_premix:
        fe_salt = FE_SALTS.get(fe_chelate, FE_DTPA)
        _use_chelate(fe_salt, fe_need, "A",
                     step(1, f"{fe_salt.name} → {t('b.for_fe')}"))
    elif fe_need > 0 and use_premix:
        result.steps.append(
            step(1, warn_fmt("b.fe_via_premix", micro_source)))

    # ════════════════════════════════════════════════════════════════════
    # SCHRITT 2: Nitrat-Quellen – Ca(NO₃)₂ für Calcium
    # Liefert Ca²⁺ + NO₃⁻. Ca bestimmt die Menge (limitierendes Ion).
    # ════════════════════════════════════════════════════════════════════
    ca_need = _get_remaining("Ca")
    if ca_need > 0:
        _use_salt(CALCIUM_NITRATE, "Ca", ca_need, "A",
                  step("2a", f"Ca(NO₃)₂·4H₂O → {t('b.ca_demand')} ({ca_need:.2f} mmol/L Ca, {t('b.delivers')} {ca_need * 2:.2f} mmol/L NO₃)"))

    # ════════════════════════════════════════════════════════════════════
    # SCHRITT 3: Stickstoff-Balance – NH₄-Anteil einstellen
    # NH₄NO₃ oder MAP/DAP für das gewünschte NO₃:NH₄-Verhältnis.
    # ════════════════════════════════════════════════════════════════════
    nh4_need = _get_remaining("NH4")
    if nh4_need > 0:
        if nh4_source == "MAP":
            # MAP liefert NH₄ + P gleichzeitig
            p_remaining = _get_remaining("H2PO4")
            # Limitierend: min(NH₄-Bedarf, P-Bedarf) da MAP 1:1 liefert
            use_amount = min(nh4_need, p_remaining) if p_remaining > 0 else 0
            if use_amount > 0:
                _use_salt(MAP, "NH4", use_amount, "B",
                          step(3, f"MAP → NH₄ + P {t('b.simultaneous')} ({use_amount:.2f} mmol/L)"))
            # Restlicher NH₄-Bedarf mit NH₄NO₃
            nh4_still = _get_remaining("NH4")
            if nh4_still > 0:
                _use_salt(AMMONIUM_NITRATE, "NH4", nh4_still, "A",
                          step(3, f"NH₄NO₃ → {t('b.remaining')} NH₄-{t('b.demand')} ({nh4_still:.2f} mmol/L)"))
        elif nh4_source == "DAP":
            # DAP liefert 2× NH₄ + P
            p_remaining = _get_remaining("H2PO4")
            # DAP: 2 NH₄ pro 1 P → limitierend ist min(NH₄/2, P)
            use_by_nh4 = nh4_need / 2.0
            use_by_p = p_remaining if p_remaining > 0 else 0
            use_amount = min(use_by_nh4, use_by_p) if use_by_p > 0 else 0
            if use_amount > 0:
                # use_amount ist mmol DAP → liefert 2*use_amount NH₄
                _use_salt(DAP, "H2PO4", use_amount, "B",
                          step(3, f"DAP → 2×NH₄ + P ({use_amount:.2f} mmol/L)"))
            nh4_still = _get_remaining("NH4")
            if nh4_still > 0:
                _use_salt(AMMONIUM_NITRATE, "NH4", nh4_still, "A",
                          step(3, f"NH₄NO₃ → {t('b.remaining')} NH₄-{t('b.demand')} ({nh4_still:.2f} mmol/L)"))
        else:
            # Standard: NH₄NO₃
            _use_salt(AMMONIUM_NITRATE, "NH4", nh4_need, "A",
                      step(3, f"NH₄NO₃ → NH₄-{t('b.demand')} ({nh4_need:.2f} mmol/L)"))

    # ════════════════════════════════════════════════════════════════════
    # SCHRITT 4: Phosphor-Quelle
    # KH₂PO₄, MAP oder H₃PO₄ → immer Tank B (Ca-P-Trennung!)
    # ════════════════════════════════════════════════════════════════════
    p_need = _get_remaining("H2PO4")
    if p_need > 0:
        if p_source == "MAP" and nh4_source != "MAP":
            # MAP noch nicht verwendet → P + NH₄
            _use_salt(MAP, "H2PO4", p_need, "B",
                      step(4, f"MAP → P-{t('b.demand')} ({p_need:.2f} mmol/L, {t('b.delivers_also')} NH₄)"))
        elif p_source == "H3PO4":
            _use_salt(PHOSPHORIC_ACID, "H2PO4", p_need, "B",
                      step(4, f"H₃PO₄ → {t('b.pure_p')} ({p_need:.2f} mmol/L)"))
        else:
            _use_salt(POTASSIUM_DIHYDROGEN_PHOSPHATE, "H2PO4", p_need, "B",
                      step(4, f"KH₂PO₄ → P-{t('b.demand')} ({p_need:.2f} mmol/L, {t('b.delivers_also')} K)"))

    # ════════════════════════════════════════════════════════════════════
    # SCHRITT 5: Schwefel-Steuerung
    # MgSO₄ für Mg (schließt meist auch S-Bedarf) → Tank B
    # K₂SO₄ für Rest-S falls nötig → Tank B
    # ════════════════════════════════════════════════════════════════════
    mg_need = _get_remaining("Mg")
    so4_need = _get_remaining("SO4")

    if mg_need > 0:
        # MgSO₄ liefert Mg + SO₄ im Verhältnis 1:1
        # Limitierendes Ion bestimmt die Menge
        use_amount = mg_need  # Mg ist primär
        _use_salt(MAGNESIUM_SULFATE, "Mg", use_amount, "B",
                  step("5a", f"MgSO₄·7H₂O → Mg-{t('b.demand')} ({use_amount:.2f} mmol/L, {t('b.delivers_also')} {use_amount:.2f} mmol/L SO₄)"))

    # Restlicher SO₄-Bedarf mit K₂SO₄
    so4_still = _get_remaining("SO4")
    if so4_still > 0:
        _use_salt(POTASSIUM_SULFATE, "SO4", so4_still, "B",
                  step("5b", f"K₂SO₄ → {t('b.rest')}-SO₄ ({so4_still:.2f} mmol/L, {t('b.delivers_also')} {so4_still * 2:.2f} mmol/L K)"))

    # ════════════════════════════════════════════════════════════════════
    # SCHRITT 6: Hauptelement-Check – K und NO₃ ausgleichen
    # KNO₃ liefert gleichzeitig K⁺ und NO₃⁻.
    # ════════════════════════════════════════════════════════════════════
    k_need = _get_remaining("K")
    no3_need = _get_remaining("NO3")

    if k_need > 0 and no3_need > 0:
        # KNO₃ liefert K + NO₃ im Verhältnis 1:1
        # Limitierendes Ion bestimmt die Menge
        use_amount = min(k_need, no3_need)
        _use_salt(POTASSIUM_NITRATE, "K", use_amount, "B",
                  step("6a", f"KNO₃ → K + NO₃ {t('b.simultaneous')} ({use_amount:.2f} mmol/L)"))

    # Wenn noch K fehlt → K₂SO₄ (liefert auch SO₄)
    k_still = _get_remaining("K")
    if k_still > 0:
        _use_salt(POTASSIUM_SULFATE, "K", k_still, "B",
                  step("6b", f"K₂SO₄ → {t('b.rest')}-K ({k_still:.2f} mmol/L K)"))
        result.warnings.append(
            warn_fmt("b.warn_k_rest", mmol_to_mg(k_still, ION_BY_SYMBOL["K"]))
        )

    # Wenn noch NO₃ fehlt → KNO₃ nachschießen
    no3_still = _get_remaining("NO3")
    if no3_still > 0.1:
        _use_salt(POTASSIUM_NITRATE, "NO3", no3_still, "B",
                  step("6c", f"KNO₃ → {t('b.rest')}-NO₃ ({no3_still:.2f} mmol/L, K-{t('b.excess')})"))
        result.warnings.append(
            warn_fmt("b.warn_no3_rest", abs(_get_remaining("K")) * ION_BY_SYMBOL["K"].molar_mass)
        )

    # NO₃-Überschuss prüfen
    no3_balance = remaining.get("NO3", 0.0)
    if no3_balance < -0.5:
        excess_mg = abs(no3_balance) * ION_BY_SYMBOL["NO3"].molar_mass
        result.warnings.append(
            warn_fmt("b.warn_no3_excess", excess_mg))

    # ════════════════════════════════════════════════════════════════════
    # SCHRITT 7: Mikronährstoffe → alle Tank B
    # Entweder als Einzelsalze oder als Premix (z.B. Ferty 10S)
    # ════════════════════════════════════════════════════════════════════

    premix_salt = DEFAULT_SALTS.get(micro_source) if micro_source != "individual" else None

    if premix_salt and premix_salt.is_premix:
        # Premix-Dosierung: Berechne g/L basierend auf dem limitierenden Mikro
        # Jedes Mikro hat einen Bedarf (mg/L) und der Premix liefert mg/g
        mg_per_g = premix_salt.premix_mg_per_g
        micro_targets_mg = {}
        for sym in ["Fe", "Mn", "Zn", "Cu", "B", "Mo"]:
            need_mmol = _get_remaining(sym)
            if need_mmol > 0 and sym in mg_per_g and mg_per_g[sym] > 0:
                need_mg = need_mmol * ION_BY_SYMBOL[sym].molar_mass
                micro_targets_mg[sym] = need_mg

        if micro_targets_mg:
            # Limitierendes Element bestimmt die Dosierung
            g_per_l_needed = {}
            for sym, mg_needed in micro_targets_mg.items():
                g_per_l_needed[sym] = mg_needed / mg_per_g[sym]

            # Minimum nehmen (limitierendes Element)
            limiting_sym = min(g_per_l_needed, key=g_per_l_needed.get)
            g_premix_per_l = g_per_l_needed[limiting_sym]

            sr = SaltResult(
                salt=premix_salt,
                mmol_per_l=0,  # nicht relevant bei Premixen
                g_per_l=g_premix_per_l,
                g_total=g_premix_per_l * volume_l,
                g_concentrate=g_premix_per_l * concentrate_factor,
                tank="B",
            )
            salt_results.append(sr)

            # Gelieferte Mikros vom Restbedarf abziehen
            delivered_info = []
            for sym, mg_content in mg_per_g.items():
                delivered_mg = g_premix_per_l * mg_content
                delivered_mmol = delivered_mg / ION_BY_SYMBOL[sym].molar_mass
                remaining[sym] = remaining.get(sym, 0) - delivered_mmol
                delivered_info.append(f"{sym}: {delivered_mg:.2f} mg/L")

            result.steps.append(
                f"{step(7, premix_salt.name)} → {g_premix_per_l:.4f} g/L "
                f"(limitierend: {limiting_sym}, {', '.join(delivered_info)})"
            )

            # Restliche Mikros die der Premix nicht vollständig abdeckt
            for sym in ["Fe", "Mn", "Zn", "Cu", "B", "Mo"]:
                rest = _get_remaining(sym)
                if rest > 0.0001:
                    # Einzelsalz nachschießen
                    micro_salts = {
                        "Fe": FE_SALTS.get(fe_chelate, FE_DTPA),
                        "Mn": MANGANESE_SULFATE, "Zn": ZINC_SULFATE,
                        "Cu": COPPER_SULFATE, "B": BORIC_ACID, "Mo": SODIUM_MOLYBDATE,
                    }
                    if sym == "Fe":
                        _use_chelate(micro_salts[sym], rest, "A",
                                     f"{step('7+', micro_salts[sym].name)} → {t('b.rest')}-Fe")
                    elif sym in micro_salts:
                        _use_salt(micro_salts[sym], sym, rest, "B",
                                  f"{step('7+', f'{t('b.rest')}-{sym}')} ({rest:.4f} mmol/L)")
    else:
        # Einzelsalze
        mn_need = _get_remaining("Mn")
        if mn_need > 0:
            _use_salt(MANGANESE_SULFATE, "Mn", mn_need, "B",
                      step(7, f"MnSO₄·H₂O → Mn ({mn_need:.4f} mmol/L)"))

        zn_need = _get_remaining("Zn")
        if zn_need > 0:
            _use_salt(ZINC_SULFATE, "Zn", zn_need, "B",
                      step(7, f"ZnSO₄·7H₂O → Zn ({zn_need:.4f} mmol/L)"))

        cu_need = _get_remaining("Cu")
        if cu_need > 0:
            _use_salt(COPPER_SULFATE, "Cu", cu_need, "B",
                      step(7, f"CuSO₄·5H₂O → Cu ({cu_need:.4f} mmol/L)"))

        b_need = _get_remaining("B")
        if b_need > 0:
            _use_salt(BORIC_ACID, "B", b_need, "B",
                      step(7, f"H₃BO₃ → B ({b_need:.4f} mmol/L)"))

        mo_need = _get_remaining("Mo")
        if mo_need > 0:
            _use_salt(SODIUM_MOLYBDATE, "Mo", mo_need, "B",
                      step(7, f"Na₂MoO₄·2H₂O → Mo ({mo_need:.4f} mmol/L)"))

    # ════════════════════════════════════════════════════════════════════
    # SCHRITT 8 (optional): Chlorid
    # CaCl₂ → Tank A, KCl → Tank B. Typisch bei Tomate / Reben.
    # ════════════════════════════════════════════════════════════════════
    if cl_target_mg > 0 and cl_source != "none":
        cl_mmol = mg_to_mmol(cl_target_mg, ION_BY_SYMBOL["Cl"])
        if cl_source == "CaCl2":
            # CaCl₂ liefert 1 Ca + 2 Cl
            _use_salt(CALCIUM_CHLORIDE, "Cl", cl_mmol, "A",
                      step(8, f"CaCl₂·2H₂O → Cl ({cl_mmol:.2f} mmol/L)"))
        elif cl_source == "KCl":
            _use_salt(POTASSIUM_CHLORIDE, "Cl", cl_mmol, "B",
                      step(8, f"KCl → Cl ({cl_mmol:.2f} mmol/L)"))

    # ════════════════════════════════════════════════════════════════════
    # Ergebnisse aufbereiten
    # ════════════════════════════════════════════════════════════════════

    # Gleiche Salze im selben Tank zusammenfassen
    consolidated: dict[tuple[str, str], SaltResult] = {}
    for sr in salt_results:
        key = (sr.salt.formula, sr.tank)
        if key in consolidated:
            existing = consolidated[key]
            consolidated[key] = SaltResult(
                salt=sr.salt,
                mmol_per_l=existing.mmol_per_l + sr.mmol_per_l,
                g_per_l=existing.g_per_l + sr.g_per_l,
                g_total=existing.g_total + sr.g_total,
                g_concentrate=existing.g_concentrate + sr.g_concentrate,
                tank=sr.tank,
            )
        else:
            consolidated[key] = sr

    salt_results = list(consolidated.values())

    # Tank-Zuordnung
    for sr in salt_results:
        if sr.tank == "A":
            result.tank_a.append(sr)
        else:
            result.tank_b.append(sr)

    # Ist-Konzentrationen berechnen
    achieved = {ion: 0.0 for ion in target_mmol}
    for sr in salt_results:
        if sr.salt.is_premix:
            # Premix: g/L × mg/g = mg/L → in mmol/L umrechnen
            for ion_sym, mg_per_g in sr.salt.premix_mg_per_g.items():
                if ion_sym in ION_BY_SYMBOL:
                    delivered_mg = sr.g_per_l * mg_per_g
                    delivered_mmol = delivered_mg / ION_BY_SYMBOL[ion_sym].molar_mass
                    if ion_sym not in achieved:
                        achieved[ion_sym] = 0.0
                    achieved[ion_sym] += delivered_mmol
        else:
            for ion_sym, stoich in sr.salt.ion_contribution.items():
                if ion_sym not in achieved:
                    achieved[ion_sym] = 0.0
                achieved[ion_sym] += sr.mmol_per_l * stoich

    result.achieved_mmol = achieved
    result.achieved_mg = {
        ion_sym: mmol_to_mg(mmol_val, ION_BY_SYMBOL[ion_sym])
        for ion_sym, mmol_val in achieved.items()
        if ion_sym in ION_BY_SYMBOL
    }

    # Differenzen
    result.delta_mg = {
        ion_sym: result.achieved_mg.get(ion_sym, 0) - target_mg.get(ion_sym, 0)
        for ion_sym in target_mg
        if ion_sym in ION_BY_SYMBOL
    }

    return result


def format_result_text(sr: SaltResult) -> str:
    """Formatiert ein SaltResult als lesbare Textzeile."""
    return (
        f"{sr.salt.name:<35} "
        f"{sr.g_per_l:>8.4f} g/L  "
        f"{sr.g_total:>10.2f} {t('calc.col_g_total')}  "
        f"{sr.g_concentrate:>10.2f} g/Tank"
    )
