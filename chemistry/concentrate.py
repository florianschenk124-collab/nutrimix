"""
Stammlösungs-Berechnung mit Löslichkeitsprüfung.

Berechnet die Konzentrationen in den Konzentrat-Tanks (A/B)
und prüft, ob die Löslichkeitsgrenzen eingehalten werden.
"""

from dataclasses import dataclass, field
from chemistry.solver import SaltResult, SolverResult
from ui.locales import t, warn_fmt, salt_name


@dataclass
class SolubilityCheck:
    """Ergebnis einer Löslichkeitsprüfung für ein Salz."""
    salt_name: str
    formula: str
    tank: str
    g_per_l_concentrate: float   # Konzentration im Tank (g/L)
    solubility_limit: float      # Löslichkeitsgrenze (g/L bei 20°C)
    saturation_pct: float        # Sättigungsgrad in %
    is_ok: bool                  # Unter Grenze?
    warning: str = ""


@dataclass
class ConcentrateResult:
    """Ergebnis der Stammlösungs-Berechnung."""
    tank_a_volume_l: float       # Volumen Tank A
    tank_b_volume_l: float       # Volumen Tank B
    concentrate_factor: float
    checks: list[SolubilityCheck] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def all_ok(self) -> bool:
        return all(c.is_ok for c in self.checks)

    @property
    def critical_checks(self) -> list[SolubilityCheck]:
        return [c for c in self.checks if not c.is_ok]

    @property
    def high_saturation_checks(self) -> list[SolubilityCheck]:
        """Salze mit >70% Sättigung (Warnung, aber noch OK)."""
        return [c for c in self.checks if c.is_ok and c.saturation_pct > 70]


def calculate_concentrate(
    solver_result: SolverResult,
    volume_l: float,
    concentrate_factor: float,
    tank_a_volume_l: float | None = None,
    tank_b_volume_l: float | None = None,
    safety_margin: float = 0.85,
) -> ConcentrateResult:
    """
    Berechnet Stammlösungen und prüft Löslichkeit.

    Args:
        solver_result: Ergebnis des Solvers
        volume_l: Gesamtvolumen der Endlösung
        concentrate_factor: Verdünnungsfaktor (z.B. 100 = 100-fach konzentriert)
        tank_a_volume_l: Volumen Tank A (None = auto aus volume/factor)
        tank_b_volume_l: Volumen Tank B (None = auto aus volume/factor)
        safety_margin: Sicherheitsabstand zur Löslichkeitsgrenze (0.85 = 85%)

    Returns:
        ConcentrateResult mit Löslichkeitsprüfungen.
    """
    # Tankvolumen berechnen
    tank_vol = volume_l / concentrate_factor
    if tank_a_volume_l is None:
        tank_a_volume_l = tank_vol
    if tank_b_volume_l is None:
        tank_b_volume_l = tank_vol

    result = ConcentrateResult(
        tank_a_volume_l=tank_a_volume_l,
        tank_b_volume_l=tank_b_volume_l,
        concentrate_factor=concentrate_factor,
    )

    # Löslichkeit für jedes Salz prüfen
    all_salts = (
        [(sr, tank_a_volume_l) for sr in solver_result.tank_a]
        + [(sr, tank_b_volume_l) for sr in solver_result.tank_b]
    )

    for sr, tank_vol_l in all_salts:
        # g Salz pro Liter Konzentrat
        g_per_l_conc = sr.g_total / tank_vol_l

        limit = sr.salt.solubility_20
        saturation = (g_per_l_conc / limit * 100.0) if limit > 0 else 0.0

        is_ok = g_per_l_conc <= (limit * safety_margin)

        warning = ""
        if not is_ok:
            warning = warn_fmt("b.conc_exceeds", salt_name(sr.salt.name), g_per_l_conc, safety_margin*100, limit)
            result.warnings.append(warning)
        elif saturation > 70:
            warning = (
                f"⚠️ {salt_name(sr.salt.name)}: {saturation:.0f}% {t('b.conc_saturation')} "
                f"({g_per_l_conc:.1f} / {limit:.0f} g/L)"
            )

        check = SolubilityCheck(
            salt_name=sr.salt.name,
            formula=sr.salt.formula,
            tank=sr.tank,
            g_per_l_concentrate=g_per_l_conc,
            solubility_limit=limit,
            saturation_pct=saturation,
            is_ok=is_ok,
            warning=warning,
        )
        result.checks.append(check)

    if not result.all_ok:
        result.warnings.insert(0,
            t("b.conc_reduce")
        )

    return result


def suggest_max_concentrate_factor(
    solver_result: SolverResult,
    volume_l: float,
    safety_margin: float = 0.85,
) -> float:
    """
    Schlägt den maximalen Konzentratfaktor vor, bei dem alle Salze löslich bleiben.

    Returns:
        Maximaler Konzentratfaktor (abgerundet auf ganze Zahl).
    """
    max_factor = float("inf")

    for sr in solver_result.all_salts:
        if sr.g_per_l <= 0:
            continue

        limit = sr.salt.solubility_20 * safety_margin
        # g_per_l_conc = g_per_l * concentrate_factor
        # limit >= g_per_l * factor → factor <= limit / g_per_l
        factor = limit / sr.g_per_l

        if factor < max_factor:
            max_factor = factor

    return min(max_factor, 1000.0)  # Cap bei 1000x
