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

st.set_page_config(page_title="PFAS LC-MS/MS Prep Helper", layout="wide")

st.title("PFAS LC-MS/MS preparation helper")
st.caption(
    "Optional helper for standards, spiking, mobile phase, and QC planning. "
    "Research/training use only; not a validated regulatory reporting system."
)

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
    c1 = st.number_input("C1 (stock concentration)", min_value=0.0, value=100.0, format="%.6g")
    v2 = st.number_input("V2 (target volume, same units as V1)", min_value=0.0, value=1.0, format="%.6g")
    c2 = st.number_input("C2 (target concentration)", min_value=0.0, value=1.0, format="%.6g")
    if c2 > 0 and c1 > 0:
        v1 = (c2 * v2) / c1
        st.success(f"Add stock volume V1 = **{v1:.6g}** (same units as V2)")
        st.info(f"Diluent volume ≈ **{max(v2 - v1, 0):.6g}** (if V1 ≤ V2)")
    else:
        st.warning("C1 and C2 must be > 0.")

with tab_spike:
    st.subheader("Sample spiking")
    sample_vol = st.number_input("Sample volume (mL)", min_value=0.0, value=1.0, format="%.6g")
    spike_conc = st.number_input("Spike stock concentration (ng/mL)", min_value=0.0, value=1000.0)
    target_conc = st.number_input("Target spike level in sample (ng/mL)", min_value=0.0, value=10.0)
    if sample_vol > 0 and spike_conc > 0 and target_conc > 0:
        spike_vol_ul = (target_conc * sample_vol * 1000.0) / spike_conc
        st.success(f"Spike volume ≈ **{spike_vol_ul:.3f} µL** into {sample_vol} mL sample")
    else:
        st.warning("All inputs must be > 0.")

with tab_eis:
    st.subheader("EIS / NIS spiking logic")
    st.markdown(
        "Enter native, EIS, and NIS areas (or concentrations) for one analyte. "
        "Recovery uses EIS; qualitative check compares NIS response."
    )
    native = st.number_input("Native response", min_value=0.0, value=1000.0)
    eis = st.number_input("EIS response", min_value=0.0, value=950.0)
    nis = st.number_input("NIS response", min_value=0.0, value=50.0)
    eis_theoretical = st.number_input("Theoretical EIS in sample (same units)", min_value=0.0, value=1000.0)
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
    rep1 = st.number_input("Replicate 1 measured (ng/L or % recovery)", value=95.0)
    rep2 = st.number_input("Replicate 2 measured", value=102.0)
    nominal = st.number_input("Nominal / expected", value=100.0)
    if nominal != 0:
        r1 = 100.0 * rep1 / nominal
        r2 = 100.0 * rep2 / nominal
        mean_r = (r1 + r2) / 2.0
        rpd = abs(rep1 - rep2) / ((rep1 + rep2) / 2.0) * 100.0 if (rep1 + rep2) else 0.0
        st.metric("Mean recovery (%)", f"{mean_r:.1f}")
        st.metric("RPD (%)", f"{rpd:.1f}")

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
    notes = st.text_area("Notes", value="")
    all_done = all(checks.values())
    st.write("**Status:**", "Ready for review" if all_done else "Incomplete")
    if st.button("Export QC row to CSV"):
        row = {
            "batch_id": batch_id,
            "analyst": analyst,
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
