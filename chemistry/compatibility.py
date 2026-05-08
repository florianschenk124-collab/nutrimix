"""
Mischbarkeitsmatrix: Welche Salze dürfen zusammen gelöst werden?

Grundregeln:
1. Ca²⁺ + SO₄²⁻ → CaSO₄ (Gips, schwerlöslich) → NICHT mischen
2. Ca²⁺ + HPO₄²⁻ → Ca₃(PO₄)₂ (unlöslich) → NICHT mischen
3. Ca²⁺ + CO₃²⁻ → CaCO₃ (Kalk) → NICHT mischen
4. Fe³⁺ + PO₄³⁻ → FePO₄ (unlöslich) → NICHT mischen (außer Chelat)
5. Mn²⁺/Zn²⁺/Cu²⁺ bei pH > 6.5 → Hydroxide fallen aus

Über die A/B-Trennung hinaus gibt es weitere Inkompatibilitäten.
"""

from dataclasses import dataclass, field
from chemistry.salts import Salt, DEFAULT_SALTS
from ui.locales import t, warn_fmt, salt_name


# ═══════════════════════════════════════════════════════════════════════
# Inkompatibilitätsregeln
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class IncompatibilityRule:
    """Eine Inkompatibilitätsregel zwischen zwei Ionengruppen."""
    ion_a: set[str]         # Ionen der einen Seite
    ion_b: set[str]         # Ionen der anderen Seite
    severity: str           # "critical", "warning", "info"
    precipitate: str        # Was ausfällt
    description: str        # Erklärung


RULES = [
    IncompatibilityRule(
        ion_a={"Ca"}, ion_b={"SO4"},
        severity="warning",
        precipitate="CaSO₄ (Gips)",
        description=t("b.compat.caso4_desc"),
    ),
    IncompatibilityRule(
        ion_a={"Ca"}, ion_b={"H2PO4"},
        severity="critical",
        precipitate="Ca₃(PO₄)₂",
        description=t("b.compat.cap_desc"),
    ),
    IncompatibilityRule(
        ion_a={"Fe"}, ion_b={"H2PO4"},
        severity="warning",
        precipitate="FePO₄",
        description=t("b.compat.fe_full"),
    ),
    IncompatibilityRule(
        ion_a={"Ca"}, ion_b={"Mg", "SO4"},
        severity="info",
        precipitate=t("b.compat.ion_comp"),
        description=t("b.compat.ca_mg"),
    ),
    IncompatibilityRule(
        ion_a={"Fe", "Mn", "Zn", "Cu"},
        ion_b={"Ca"},
        severity="warning",
        precipitate=t("b.compat.ph_precip"),
        description=t("b.compat.trace_full"),
    ),
]


@dataclass
class CompatibilityCheck:
    """Ergebnis einer Mischbarkeitsprüfung für zwei Salze."""
    salt_a: Salt
    salt_b: Salt
    compatible: bool
    severity: str           # "ok", "info", "warning", "critical"
    reason: str
    precipitate: str = ""


def check_pair(salt_a: Salt, salt_b: Salt) -> CompatibilityCheck:
    """Prüft die Mischbarkeit zweier Salze."""
    ions_a = set(salt_a.ion_contribution.keys())
    ions_b = set(salt_b.ion_contribution.keys())

    if salt_a.is_premix:
        ions_a = set(salt_a.premix_mg_per_g.keys())
    if salt_b.is_premix:
        ions_b = set(salt_b.premix_mg_per_g.keys())

    worst_severity = "ok"
    reasons = []
    precipitates = []

    for rule in RULES:
        # Prüfe ob salt_a Ionen aus rule.ion_a und salt_b aus rule.ion_b hat (oder umgekehrt)
        match_ab = (ions_a & rule.ion_a) and (ions_b & rule.ion_b)
        match_ba = (ions_a & rule.ion_b) and (ions_b & rule.ion_a)

        if match_ab or match_ba:
            severity_order = {"ok": 0, "info": 1, "warning": 2, "critical": 3}
            if severity_order.get(rule.severity, 0) > severity_order.get(worst_severity, 0):
                worst_severity = rule.severity
            reasons.append(rule.description)
            precipitates.append(rule.precipitate)

    compatible = worst_severity in ("ok", "info")
    reason = " | ".join(reasons) if reasons else t("b.compat_ok")
    precipitate = ", ".join(precipitates) if precipitates else ""

    return CompatibilityCheck(
        salt_a=salt_a, salt_b=salt_b,
        compatible=compatible,
        severity=worst_severity,
        reason=reason,
        precipitate=precipitate,
    )


def build_matrix(salts: list[Salt] | None = None) -> list[list[CompatibilityCheck]]:
    """
    Baut eine vollständige Mischbarkeitsmatrix.

    Returns: 2D-Liste [i][j] = CompatibilityCheck für salt_i × salt_j
    """
    if salts is None:
        salts = [s for s in DEFAULT_SALTS.values()
                 if s.category in ("macro", "chelate") and not s.is_premix]

    matrix = []
    for i, sa in enumerate(salts):
        row = []
        for j, sb in enumerate(salts):
            if i == j:
                row.append(CompatibilityCheck(
                    salt_a=sa, salt_b=sb, compatible=True,
                    severity="ok", reason=t("b.compat_same")))
            else:
                row.append(check_pair(sa, sb))
        matrix.append(row)
    return matrix


def get_key_salts() -> list[Salt]:
    """Gibt die wichtigsten Salze für die Matrix zurück (reduzierte Ansicht)."""
    key_formulas = [
        "Ca(NO3)2·4H2O", "KNO3", "NH4NO3", "KH2PO4", "MgSO4·7H2O",
        "K2SO4", "(NH4)2SO4", "CaCl2·2H2O", "NH4H2PO4",
        "Fe-DTPA", "Fe-EDDHA",
    ]
    return [DEFAULT_SALTS[f] for f in key_formulas if f in DEFAULT_SALTS]


SEVERITY_ICONS = {
    "ok": "✅",
    "info": "ℹ️",
    "warning": "⚠️",
    "critical": "⛔",
}
