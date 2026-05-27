"""Laboratory calculation helpers (RUO; verify against your SOP)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SPEResult:
    sample_volume_ml: float
    final_extract_volume_ml: float
    post_extract_dilution: float
    concentration_factor: float
    effective_reporting_divisor: float

    def sample_equivalent_ng_l(self, measured_ng_l_in_final: float) -> float:
        """Convert a reading in final extract/solvent back to original sample ng/L."""
        if self.effective_reporting_divisor <= 0:
            return 0.0
        return measured_ng_l_in_final / self.effective_reporting_divisor


def spe_concentration_factor(
    sample_volume_ml: float,
    final_extract_volume_ml: float,
    post_extract_dilution: float = 1.0,
) -> SPEResult:
    """
    Concentration factor = sample volume / final extract volume.

    post_extract_dilution: additional dilution applied after extraction (1 = none).
    Effective divisor for reporting to sample = CF × post_extract_dilution.
    """
    if sample_volume_ml <= 0 or final_extract_volume_ml <= 0:
        raise ValueError("Sample and final extract volumes must be > 0.")
    if post_extract_dilution <= 0:
        raise ValueError("Post-extract dilution must be > 0.")
    cf = sample_volume_ml / final_extract_volume_ml
    eff = cf * post_extract_dilution
    return SPEResult(
        sample_volume_ml=sample_volume_ml,
        final_extract_volume_ml=final_extract_volume_ml,
        post_extract_dilution=post_extract_dilution,
        concentration_factor=cf,
        effective_reporting_divisor=eff,
    )


@dataclass(frozen=True)
class CalibrationLevel:
    level_id: str
    target_ng_l: float
    stock_volume_ul: float
    diluent_volume_ml: float
    final_volume_ml: float


def calibration_prep_table(
    targets_ng_l: list[float],
    stock_ng_ml: float,
    final_volume_ml: float,
    level_prefix: str = "Std",
) -> list[CalibrationLevel]:
    """
    Prepare standards in aqueous solvent (ρ ≈ 1): target ng/L in final_volume_ml.

    stock_ng_ml: stock standard concentration (ng/mL).
    """
    if stock_ng_ml <= 0 or final_volume_ml <= 0:
        raise ValueError("Stock concentration and final volume must be > 0.")
    rows: list[CalibrationLevel] = []
    for i, target in enumerate(targets_ng_l, start=1):
        if target < 0:
            continue
        amount_ng = target * final_volume_ml / 1000.0
        stock_ml = amount_ng / stock_ng_ml
        stock_ul = stock_ml * 1000.0
        diluent_ml = max(final_volume_ml - stock_ml, 0.0)
        rows.append(
            CalibrationLevel(
                level_id=f"{level_prefix}{i}",
                target_ng_l=target,
                stock_volume_ul=stock_ul,
                diluent_volume_ml=diluent_ml,
                final_volume_ml=final_volume_ml,
            )
        )
    return rows


@dataclass(frozen=True)
class ISSpikeResult:
    sample_volume_ml: float
    stock_ng_ml: float
    target_ng_ml_in_sample: float
    spike_volume_ul: float
    target_ng_l_in_sample: float


def internal_standard_spike(
    sample_volume_ml: float,
    stock_ng_ml: float,
    target_ng_ml_in_sample: float,
) -> ISSpikeResult:
    """Volume (µL) of IS stock to add for target concentration in sample."""
    if sample_volume_ml <= 0 or stock_ng_ml <= 0 or target_ng_ml_in_sample <= 0:
        raise ValueError("Sample volume, stock, and target must be > 0.")
    spike_ul = (target_ng_ml_in_sample * sample_volume_ml * 1000.0) / stock_ng_ml
    return ISSpikeResult(
        sample_volume_ml=sample_volume_ml,
        stock_ng_ml=stock_ng_ml,
        target_ng_ml_in_sample=target_ng_ml_in_sample,
        spike_volume_ul=spike_ul,
        target_ng_l_in_sample=target_ng_ml_in_sample * 1000.0,
    )


def is_spike_with_extraction_note(
    spike: ISSpikeResult,
    spe: SPEResult | None,
) -> str:
    """Short note when IS is spiked pre-extraction and SPE concentrates the extract."""
    base = (
        f"Add **{spike.spike_volume_ul:.2f} µL** IS stock "
        f"({spike.stock_ng_ml:g} ng/mL) to **{spike.sample_volume_ml:g} mL** sample "
        f"→ target **{spike.target_ng_ml_in_sample:g} ng/mL** "
        f"({spike.target_ng_l_in_sample:g} ng/L)."
    )
    if spe is None:
        return base
    expected_in_extract_ng_ml = spike.target_ng_ml_in_sample * spe.concentration_factor
    return (
        f"{base}  \n"
        f"If spiked **before** extraction (CF = {spe.concentration_factor:g}), "
        f"theoretical IS in neat extract ≈ **{expected_in_extract_ng_ml:g} ng/mL** "
        f"(verify against your SOP; recovery not applied)."
    )
