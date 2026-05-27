#!/usr/bin/env python3
"""Linux/Docker smoke checks for lcms-calculator (no Streamlit server required)."""

from __future__ import annotations

import sys

from lcms_lab_calc import (
    BatchPlannerInput,
    RecoveryLimits,
    classify_recovery,
    evaluate_recovery_pair,
    generate_batch_sequence,
    salt_mass_for_buffer,
    spe_concentration_factor,
)
from lcms_presets import ANALYTE_PRESETS, convert_concentration


def main() -> int:
    assert len(ANALYTE_PRESETS) >= 6
    spe = spe_concentration_factor(250.0, 1.0)
    assert spe.concentration_factor == 250.0
    salt = salt_mass_for_buffer("Ammonium acetate", 5.0, 50.0)
    assert salt.mass_g > 0
    assert abs(convert_concentration(10.0, "ng/mL", "ng/L") - 10000.0) < 1e-6
    result = evaluate_recovery_pair(95.0, 102.0, 100.0)
    assert result.recovery.flag.value == "PASS"
    flagged = classify_recovery(55.0, RecoveryLimits())
    assert flagged.flag.value == "WARN"
    rows = generate_batch_sequence(
        BatchPlannerInput("DOCKER-TEST", sample_count=2),
        "Training minimal",
    )
    assert len(rows) >= 5
    print("=== Linux verify: ALL PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
