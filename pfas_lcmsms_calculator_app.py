"""
PFAS LC-MS/MS preparation helper (Streamlit).

Research/training use only — not a validated regulatory reporting system.
Not part of PFAS Enterprise 5.0 frozen serum reproducibility program.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from lcms_presets import (
    ANALYTE_PRESETS,
    CONC_UNIT_OPTIONS,
    PRESET_BY_NAME,
    convert_concentration,
    format_conc,
)

st.set_page_config(page_title="PFAS LC-MS/MS Prep Helper", layout="wide")

st.title("PFAS LC-MS/MS preparation helper")
st.caption(
    "Optional helper for standards, spiking, mobile phase, and QC planning. "
    "Research/training use only; not a validated regulatory reporting system."
)

with st.sidebar:
    st.subheader("Analyte preset")
    preset_names = ["Custom / manual"] + [p.name for p in ANALYTE_PRESETS]
    selected_preset = st.selectbox("Common PFAS analyte", preset_names, key="analyte_preset")
    if selected_preset != "Custom / manual":
        preset = PRESET_BY_NAME[selected_preset]
        st.caption(f"**CAS:** {preset.cas}")
        st.caption(preset.notes)
        st.info(
            f"Suggested starting points (verify against your SOP): "
            f"stock **{preset.typical_stock_ng_ml:g} ng/mL**, "
            f"target spike **{preset.typical_spike_ng_ml:g} ng/mL** in sample."
        )
        apply_defaults = st.button("Apply suggested spike values")
        if apply_defaults:
            st.session_state["spike_stock_ng_ml"] = float(preset.typical_stock_ng_ml)
            st.session_state["target_spike_ng_ml"] = float(preset.typical_spike_ng_ml)
            spike_u = st.session_state.get("spike_unit", "ng/mL")
            if spike_u in CONC_UNIT_OPTIONS:
                st.session_state["spike_stock_input"] = convert_concentration(
                    preset.typical_stock_ng_ml, "ng/mL", spike_u
                )
                st.session_state["target_spike_input"] = convert_concentration(
                    preset.typical_spike_ng_ml, "ng/mL", spike_u
                )

    st.divider()
    st.subheader("Unit helper")
    st.caption("Mass/volume conversions (aqueous, ρ ≈ 1 g/mL).")
    uh_value = st.number_input("Value to convert", min_value=0.0, value=10.0, format="%.6g")
    uh_from = st.selectbox("From unit", CONC_UNIT_OPTIONS, index=2, key="uh_from")
    uh_to = st.selectbox("To unit", CONC_UNIT_OPTIONS, index=0, key="uh_to")
    if uh_from != uh_to:
        converted = convert_concentration(uh_value, uh_from, uh_to)
        st.success(f"**{format_conc(converted, uh_to)}**")
    else:
        st.write(format_conc(uh_value, uh_from))

tab_c1v1, tab_spike, tab_eis, tab_mobile, tab_recovery, tab_qc = st.tabs(
    [
        "C1V1 dilution",
        "Sample spiking",
        "EIS / NIS",
        "Mobile phase",
        "Recovery / RPD",
        "Batch QC",
    ]
)

with tab_c1v1:
    st.subheader("C1V1 calculator")
    c1_unit = st.selectbox("Concentration units (C1, C2)", CONC_UNIT_OPTIONS, index=2, key="c1v1_unit")
    c1 = st.number_input("C1 (stock concentration)", min_value=0.0, value=100.0, format="%.6g")
    v2 = st.number_input("V2 (target volume, same units as V1)", min_value=0.0, value=1.0, format="%.6g")
    c2 = st.number_input("C2 (target concentration)", min_value=0.0, value=1.0, format="%.6g")
    if c2 > 0 and c1 > 0:
        v1 = (c2 * v2) / c1
        st.success(f"Add stock volume V1 = **{v1:.6g}** (same units as V2)")
        st.info(f"Diluent volume ≈ **{max(v2 - v1, 0):.6g}** (if V1 ≤ V2)")
        if c1_unit != "ng/mL":
            st.caption(
                f"C2 in ng/mL ≈ **{convert_concentration(c2, c1_unit, 'ng/mL'):.6g}** "
                f"(unit helper reference only)."
            )
    else:
        st.warning("C1 and C2 must be > 0.")

with tab_spike:
    st.subheader("Sample spiking")
    if selected_preset != "Custom / manual":
        st.caption(f"Preset context: **{selected_preset}**")
    spike_unit = st.selectbox("Concentration units", CONC_UNIT_OPTIONS, index=2, key="spike_unit")
    sample_vol = st.number_input("Sample volume (mL)", min_value=0.0, value=1.0, format="%.6g")
    default_stock = float(st.session_state.get("spike_stock_ng_ml", 1000.0))
    default_target = float(st.session_state.get("target_spike_ng_ml", 10.0))
    if spike_unit != "ng/mL":
        default_stock = convert_concentration(default_stock, "ng/mL", spike_unit)
        default_target = convert_concentration(default_target, "ng/mL", spike_unit)
    spike_conc = st.number_input(
        f"Spike stock concentration ({spike_unit})",
        min_value=0.0,
        value=default_stock,
        key="spike_stock_input",
    )
    target_conc = st.number_input(
        f"Target spike level in sample ({spike_unit})",
        min_value=0.0,
        value=default_target,
        key="target_spike_input",
    )
    if sample_vol > 0 and spike_conc > 0 and target_conc > 0:
        stock_ng_ml = convert_concentration(spike_conc, spike_unit, "ng/mL")
        target_ng_ml = convert_concentration(target_conc, spike_unit, "ng/mL")
        spike_vol_ul = (target_ng_ml * sample_vol * 1000.0) / stock_ng_ml
        st.success(
            f"Spike volume ≈ **{spike_vol_ul:.3f} µL** into {sample_vol} mL sample "
            f"({format_conc(target_ng_ml, 'ng/mL')} in sample)."
        )
        if spike_unit != "ng/L":
            st.caption(
                f"Target ≈ **{convert_concentration(target_conc, spike_unit, 'ng/L'):.6g} ng/L**."
            )
    else:
        st.warning("All inputs must be > 0.")

with tab_eis:
    st.subheader("EIS / NIS spiking logic")
    if selected_preset != "Custom / manual":
        st.caption(f"Working analyte: **{selected_preset}** (labels only; enter your responses below).")
    st.markdown(
        "Enter native, EIS, and NIS areas (or concentrations) for one analyte. "
        "Recovery uses EIS; qualitative check compares NIS response."
    )
    eis_unit = st.selectbox("Response / concentration units", CONC_UNIT_OPTIONS, index=0, key="eis_unit")
    native = st.number_input("Native response", min_value=0.0, value=1000.0)
    eis = st.number_input("EIS response", min_value=0.0, value=950.0)
    nis = st.number_input("NIS response", min_value=0.0, value=50.0)
    eis_theoretical = st.number_input(
        f"Theoretical EIS in sample ({eis_unit})",
        min_value=0.0,
        value=1000.0,
    )
    if eis_theoretical > 0:
        eis_recovery = 100.0 * eis / eis_theoretical
        st.metric("EIS recovery (%)", f"{eis_recovery:.1f}")
    if native > 0:
        st.metric("EIS/native ratio", f"{eis / native:.3f}")
        st.metric("NIS/native ratio", f"{nis / native:.3f}")
    st.caption("Interpret against your SOP limits; this tool does not apply method-specific acceptance criteria.")

with tab_mobile:
    st.subheader("Mobile phase preparation")
    total_ml = st.number_input("Total mobile phase volume (mL)", min_value=0.0, value=1000.0)
    pct_a = st.slider("Organic fraction A (%)", 0.0, 100.0, 20.0)
    pct_b = 100.0 - pct_a
    if total_ml > 0:
        vol_a = total_ml * pct_a / 100.0
        vol_b = total_ml * pct_b / 100.0
        st.write(f"Component A: **{vol_a:.2f} mL** ({pct_a:.1f}%)")
        st.write(f"Component B: **{vol_b:.2f} mL** ({pct_b:.1f}%)")
    additive_ul = st.number_input("Additive (e.g. ammonium acetate) µL per L", min_value=0.0, value=0.0)
    if total_ml > 0 and additive_ul > 0:
        st.write(f"Additive volume: **{additive_ul * total_ml / 1000.0:.3f} µL** for {total_ml} mL")

with tab_recovery:
    st.subheader("Recovery and RPD")
    st.markdown("Duplicate spike recoveries and relative percent difference (RPD).")
    rec_unit = st.selectbox("Measured value units", CONC_UNIT_OPTIONS + ["% recovery"], index=0, key="rec_unit")
    rep1 = st.number_input("Replicate 1 measured", value=95.0)
    rep2 = st.number_input("Replicate 2 measured", value=102.0)
    nominal = st.number_input("Nominal / expected", value=100.0)
    if rec_unit == "% recovery":
        if nominal != 0:
            mean_r = (rep1 + rep2) / 2.0
            rpd = abs(rep1 - rep2) / ((rep1 + rep2) / 2.0) * 100.0 if (rep1 + rep2) else 0.0
            st.metric("Mean recovery (%)", f"{mean_r:.1f}")
            st.metric("RPD (%)", f"{rpd:.1f}")
    elif nominal != 0:
        r1 = 100.0 * rep1 / nominal
        r2 = 100.0 * rep2 / nominal
        mean_r = (r1 + r2) / 2.0
        rpd = abs(rep1 - rep2) / ((rep1 + rep2) / 2.0) * 100.0 if (rep1 + rep2) else 0.0
        st.metric("Mean recovery (%)", f"{mean_r:.1f}")
        st.metric("RPD (%)", f"{rpd:.1f}")
        st.caption(f"Nominal in ng/L ≈ **{convert_concentration(nominal, rec_unit, 'ng/L'):.6g}**.")

with tab_qc:
    st.subheader("Batch QC checklist")
    checks = {
        "Calibration bracketed per SOP": st.checkbox("Calibration bracketed", value=False),
        "Blanks acceptable": st.checkbox("Blanks acceptable", value=False),
        "LCS / CCV within limits": st.checkbox("LCS / CCV within limits", value=False),
        "IS recovery within SOP": st.checkbox("IS recovery within SOP", value=False),
        "Holding time documented": st.checkbox("Holding time documented", value=False),
        "Instrument tune / mass cal current": st.checkbox("Instrument tune current", value=False),
    }
    batch_id = st.text_input("Batch ID", value="BATCH-001")
    analyst = st.text_input("Analyst", value="")
    analyte_log = st.text_input(
        "Analyte / preset (optional)",
        value="" if selected_preset == "Custom / manual" else selected_preset,
    )
    notes = st.text_area("Notes", value="")
    all_done = all(checks.values())
    st.write("**Status:**", "Ready for review" if all_done else "Incomplete")
    if st.button("Export QC row to CSV"):
        row = {
            "batch_id": batch_id,
            "analyst": analyst,
            "analyte": analyte_log,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
            **{k.replace(" ", "_").lower(): v for k, v in checks.items()},
            "all_checks_pass": all_done,
        }
        df = pd.DataFrame([row])
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        st.download_button(
            "Download QC CSV",
            buf.getvalue(),
            file_name=f"pfas_lcms_qc_{batch_id}.csv",
            mime="text/csv",
        )

st.divider()
st.caption(
    "LC-MS/MS laboratory preparation helper only — separate from governed PFAS serum "
    "reproducibility releases. Not a validated regulatory engine."
)
