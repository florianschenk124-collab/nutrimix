"""
Prüfung der 5 kritischen physiologischen Nährstoff-Verhältnisse.

1. Ca:Mg      = 3–5:1
2. K:(Ca+Mg)  = 0.5:1
3. N:K        = 1.2:1
4. Ca:K       = 0.8:1
5. S:N        = 0.1:1

Alle Verhältnisse werden in mmol/L berechnet.
"""

from dataclasses import dataclass
from chemistry.ions import ION_BY_SYMBOL, mg_to_mmol
from ui.locales import t


@dataclass
class RatioResult:
    name: str
    description: str
    actual: float
    target_min: float
    target_max: float
    is_ok: bool
    warning: str = ""
    unit: str = ":1"

    @property
    def status_icon(self) -> str:
        if self.is_ok:
            return "✅"
        elif self.actual < self.target_min:
            return "🔻"
        else:
            return "🔺"

    @property
    def target_str(self) -> str:
        return f"{self.target_min}–{self.target_max}{self.unit}"


def _ratio_warning(name: str, value: float, fmt: str, low_key: str, high_key: str,
                   target_min: float, is_low: bool) -> str:
    direction = t("b.too_low") if is_low else t("b.too_high")
    detail = t(low_key) if is_low else t(high_key)
    return f"{name} {direction} ({value:{fmt}}:1) – {detail}"


def check_ratios(ion_mg: dict[str, float]) -> list[RatioResult]:
    results = []

    def _mmol(sym: str) -> float:
        mg = ion_mg.get(sym, 0.0)
        if mg <= 0 or sym not in ION_BY_SYMBOL:
            return 0.0
        return mg_to_mmol(mg, ION_BY_SYMBOL[sym])

    ca = _mmol("Ca")
    mg = _mmol("Mg")
    k = _mmol("K")
    no3 = _mmol("NO3")
    nh4 = _mmol("NH4")
    so4 = _mmol("SO4")
    total_n = no3 + nh4

    # ── 1. Ca:Mg = 3–5:1 ──
    ratio_ca_mg = ca / mg if mg > 0 else float("inf")
    ok = 3.0 <= ratio_ca_mg <= 5.0
    warning = ""
    if not ok:
        warning = _ratio_warning("Ca:Mg", ratio_ca_mg, ".2f",
            "b.ratio_warn.ca_mg_low", "b.ratio_warn.ca_mg_high",
            3.0, ratio_ca_mg < 3.0)
    results.append(RatioResult(
        name="Ca:Mg", description=t("b.ratio_desc.ca_mg"),
        actual=ratio_ca_mg, target_min=3.0, target_max=5.0, is_ok=ok, warning=warning))

    # ── 2. K:(Ca+Mg) = 0.35–0.65:1 ──
    ca_mg_sum = ca + mg
    ratio_k_camg = k / ca_mg_sum if ca_mg_sum > 0 else float("inf")
    ok = 0.35 <= ratio_k_camg <= 0.65
    warning = ""
    if not ok:
        warning = _ratio_warning("K:(Ca+Mg)", ratio_k_camg, ".2f",
            "b.ratio_warn.k_camg_low", "b.ratio_warn.k_camg_high",
            0.35, ratio_k_camg < 0.35)
    results.append(RatioResult(
        name="K:(Ca+Mg)", description=t("b.ratio_desc.k_camg"),
        actual=ratio_k_camg, target_min=0.35, target_max=0.65, is_ok=ok, warning=warning))

    # ── 3. N:K = 0.8–1.6:1 ──
    ratio_n_k = total_n / k if k > 0 else float("inf")
    ok = 0.8 <= ratio_n_k <= 1.6
    warning = ""
    if not ok:
        warning = _ratio_warning("N:K", ratio_n_k, ".2f",
            "b.ratio_warn.n_k_low", "b.ratio_warn.n_k_high",
            0.8, ratio_n_k < 0.8)
    results.append(RatioResult(
        name="N:K", description=t("b.ratio_desc.n_k"),
        actual=ratio_n_k, target_min=0.8, target_max=1.6, is_ok=ok, warning=warning))

    # ── 4. Ca:K = 0.5–1.2:1 ──
    ratio_ca_k = ca / k if k > 0 else float("inf")
    ok = 0.5 <= ratio_ca_k <= 1.2
    warning = ""
    if not ok:
        warning = _ratio_warning("Ca:K", ratio_ca_k, ".2f",
            "b.ratio_warn.ca_k_low", "b.ratio_warn.ca_k_high",
            0.5, ratio_ca_k < 0.5)
    results.append(RatioResult(
        name="Ca:K", description=t("b.ratio_desc.ca_k"),
        actual=ratio_ca_k, target_min=0.5, target_max=1.2, is_ok=ok, warning=warning))

    # ── 5. S:N = 0.05–0.2:1 ──
    ratio_s_n = so4 / total_n if total_n > 0 else float("inf")
    ok = 0.05 <= ratio_s_n <= 0.2
    warning = ""
    if not ok:
        warning = _ratio_warning("S:N", ratio_s_n, ".3f",
            "b.ratio_warn.s_n_low", "b.ratio_warn.s_n_high",
            0.05, ratio_s_n < 0.05)
    results.append(RatioResult(
        name="S:N", description=t("b.ratio_desc.s_n"),
        actual=ratio_s_n, target_min=0.05, target_max=0.2, is_ok=ok, warning=warning))

    return results


def format_ratio_summary(results: list[RatioResult]) -> str:
    lines = [t("b.ratios_header"), ""]
    for r in results:
        lines.append(
            f"  {r.status_icon} {r.name:<12} "
            f"{t('b.actual')}: {r.actual:>6.2f}:1  "
            f"{t('b.target')}: {r.target_str:<12}  "
            f"– {r.description}"
        )
        if r.warning:
            lines.append(f"     └→ {r.warning}")
    return "\n".join(lines)
