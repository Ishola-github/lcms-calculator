"""Laboratory calculation helpers (RUO; verify against your SOP)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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


class QCFlag(str, Enum):
    """Suggested interpretation only — not regulatory adjudication."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class RecoveryLimits:
    """Percent recovery bands (inclusive). Review against laboratory SOP."""

    pass_low: float = 70.0
    pass_high: float = 130.0
    warn_low: float = 50.0
    warn_high: float = 150.0

    def validate(self) -> None:
        if not (self.warn_low <= self.pass_low <= self.pass_high <= self.warn_high):
            raise ValueError(
                "Limits must satisfy: warn_low ≤ pass_low ≤ pass_high ≤ warn_high."
            )


@dataclass(frozen=True)
class RPDLimits:
    """Relative percent difference limits (inclusive PASS/WARN upper bounds)."""

    pass_max: float = 20.0
    warn_max: float = 30.0

    def validate(self) -> None:
        if self.pass_max < 0 or self.warn_max < self.pass_max:
            raise ValueError("RPD limits must satisfy: 0 ≤ pass_max ≤ warn_max.")


@dataclass(frozen=True)
class FlaggedValue:
    value: float
    flag: QCFlag
    detail: str


def classify_recovery(recovery_pct: float, limits: RecoveryLimits) -> FlaggedValue:
    """Suggested recovery interpretation (RUO workflow guidance)."""
    limits.validate()
    if limits.pass_low <= recovery_pct <= limits.pass_high:
        flag = QCFlag.PASS
        detail = f"Within PASS band ({limits.pass_low:g}–{limits.pass_high:g}%)."
    elif limits.warn_low <= recovery_pct < limits.pass_low:
        flag = QCFlag.WARN
        detail = f"Below PASS, within WARN low ({limits.warn_low:g}–{limits.pass_low:g}%)."
    elif limits.pass_high < recovery_pct <= limits.warn_high:
        flag = QCFlag.WARN
        detail = f"Above PASS, within WARN high ({limits.pass_high:g}–{limits.warn_high:g}%)."
    else:
        flag = QCFlag.FAIL
        detail = f"Outside WARN bands (<{limits.warn_low:g}% or >{limits.warn_high:g}%)."
    return FlaggedValue(recovery_pct, flag, detail)


def classify_rpd(rpd_pct: float, limits: RPDLimits) -> FlaggedValue:
    """Suggested RPD interpretation (RUO workflow guidance)."""
    limits.validate()
    if rpd_pct <= limits.pass_max:
        flag = QCFlag.PASS
        detail = f"RPD ≤ PASS limit ({limits.pass_max:g}%)."
    elif rpd_pct <= limits.warn_max:
        flag = QCFlag.WARN
        detail = f"RPD between PASS and WARN ({limits.pass_max:g}–{limits.warn_max:g}%)."
    else:
        flag = QCFlag.FAIL
        detail = f"RPD > WARN limit (>{limits.warn_max:g}%)."
    return FlaggedValue(rpd_pct, flag, detail)


@dataclass(frozen=True)
class RecoveryPairResult:
    replicate_1_pct: float
    replicate_2_pct: float
    mean_recovery_pct: float
    rpd_pct: float
    recovery: FlaggedValue
    rpd: FlaggedValue


def evaluate_recovery_pair(
    rep1: float,
    rep2: float,
    nominal: float,
    *,
    values_are_percent_recovery: bool = False,
    recovery_limits: RecoveryLimits | None = None,
    rpd_limits: RPDLimits | None = None,
) -> RecoveryPairResult:
    """
    Compute mean recovery and RPD for duplicate QC, with suggested flags.

    If values_are_percent_recovery is False, rep1/rep2 are measured amounts and
    nominal is the expected amount (same units).
    """
    rec_lim = recovery_limits or RecoveryLimits()
    rpd_lim = rpd_limits or RPDLimits()
    if values_are_percent_recovery:
        r1, r2 = rep1, rep2
    elif nominal != 0:
        r1 = 100.0 * rep1 / nominal
        r2 = 100.0 * rep2 / nominal
    else:
        raise ValueError("Nominal must be > 0 when converting measured values to recovery %.")
    mean_r = (r1 + r2) / 2.0
    rpd = abs(rep1 - rep2) / ((rep1 + rep2) / 2.0) * 100.0 if (rep1 + rep2) else 0.0
    return RecoveryPairResult(
        replicate_1_pct=r1,
        replicate_2_pct=r2,
        mean_recovery_pct=mean_r,
        rpd_pct=rpd,
        recovery=classify_recovery(mean_r, rec_lim),
        rpd=classify_rpd(rpd, rpd_lim),
    )
