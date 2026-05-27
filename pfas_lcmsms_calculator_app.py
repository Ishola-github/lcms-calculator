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

from lcms_lab_calc import (
    QCFlag,
    RecoveryLimits,
    RPDLimits,
    SALT_MW,
    calibration_prep_table,
    classify_recovery,
    evaluate_recovery_pair,
    internal_standard_spike,
    is_spike_with_extraction_note,
    organic_aqueous_volumes,
    ppm_to_mg_per_l,
    recipe_meoh_water_with_buffer,
    salt_mass_for_buffer,
    spe_concentration_factor,
)
from lcms_presets import (
    ANALYTE_PRESETS,
    CONC_UNIT_OPTIONS,
    DEFAULT_CAL_LEVELS_NG_L,
    IS_PRESET_BY_NAME,
    IS_PRESETS,
    PRESET_BY_NAME,
    convert_concentration,
    format_conc,
)

st.set_page_config(page_title="PFAS LC-MS/MS Prep Helper", layout="wide")

st.title("PFAS LC-MS/MS preparation helper")
st.caption(
    "Workflow helper for standards, SPE, spiking, calibration, and QC planning. "
    "Research/training use only — not EPA/ISO certified; not for regulatory submission."
)

with st.sidebar:
    st.subheader("Analyte preset")
    preset_names = ["Custom / manual"] + [p.name for p in ANALYTE_PRESETS]
    selected_preset = st.selectbox("Common PFAS analyte", preset_names, key="analyte_preset")
    if selected_preset != "Custom / manual":
        preset = PRESET_BY_NAME[selected_preset]
        st.caption(f"**CAS:** {preset.cas} · **MW:** {preset.molecular_weight:g} g/mol")
        st.caption(preset.notes)
        st.markdown(
            f"| | |\n|---|---|\n"
            f"| **Calibration range** | {preset.cal_range_low_ng_l:g}–{preset.cal_range_high_ng_l:g} ng/L |\n"
            f"| **Suggested IS** | {preset.suggested_is} |\n"
            f"| **Typical stock** | {preset.typical_stock_ng_ml:g} ng/mL |\n"
            f"| **Typical spike** | {preset.typical_spike_ng_ml:g} ng/mL in sample |"
        )
        if st.button("Apply preset to spiking + calibration"):
            st.session_state["spike_stock_ng_ml"] = float(preset.typical_stock_ng_ml)
            st.session_state["target_spike_ng_ml"] = float(preset.typical_spike_ng_ml)
            st.session_state["cal_stock_ng_ml"] = float(preset.typical_stock_ng_ml)
            st.session_state["cal_levels_text"] = ", ".join(
                str(x) for x in DEFAULT_CAL_LEVELS_NG_L
                if preset.cal_range_low_ng_l <= x <= preset.cal_range_high_ng_l
            ) or f"{preset.cal_range_low_ng_l}, {preset.cal_range_high_ng_l}"

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

(
    tab_c1v1,
    tab_spike,
    tab_spe,
    tab_cal,
    tab_is,
    tab_eis,
    tab_mobile,
    tab_recovery,
    tab_qc,
) = st.tabs(
    [
        "C1V1 dilution",
        "Sample spiking",
        "SPE factor",
        "Calibration prep",
        "Internal standard",
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
    else:
        st.warning("C1 and C2 must be > 0.")

with tab_spike:
    st.subheader("Sample spiking")
    if selected_preset != "Custom / manual":
        st.caption(f"Preset: **{selected_preset}**")
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

with tab_spe:
    st.subheader("SPE concentration factor")
    st.caption(
        "Relates original sample volume to final extract volume. "
        "Use your SOP for recovery and unit reporting."
    )
    col1, col2 = st.columns(2)
    with col1:
        spe_sample_ml = st.number_input("Sample volume (mL)", min_value=0.0, value=250.0, key="spe_sample")
    with col2:
        spe_final_ml = st.number_input("Final extract volume (mL)", min_value=0.0, value=1.0, key="spe_final")
    spe_dilution = st.number_input(
        "Post-extract dilution factor (1 = none)",
        min_value=0.0,
        value=1.0,
        format="%.6g",
        key="spe_dilution",
    )
    spe_measured = st.number_input(
        "Optional: measured concentration in final solvent (ng/L)",
        min_value=0.0,
        value=0.0,
        format="%.6g",
        help="Enter to back-calculate sample-equivalent concentration.",
    )
    if spe_sample_ml > 0 and spe_final_ml > 0 and spe_dilution > 0:
        spe = spe_concentration_factor(spe_sample_ml, spe_final_ml, spe_dilution)
        st.metric("Concentration factor (CF)", f"{spe.concentration_factor:.4g}")
        st.metric("Effective reporting divisor", f"{spe.effective_reporting_divisor:.4g}")
        st.info(
            f"**{spe_sample_ml:g} mL** sample → **{spe_final_ml:g} mL** extract "
            f"{'(no post-dilution)' if spe_dilution == 1 else f'× {spe_dilution:g} post-dilution'}."
        )
        if spe_measured > 0:
            sample_eq = spe.sample_equivalent_ng_l(spe_measured)
            st.success(
                f"Sample-equivalent concentration ≈ **{sample_eq:.4g} ng/L** "
                f"(from {spe_measured:g} ng/L in final solvent)."
            )
    else:
        st.warning("Sample volume, final extract volume, and dilution factor must be > 0.")

with tab_cal:
    st.subheader("Calibration curve preparation table")
    st.caption("Aqueous standards in ng/L; stock in ng/mL. Verify against your SOP.")
    if selected_preset != "Custom / manual":
        p = PRESET_BY_NAME[selected_preset]
        st.caption(
            f"**{selected_preset}** suggested range: "
            f"{p.cal_range_low_ng_l:g}–{p.cal_range_high_ng_l:g} ng/L"
        )
    cal_stock = st.number_input(
        "Stock concentration (ng/mL)",
        min_value=0.0,
        value=float(st.session_state.get("cal_stock_ng_ml", 1000.0)),
        key="cal_stock_input",
    )
    cal_final_ml = st.number_input("Final volume per standard (mL)", min_value=0.0, value=10.0)
    default_levels = st.session_state.get(
        "cal_levels_text",
        ", ".join(str(x) for x in DEFAULT_CAL_LEVELS_NG_L),
    )
    cal_levels_text = st.text_input(
        "Target levels (ng/L), comma-separated",
        value=default_levels,
        key="cal_levels_input",
    )
    if st.button("Generate calibration table", type="primary"):
        try:
            targets = [float(x.strip()) for x in cal_levels_text.split(",") if x.strip()]
            rows = calibration_prep_table(targets, cal_stock, cal_final_ml)
            df = pd.DataFrame(
                [
                    {
                        "Level": r.level_id,
                        "Target (ng/L)": r.target_ng_l,
                        "Stock volume (µL)": round(r.stock_volume_ul, 3),
                        "Diluent (mL)": round(r.diluent_volume_ml, 4),
                        "Final volume (mL)": r.final_volume_ml,
                    }
                    for r in rows
                ]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            st.download_button(
                "Download calibration prep CSV",
                buf.getvalue(),
                file_name="pfas_calibration_prep.csv",
                mime="text/csv",
            )
        except ValueError as exc:
            st.error(str(exc))

with tab_is:
    st.subheader("Internal standard spiking")
    st.caption("Isotope dilution / IS spike volume calculator (RUO defaults).")
    is_preset_name = st.selectbox(
        "IS mix preset (starting values)",
        [p.name for p in IS_PRESETS],
        key="is_preset",
    )
    is_preset = IS_PRESET_BY_NAME[is_preset_name]
    if selected_preset != "Custom / manual":
        st.caption(f"Analyte context: **{PRESET_BY_NAME[selected_preset].suggested_is}**")
    col_a, col_b = st.columns(2)
    with col_a:
        is_sample_ml = st.number_input("Sample volume (mL)", min_value=0.0, value=250.0, key="is_sample")
        is_stock = st.number_input(
            "IS stock concentration (ng/mL)",
            min_value=0.0,
            value=float(is_preset.typical_stock_ng_ml),
        )
    with col_b:
        is_target = st.number_input(
            "Target IS in sample (ng/mL)",
            min_value=0.0,
            value=float(is_preset.typical_target_ng_ml),
        )
        link_spe = st.checkbox("Include SPE pre-spike note (use SPE tab volumes)", value=False)
    if is_sample_ml > 0 and is_stock > 0 and is_target > 0:
        spike = internal_standard_spike(is_sample_ml, is_stock, is_target)
        spe_ctx = None
        if link_spe and st.session_state.get("spe_sample", 0) > 0:
            try:
                spe_ctx = spe_concentration_factor(
                    float(st.session_state["spe_sample"]),
                    float(st.session_state.get("spe_final", 1.0)),
                    float(st.session_state.get("spe_dilution", 1.0)),
                )
            except ValueError:
                spe_ctx = None
        st.success(is_spike_with_extraction_note(spike, spe_ctx))
        st.caption(is_preset.notes)
    else:
        st.warning("Sample volume, stock, and target must be > 0.")

with tab_eis:
    st.subheader("EIS / NIS response check")
    if selected_preset != "Custom / manual":
        st.caption(f"Working analyte: **{selected_preset}**")
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
        st.metric("EIS recovery (%)", f"{100.0 * eis / eis_theoretical:.1f}")
    if native > 0:
        st.metric("EIS/native ratio", f"{eis / native:.3f}")
        st.metric("NIS/native ratio", f"{nis / native:.3f}")
    st.caption("Interpret against your SOP; no method-specific acceptance criteria applied.")

with tab_mobile:
    st.subheader("Mobile phase & chemistry helper")
    st.caption(
        "RUO bench preparation estimates. Review against your laboratory SOP before use."
    )
    mp_total = st.number_input("Total mobile phase volume (mL)", min_value=0.0, value=1000.0, key="mp_total")

    sec_mix, sec_buffer, sec_ppm, sec_recipe = st.tabs(
        ["Organic / aqueous mix", "Buffer salts", "ppm → mg/L", "Recipe text"]
    )

    with sec_mix:
        organic_name = st.selectbox("Organic solvent", ["Methanol (MeOH)", "Acetonitrile (ACN)"])
        pct_org = st.slider("% organic (MeOH or ACN)", 0.0, 100.0, 95.0, key="mp_pct_org")
        if mp_total > 0:
            try:
                org_ml, aq_ml = organic_aqueous_volumes(mp_total, pct_org)
                st.success(
                    f"**{org_ml:.2f} mL** {organic_name} + **{aq_ml:.2f} mL** aqueous "
                    f"= **{mp_total:g} mL** ({pct_org:g}:{100 - pct_org:g})."
                )
            except ValueError as exc:
                st.error(str(exc))

    with sec_buffer:
        salt = st.selectbox("Salt", list(SALT_MW.keys()))
        buf_mm = st.number_input("Target concentration (mM)", min_value=0.0, value=5.0)
        buf_vol = st.number_input(
            "Aqueous volume to prepare (mL)",
            min_value=0.0,
            value=float(mp_total * (100 - pct_org) / 100.0) if mp_total else 50.0,
            help="Usually the aqueous fraction only.",
        )
        if buf_mm > 0 and buf_vol > 0:
            try:
                sm = salt_mass_for_buffer(salt, buf_mm, buf_vol)
                st.metric("Mass to weigh", f"{sm.mass_g:.4f} g")
                st.caption(f"≈ **{sm.mass_mg:.2f} mg** · MW {SALT_MW[salt]:g} g/mol")
                st.info(
                    f"Dissolve {sm.mass_g:.4f} g {salt} in water and dilute to **{buf_vol:g} mL** "
                    f"for ~**{buf_mm:g} mM** (verify on balance and SOP)."
                )
            except ValueError as exc:
                st.error(str(exc))

    with sec_ppm:
        st.markdown("**ppm → mg/L** (aqueous, ρ ≈ 1 g/mL)")
        ppm_val = st.number_input("ppm", min_value=0.0, value=5.0)
        st.success(f"≈ **{ppm_to_mg_per_l(ppm_val):.6g} mg/L**")
        mg_val = st.number_input("mg/L → ppm", min_value=0.0, value=5.0, key="mg_to_ppm")
        st.caption(f"≈ **{mg_val:.6g} ppm** (training approximation).")

    with sec_recipe:
        st.markdown("**Generate printable prep steps**")
        preset = st.selectbox(
            "Starting template",
            [
                "Custom",
                "95:5 MeOH/H2O + 5 mM NH4OAc (aqueous)",
                "80:20 ACN/H2O + 10 mM ammonium formate (aqueous)",
                "20:80 MeOH/H2O (no buffer)",
            ],
        )
        r_org = pct_org
        r_mm = buf_mm
        r_salt = salt
        r_solvent = organic_name
        if preset.startswith("95:5 MeOH"):
            r_org, r_mm, r_salt, r_solvent = 95.0, 5.0, "Ammonium acetate", "Methanol (MeOH)"
        elif preset.startswith("80:20 ACN"):
            r_org, r_mm, r_salt, r_solvent = 80.0, 10.0, "Ammonium formate", "Acetonitrile (ACN)"
        elif preset.startswith("20:80"):
            r_org, r_mm, r_salt, r_solvent = 20.0, 0.0, salt, "Methanol (MeOH)"

        add_1mp = st.checkbox("Note: 1-methylpiperidine additive (method-specific)", value=False)
        add_note = (
            "Add 1-methylpiperidine per method SOP (e.g. FDA PFAS LC-MS/MS workflows) — "
            "confirm µL/L with your validated procedure."
            if add_1mp
            else ""
        )
        if st.button("Generate recipe", type="primary") and mp_total > 0:
            try:
                recipe = recipe_meoh_water_with_buffer(
                    mp_total,
                    r_org,
                    r_solvent,
                    r_mm,
                    r_salt,
                    buffer_in_aqueous_only=True,
                    additive_note=add_note,
                )
                st.text_area("Prep sheet (copy to lab notebook)", recipe.as_text(), height=280)
            except ValueError as exc:
                st.error(str(exc))

def _render_qc_flag(label: str, flagged) -> None:
    """Color-coded suggested interpretation (RUO only)."""
    flag = flagged.flag
    text = (
        f"**{label} — suggested: {flag.value}**  \n"
        f"{flagged.value:.1f}% · {flagged.detail}"
    )
    if flag == QCFlag.PASS:
        st.success(text)
    elif flag == QCFlag.WARN:
        st.warning(text)
    else:
        st.error(text)


with tab_recovery:
    st.subheader("Recovery, RPD, and suggested QC flags")
    st.caption(
        "RUO workflow guidance only. **Suggested interpretation** — "
        "review against your laboratory SOP. Not an EPA acceptance engine or validated QC adjudicator."
    )
    rec_limits = RecoveryLimits()
    rpd_limits = RPDLimits()
    with st.expander("Configure limits (per laboratory SOP)", expanded=False):
        st.markdown("**Recovery (%):** PASS and WARN bands (inclusive).")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            pass_low = st.number_input("PASS low", value=70.0, key="rec_pass_lo")
        with c2:
            pass_high = st.number_input("PASS high", value=130.0, key="rec_pass_hi")
        with c3:
            warn_low = st.number_input("WARN low", value=50.0, key="rec_warn_lo")
        with c4:
            warn_high = st.number_input("WARN high", value=150.0, key="rec_warn_hi")
        st.markdown("**RPD (%):** upper limits for PASS and WARN.")
        r1, r2 = st.columns(2)
        with r1:
            rpd_pass = st.number_input("PASS max RPD", value=20.0, key="rpd_pass")
        with r2:
            rpd_warn = st.number_input("WARN max RPD", value=30.0, key="rpd_warn")
        try:
            rec_limits = RecoveryLimits(pass_low, pass_high, warn_low, warn_high)
            rpd_limits = RPDLimits(rpd_pass, rpd_warn)
            rec_limits.validate()
            rpd_limits.validate()
        except ValueError as exc:
            st.error(str(exc))
    rec_unit = st.selectbox("Measured value units", CONC_UNIT_OPTIONS + ["% recovery"], index=4, key="rec_unit")
    qc_label = st.text_input("QC sample label (optional)", value="Matrix spike duplicate")
    rep1 = st.number_input("Replicate 1 measured", value=95.0)
    rep2 = st.number_input("Replicate 2 measured", value=102.0)
    nominal = st.number_input("Nominal / expected", value=100.0)
    if nominal != 0 and (rep1 + rep2):
        try:
            result = evaluate_recovery_pair(
                rep1,
                rep2,
                nominal,
                values_are_percent_recovery=(rec_unit == "% recovery"),
                recovery_limits=rec_limits,
                rpd_limits=rpd_limits,
            )
            st.metric("Replicate 1 recovery (%)", f"{result.replicate_1_pct:.1f}")
            st.metric("Replicate 2 recovery (%)", f"{result.replicate_2_pct:.1f}")
            st.metric("Mean recovery (%)", f"{result.mean_recovery_pct:.1f}")
            st.metric("RPD (%)", f"{result.rpd_pct:.1f}")
            _render_qc_flag("Mean recovery", result.recovery)
            _render_qc_flag("RPD", result.rpd)
            st.info(
                "Manual analyst review required. Adjust limits in the expander to match your SOP "
                "(e.g. LCS, MS/MSD, IS recovery)."
            )
        except ValueError as exc:
            st.error(str(exc))

    st.divider()
    st.markdown("**Batch QC entries** (optional table)")
    batch_labels = st.text_input(
        "Labels (comma-separated)",
        value="LCS, MS/MSD rep1, MS/MSD rep2",
        key="rec_batch_labels",
    )
    batch_recoveries = st.text_input(
        "Recovery values (%, comma-separated)",
        value="98, 102, 88",
        key="rec_batch_vals",
    )
    if st.button("Evaluate batch recoveries"):
        try:
            labels = [x.strip() for x in batch_labels.split(",") if x.strip()]
            values = [float(x.strip()) for x in batch_recoveries.split(",") if x.strip()]
            if len(labels) != len(values):
                st.warning("Label count must match recovery value count.")
            else:
                rows = []
                for lab, val in zip(labels, values):
                    flagged = classify_recovery(val, rec_limits)
                    rows.append(
                        {
                            "Sample": lab,
                            "Recovery (%)": val,
                            "Suggested": flagged.flag.value,
                            "Note": flagged.detail,
                        }
                    )
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        except ValueError as exc:
            st.error(str(exc))

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
