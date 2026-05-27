"""PFAS analyte presets and concentration unit helpers (RUO defaults only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# Mass/volume concentration units supported by the helper (aqueous, ρ ≈ 1 g/mL).
CONC_UNIT_OPTIONS: Final[list[str]] = [
    "ng/L",
    "µg/L (ppb)",
    "ng/mL",
    "µg/mL",
    "mg/L (ppm)",
    "pg/mL",
]

# Each unit expressed as ng per mL (1 ng/mL ≡ 1 µg/L for dilute water).
_TO_NG_PER_ML: Final[dict[str, float]] = {
    "ng/L": 0.001,
    "µg/L (ppb)": 1.0,
    "ng/mL": 1.0,
    "µg/mL": 1000.0,
    "mg/L (ppm)": 1_000_000.0,
    "pg/mL": 0.001,
}


@dataclass(frozen=True)
class AnalytePreset:
    name: str
    cas: str
    typical_spike_ng_ml: float
    typical_stock_ng_ml: float
    notes: str


ANALYTE_PRESETS: Final[list[AnalytePreset]] = [
    AnalytePreset("PFOA", "335-67-1", 10.0, 1000.0, "Perfluorooctanoic acid"),
    AnalytePreset("PFOS", "1763-23-1", 10.0, 1000.0, "Perfluorooctanesulfonic acid"),
    AnalytePreset("PFHxS", "355-46-4", 5.0, 500.0, "Perfluorohexanesulfonic acid"),
    AnalytePreset("PFNA", "375-95-1", 5.0, 500.0, "Perfluorononanoic acid"),
    AnalytePreset("PFDA", "335-76-2", 5.0, 500.0, "Perfluorodecanoic acid"),
    AnalytePreset("PFUnDA", "2058-94-8", 2.0, 200.0, "Perfluoroundecanoic acid"),
    AnalytePreset("PFDoDA", "307-55-1", 2.0, 200.0, "Perfluorododecanoic acid"),
    AnalytePreset("PFBS", "375-73-3", 10.0, 1000.0, "Perfluorobutanesulfonic acid"),
    AnalytePreset("PFHxA", "307-24-4", 10.0, 1000.0, "Perfluorohexanoic acid"),
    AnalytePreset("HFPO-DA (GenX)", "13252-13-6", 10.0, 1000.0, "Hexafluoropropylene oxide dimer acid"),
    AnalytePreset("PFHpA", "375-85-9", 5.0, 500.0, "Perfluoroheptanoic acid"),
    AnalytePreset("PFHpS", "375-92-8", 5.0, 500.0, "Perfluoroheptanesulfonic acid"),
]

PRESET_BY_NAME: Final[dict[str, AnalytePreset]] = {p.name: p for p in ANALYTE_PRESETS}


def convert_concentration(value: float, from_unit: str, to_unit: str) -> float:
    """Convert mass/volume concentration between supported units."""
    if from_unit not in _TO_NG_PER_ML or to_unit not in _TO_NG_PER_ML:
        raise ValueError(f"Unsupported unit; choose from {CONC_UNIT_OPTIONS}")
    ng_per_ml = value * _TO_NG_PER_ML[from_unit]
    return ng_per_ml / _TO_NG_PER_ML[to_unit]


def format_conc(value: float, unit: str, digits: int = 6) -> str:
    return f"{value:.{digits}g} {unit}"
