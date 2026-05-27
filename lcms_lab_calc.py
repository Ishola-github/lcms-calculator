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


# Common salt molar masses (g/mol) for bench prep estimates.
SALT_MW: dict[str, float] = {
    "Ammonium acetate": 77.08,
    "Ammonium formate": 63.06,
}

# Approximate solvent densities (g/mL) for mass-from-volume estimates.
SOLVENT_DENSITY: dict[str, float] = {
    "Water": 1.0,
    "Methanol (MeOH)": 0.79,
    "Acetonitrile (ACN)": 0.79,
}


@dataclass(frozen=True)
class SaltMassResult:
    salt: str
    concentration_mm: float
    volume_ml: float
    mass_g: float
    mass_mg: float


def salt_mass_for_buffer(
    salt_name: str,
    concentration_mm: float,
    volume_ml: float,
) -> SaltMassResult:
    """Mass of ammonium acetate/formate for aqueous buffer (RUO estimate)."""
    if concentration_mm <= 0 or volume_ml <= 0:
        raise ValueError("Concentration and volume must be > 0.")
    mw = SALT_MW.get(salt_name)
    if mw is None:
        raise ValueError(f"Unknown salt; choose from {list(SALT_MW)}.")
    moles = (concentration_mm / 1000.0) * (volume_ml / 1000.0)
    mass_g = moles * mw
    return SaltMassResult(
        salt=salt_name,
        concentration_mm=concentration_mm,
        volume_ml=volume_ml,
        mass_g=mass_g,
        mass_mg=mass_g * 1000.0,
    )


def ppm_to_mg_per_l(ppm: float) -> float:
    """Aqueous approximation: ppm ≈ mg/L."""
    return ppm


def organic_aqueous_volumes(
    total_ml: float,
    organic_percent: float,
) -> tuple[float, float]:
    if total_ml <= 0:
        raise ValueError("Total volume must be > 0.")
    if not 0 <= organic_percent <= 100:
        raise ValueError("Organic percent must be 0–100.")
    organic_ml = total_ml * organic_percent / 100.0
    aqueous_ml = total_ml - organic_ml
    return organic_ml, aqueous_ml


@dataclass(frozen=True)
class MobilePhaseRecipe:
    title: str
    steps: tuple[str, ...]

    def as_text(self) -> str:
        lines = [f"# {self.title}", ""]
        for i, step in enumerate(self.steps, start=1):
            lines.append(f"{i}. {step}")
        return "\n".join(lines)


def recipe_meoh_water_with_buffer(
    total_ml: float,
    organic_percent: float,
    organic_solvent: str,
    buffer_mm: float,
    buffer_salt: str,
    buffer_in_aqueous_only: bool = True,
    additive_note: str = "",
) -> MobilePhaseRecipe:
    """Build prep steps for organic/aqueous mobile phase with optional aqueous buffer."""
    org_ml, aq_ml = organic_aqueous_volumes(total_ml, organic_percent)
    aq_pct = 100.0 - organic_percent
    steps: list[str] = []
    if buffer_mm > 0 and buffer_salt in SALT_MW:
        buf_vol = aq_ml if buffer_in_aqueous_only else total_ml
        salt = salt_mass_for_buffer(buffer_salt, buffer_mm, buf_vol)
        steps.append(
            f"Weigh **{salt.mass_g:.4f} g** ({salt.mass_mg:.2f} mg) {buffer_salt} "
            f"into a {buf_vol:.1f} mL volumetric (target **{buffer_mm:g} mM** aqueous)."
        )
        steps.append(f"Dissolve and bring aqueous portion to volume with water (~{buf_vol:.1f} mL).")
    steps.append(f"Measure **{org_ml:.2f} mL** {organic_solvent} ({organic_percent:g}% of {total_ml:g} mL).")
    steps.append(f"Measure **{aq_ml:.2f} mL** aqueous portion ({aq_pct:g}% of total).")
    steps.append(f"Combine to **{total_ml:g} mL** final; mix thoroughly and degas per SOP.")
    if additive_note.strip():
        steps.append(additive_note.strip())
    steps.append("Verify against your method SOP before use (RUO workflow guidance).")
    title = f"{organic_percent:g}:{aq_pct:g} {organic_solvent}/aqueous"
    if buffer_mm > 0:
        title += f" + {buffer_mm:g} mM {buffer_salt}"
    return MobilePhaseRecipe(title=title, steps=tuple(steps))


@dataclass(frozen=True)
class SequenceRow:
    position: int
    vial: str
    sample_type: str
    role: str
    notes: str


@dataclass(frozen=True)
class BatchPlannerInput:
    """Inputs for batch sequence templates (planning aid only)."""

    batch_id: str
    cal_levels: int = 6
    sample_count: int = 10
    sample_prefix: str = "S"
    include_initial_blank: bool = True
    include_end_blank: bool = True
    include_calibration: bool = True
    include_lcs: bool = True
    include_llopr: bool = False
    include_opr: bool = False
    msspd_every_n_samples: int = 0
    msspd_pairs_at_end: int = 1
    include_ccv_mid: bool = True
    include_ccv_end: bool = True
    continuing_blank_every: int = 0


def _sample_labels(prefix: str, count: int) -> list[str]:
    return [f"{prefix}-{i:03d}" for i in range(1, count + 1)]


def _append_row(
    rows: list[SequenceRow],
    vial: str,
    sample_type: str,
    role: str,
    notes: str = "",
) -> None:
    rows.append(
        SequenceRow(
            position=len(rows) + 1,
            vial=vial,
            sample_type=sample_type,
            role=role,
            notes=notes,
        )
    )


def _maybe_continuing_blank(
    rows: list[SequenceRow],
    every: int,
    batch_id: str,
) -> None:
    if every <= 0:
        return
    if len(rows) > 0 and len(rows) % every == 0:
        _append_row(
            rows,
            f"{batch_id}-CB-{len(rows) + 1:02d}",
            "Continuing blank",
            "QC",
            "Suggested continuing blank interval — confirm per SOP.",
        )


def generate_training_minimal_sequence(cfg: BatchPlannerInput) -> list[SequenceRow]:
    """Short bracketed sequence for training demos."""
    rows: list[SequenceRow] = []
    bid = cfg.batch_id
    if cfg.include_initial_blank:
        _append_row(rows, f"{bid}-MB-01", "Method blank", "Blank", "Initial blank")
    if cfg.include_calibration:
        for i in range(1, cfg.cal_levels + 1):
            _append_row(rows, f"{bid}-CAL-{i}", "Calibration", "Cal", f"Level {i}")
    if cfg.include_lcs:
        _append_row(rows, f"{bid}-LCS", "LCS", "QC", "Laboratory control sample")
    for lab in _sample_labels(cfg.sample_prefix, cfg.sample_count):
        _append_row(rows, lab, "Sample", "Field", "Editable — assign matrix ID in LIMS")
        _maybe_continuing_blank(rows, cfg.continuing_blank_every, bid)
    if cfg.include_end_blank:
        _append_row(rows, f"{bid}-MB-END", "Method blank", "Blank", "End blank")
    return rows


def generate_1633a_planning_sequence(cfg: BatchPlannerInput) -> list[SequenceRow]:
    """
    1633A-inspired injection outline for planning (RUO template — not compliance automation).
    """
    rows: list[SequenceRow] = []
    bid = cfg.batch_id
    disclaimer = "1633A-style planning template; verify sequence against your SOP/method."

    if cfg.include_initial_blank:
        _append_row(rows, f"{bid}-MB-01", "Method blank", "Blank", "Initial blank · " + disclaimer)
    if cfg.include_calibration:
        for i in range(1, cfg.cal_levels + 1):
            _append_row(rows, f"{bid}-CAL-{i}", "Calibration", "Cal", f"Std level {i}")
    if cfg.include_lcs:
        _append_row(rows, f"{bid}-LCS", "LCS", "QC", "Laboratory control sample")
    if cfg.include_llopr:
        _append_row(rows, f"{bid}-LLOPR", "LLOPR", "QC", "Lower limit check — label per SOP")
    if cfg.include_opr:
        _append_row(rows, f"{bid}-OPR", "OPR", "QC", "Ongoing precision — label per SOP")

    labels = _sample_labels(cfg.sample_prefix, cfg.sample_count)
    mid = max(len(labels) // 2, 1)
    for idx, lab in enumerate(labels, start=1):
        _append_row(rows, lab, "Sample", "Field", "Field / client sample")
        _maybe_continuing_blank(rows, cfg.continuing_blank_every, bid)
        if cfg.msspd_every_n_samples > 0 and idx % cfg.msspd_every_n_samples == 0:
            _append_row(rows, f"{lab}-MS", "Matrix spike", "MS", "Matrix spike (MS)")
            _append_row(rows, f"{lab}-MSD", "Matrix spike duplicate", "MSD", "Matrix spike duplicate (MSD)")
        if cfg.include_ccv_mid and idx == mid:
            _append_row(rows, f"{bid}-CCV-MID", "CCV", "QC", "Mid-run continuing calibration verification")
    for pair in range(1, cfg.msspd_pairs_at_end + 1):
        if cfg.msspd_every_n_samples <= 0:
            _append_row(rows, f"{bid}-MS-{pair:02d}", "Matrix spike", "MS", "End-batch MS pair")
            _append_row(rows, f"{bid}-MSD-{pair:02d}", "Matrix spike duplicate", "MSD", "End-batch MSD pair")
    if cfg.include_ccv_end:
        _append_row(rows, f"{bid}-CCV-END", "CCV", "QC", "End-run CCV")
    if cfg.include_end_blank:
        _append_row(rows, f"{bid}-MB-END", "Method blank", "Blank", "End blank")
    return rows


def generate_batch_sequence(cfg: BatchPlannerInput, template: str) -> list[SequenceRow]:
    if template == "1633A-style planning template (RUO)":
        return generate_1633a_planning_sequence(cfg)
    if template == "Training minimal":
        return generate_training_minimal_sequence(cfg)
    if template == "Custom (use checkboxes below)":
        return generate_1633a_planning_sequence(cfg)
    raise ValueError(f"Unknown template: {template}")


def sequence_to_records(rows: list[SequenceRow]) -> list[dict[str, object]]:
    return [
        {
            "Position": r.position,
            "Vial": r.vial,
            "Type": r.sample_type,
            "Role": r.role,
            "Notes": r.notes,
        }
        for r in rows
    ]
