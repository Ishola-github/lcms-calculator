"""PFAS analyte presets and concentration unit helpers (RUO defaults only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

CONC_UNIT_OPTIONS: Final[list[str]] = [
    "ng/L",
    "µg/L (ppb)",
    "ng/mL",
    "µg/mL",
    "mg/L (ppm)",
    "pg/mL",
]

_TO_NG_PER_ML: Final[dict[str, float]] = {
    "ng/L": 0.001,
    "µg/L (ppb)": 1.0,
    "ng/mL": 1.0,
    "µg/mL": 1000.0,
    "mg/L (ppm)": 1_000_000.0,
    "pg/mL": 0.001,
}

DEFAULT_CAL_LEVELS_NG_L: Final[list[float]] = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]


@dataclass(frozen=True)
class AnalytePreset:
    name: str
    cas: str
    molecular_weight: float
    cal_range_low_ng_l: float
    cal_range_high_ng_l: float
    typical_spike_ng_ml: float
    typical_stock_ng_ml: float
    suggested_is: str
    notes: str


@dataclass(frozen=True)
class ISPreset:
    name: str
    typical_stock_ng_ml: float
    typical_target_ng_ml: float
    notes: str


# Phase 1 core analytes + common extensions (RUO starting points only).
ANALYTE_PRESETS: Final[list[AnalytePreset]] = [
    AnalytePreset(
        "PFOS", "1763-23-1", 500.13, 0.5, 50.0, 10.0, 1000.0,
        "13C4-PFOS (MPFAC-MXA mix)", "Perfluorooctanesulfonic acid",
    ),
    AnalytePreset(
        "PFOA", "335-67-1", 414.07, 0.5, 50.0, 10.0, 1000.0,
        "13C4-PFOA (MPFAC-MXA mix)", "Perfluorooctanoic acid",
    ),
    AnalytePreset(
        "PFHxS", "355-46-4", 400.12, 0.5, 50.0, 5.0, 500.0,
        "13C3-PFHxS (MPFAC-MXA mix)", "Perfluorohexanesulfonic acid",
    ),
    AnalytePreset(
        "PFNA", "375-95-1", 464.08, 0.5, 50.0, 5.0, 500.0,
        "13C9-PFNA (MPFAC-MXA mix)", "Perfluorononanoic acid",
    ),
    AnalytePreset(
        "PFBS", "375-73-3", 300.10, 0.5, 50.0, 10.0, 1000.0,
        "18O2-PFBS (MPFAC-MXA mix)", "Perfluorobutanesulfonic acid",
    ),
    AnalytePreset(
        "HFPO-DA (GenX)", "13252-13-6", 330.05, 0.5, 50.0, 10.0, 1000.0,
        "13C2-HFPO-DA", "Hexafluoropropylene oxide dimer acid",
    ),
    AnalytePreset(
        "PFDA", "335-76-2", 514.08, 0.5, 50.0, 5.0, 500.0,
        "13C2-PFDA", "Perfluorodecanoic acid",
    ),
    AnalytePreset(
        "PFHxA", "307-24-4", 314.05, 0.5, 50.0, 10.0, 1000.0,
        "13C2-PFHxA", "Perfluorohexanoic acid",
    ),
]

IS_PRESETS: Final[list[ISPreset]] = [
    ISPreset(
        "MPFAC-MXA (Wellington-style mix)",
        50.0, 0.04,
        "Typical isotope dilution mix; verify lot-specific concentrations.",
    ),
    ISPreset(
        "Single-compound 13C-labeled IS",
        100.0, 0.05,
        "Per-analyte labeled standard; adjust per SOP.",
    ),
    ISPreset(
        "Extraction surrogate (e.g. 13C-PFOS)",
        1000.0, 0.10,
        "Higher level for SPE/surrogate tracking; not a quantitation IS.",
    ),
]

PRESET_BY_NAME: Final[dict[str, AnalytePreset]] = {p.name: p for p in ANALYTE_PRESETS}
IS_PRESET_BY_NAME: Final[dict[str, ISPreset]] = {p.name: p for p in IS_PRESETS}


def convert_concentration(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit not in _TO_NG_PER_ML or to_unit not in _TO_NG_PER_ML:
        raise ValueError(f"Unsupported unit; choose from {CONC_UNIT_OPTIONS}")
    ng_per_ml = value * _TO_NG_PER_ML[from_unit]
    return ng_per_ml / _TO_NG_PER_ML[to_unit]


def format_conc(value: float, unit: str, digits: int = 6) -> str:
    return f"{value:.{digits}g} {unit}"
