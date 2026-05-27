# Release `lcms-tools-v1.0.0`

Research-use-only (RUO) PFAS LC-MS/MS preparation helper — **not** the governed serum reproducibility program.

## What this release is

- Laboratory workflow utility: prep calculations, SPE factor, calibration tables, IS spiking, recovery suggestions, mobile phase chemistry, batch sequence templates
- Training and bench support with **manual analyst review required**
- Separate repository and citation line from PFAS Enterprise serum evidence

## What this release is not

- Not EPA-certified or ISO-certified software
- Not for regulatory submission
- Not a validated QC adjudicator or compliance automation engine
- **Do not** cite the serum reproducibility Zenodo DOI (`10.5281/zenodo.20348369`) for this tool

## Tag

```text
lcms-tools-v1.0.0 → commit 27833de (or current main at release time)
```

## GitHub release (suggested body)

```markdown
## PFAS LC-MS/MS preparation helper — lcms-tools-v1.0.0

RUO workflow helper for LC-MS/MS prep, QC planning, and training.

### Includes
- Analyte presets + unit helper
- SPE concentration factor
- Calibration prep table (CSV export)
- Internal standard spiking
- Recovery PASS/WARN/FAIL (suggested interpretation)
- Mobile phase chemistry helper
- Batch sequence planner (editable template)

### Governance
Separate from PFAS Enterprise serum reproducibility releases. Manual SOP review required.

### License
MIT — see LICENSE
```

## Files to attach to the GitHub release

- Source zip (automatic)
- Optional: `examples/*.csv`
- Optional: demo GIF (`docs/media/demo.gif`) when available
