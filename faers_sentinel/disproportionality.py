"""Transparent, report-level 2x2 FAERS-style disproportionality statistics.

This module does not download FAERS records, deduplicate cases, adjust for
confounding, or implement the WHO-UMC Bayesian BCPNN posterior. Results are
hypothesis-generating reporting associations, never causal risk estimates.
"""
import math
from typing import Any, Dict


def calculate_signal(a: int, b: int, c: int, d: int, continuity_correction: bool = False) -> Dict[str, Any]:
    """Calculate PRR, ROR, Wald 95% intervals, Yates chi-square and crude IC.

    a = drug and event, b = drug and other event, c = other drug and
    event, d = other drug and other event. Each case must occupy exactly
    one cell; counts must represent a consistent deduplicated analysis set.
    The information component returned is the *unsmoothed* log2(O/E),
    not the posterior Bayesian BCPNN information component.
    """
    counts = (a, b, c, d)
    if any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in counts):
        raise ValueError("a, b, c and d must be non-negative integers")
    if not isinstance(continuity_correction, bool):
        raise ValueError("continuity_correction must be boolean")
    total = sum(counts)
    if total == 0:
        raise ValueError("At least one report is required")

    # Pearson/Yates statistic uses raw observed counts, not pseudocounts.
    margins = (a + b, c + d, a + c, b + d)
    denominator = math.prod(margins)
    chi_square_yates = (
        total * max(0.0, abs(a * d - b * c) - total / 2) ** 2 / denominator
        if denominator else None
    )
    expected = (a + b) * (a + c) / total
    crude_ic = math.log2(a / expected) if a > 0 and expected > 0 else None

    use_correction = continuity_correction and 0 in counts
    aa, bb, cc, dd = (float(x) + (0.5 if use_correction else 0.0) for x in counts)
    prr = ror = prr_interval = ror_interval = None
    if aa + bb > 0 and cc + dd > 0 and cc > 0:
        prr = (aa / (aa + bb)) / (cc / (cc + dd))
    if bb > 0 and cc > 0:
        ror = (aa * dd) / (bb * cc)
    if aa > 0 and bb > 0 and cc > 0 and dd > 0:
        se_log_prr = math.sqrt(1 / aa - 1 / (aa + bb) + 1 / cc - 1 / (cc + dd))
        se_log_ror = math.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / dd)
        prr_interval = [math.exp(math.log(prr) - 1.96 * se_log_prr),
                        math.exp(math.log(prr) + 1.96 * se_log_prr)]
        ror_interval = [math.exp(math.log(ror) - 1.96 * se_log_ror),
                        math.exp(math.log(ror) + 1.96 * se_log_ror)]

    # Descriptive Evans-type screening rule, not a regulatory determination.
    # Do not apply when a zero cell makes the uncorrected PRR undefined.
    signal_flag = bool(
        a >= 3 and all(x > 0 for x in counts)
        and prr is not None and prr >= 2
        and chi_square_yates is not None and chi_square_yates >= 4
    )
    return {
        "counts": {"a": a, "b": b, "c": c, "d": d, "total": total},
        "expected": expected,
        "prr": prr, "prr_ci95": prr_interval,
        "ror": ror, "ror_ci95": ror_interval,
        "chi_square_yates": chi_square_yates,
        "ic_crude_log2_observed_expected": crude_ic,
        "continuity_correction_applied": use_correction,
        "evans_screening_flag": signal_flag,
        "note": "Exploratory disproportionality only; no causality or incidence inference. "
                "Crude IC is not Bayesian BCPNN. Undefined ratios or intervals are null.",
    }
