# PFAS LC-MS/MS preparation helper

[![Release](https://img.shields.io/github/v/tag/Ishola-github/lcms-calculator?label=lcms-tools-v1.0.1)](https://github.com/Ishola-github/lcms-calculator/releases/tag/lcms-tools-v1.0.1)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Research-use-only (RUO) LC-MS/MS preparation helper for PFAS workflows, standards preparation, spiking calculations, QC planning, and laboratory support.

This utility is intentionally separate from governed reproducibility workflows and frozen analytical releases.

**Not EPA-certified.**  
**Not ISO-certified software.**  
**Not intended for regulatory submission.**  
**Not a validated reporting platform.**

Repository: https://github.com/Ishola-github/lcms-calculator

## Live demo (optional)

Deploy on [Streamlit Community Cloud](docs/DEPLOY_STREAMLIT_CLOUD.md) for training demos. Manual analyst review required; not a regulatory service.

## Demo media

Screen recording instructions: [docs/DEMO_MEDIA.md](docs/DEMO_MEDIA.md). Add `docs/media/demo.gif` when available.

## Features

**Phase 1 — laboratory workflow helpers**

- C1V1 dilution calculator
- PFAS **analyte presets** (PFOS, PFOA, PFHxS, PFNA, PFBS, GenX) — MW, calibration range, suggested IS
- **SPE concentration factor** + sample-equivalent back-calculation
- **Calibration prep table** (ng/L levels → stock µL + diluent) with CSV export
- **Internal standard spiking** (MPFAC-MXA / Wellington-style starting values)
- Sample spiking + **unit helper** (ng/L ↔ ng/mL ↔ µg/L, etc.)
- EIS/NIS response check, recovery/RPD, mobile phase, batch QC CSV

**Phase 2**

- **Recovery PASS/WARN/FAIL** — configurable limits, *suggested interpretation* (RUO; review per SOP)
- **Mobile phase chemistry** — NH₄OAc / ammonium formate mass (mM), MeOH/ACN %, ppm↔mg/L, recipe text
- **Batch sequence planner** — editable 1633A-style / training templates; CSV export (planning aid only)

## Example downloads

| Example | File |
|---------|------|
| Calibration prep | [examples/calibration_prep_example.csv](examples/calibration_prep_example.csv) |
| Batch sequence | [examples/batch_sequence_example.csv](examples/batch_sequence_example.csv) |
| QC export | [examples/qc_export_example.csv](examples/qc_export_example.csv) |

## Scientific positioning

| This calculator | Governed serum release (separate repo) |
|-----------------|----------------------------------------|
| Lab helper / training utility | Reproducibility evidence |
| Preparation calculations | Frozen analytical release |
| Optional workflow support | Provenance + blind verification |

Do **not** cite the serum reproducibility Zenodo DOI (`10.5281/zenodo.20348369`) for this tool. When published, cite this repository’s **own** tag and Zenodo DOI — see [docs/ZENODO_DOI_WORKFLOW.md](docs/ZENODO_DOI_WORKFLOW.md).

## Verify in Linux / Docker

WSL or Ubuntu: [docs/VERIFY_LINUX_DOCKER.md](docs/VERIFY_LINUX_DOCKER.md)

Quick smoke test:

```powershell
docker build -t lcms-calculator-verify .
docker run --rm lcms-calculator-verify
```

## Setup

```powershell
cd C:\Users\techj\Downloads\lcms_calculator
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run pfas_lcmsms_calculator_app.py
```

Open http://localhost:8501

## Screenshots

| Overview (sidebar + C1V1) | SPE factor |
|:---:|:---:|
| ![Overview](screenshots/00_overview_c1v1.png) | *Refresh after Phase 2 — see below* |

| Calibration prep | Batch sequence |
|:---:|:---:|
| *Add updated captures* | *Add updated captures* |

Legacy tab gallery: [screenshots/01_c1v1_dilution.png](screenshots/01_c1v1_dilution.png) · [02_sample_spiking.png](screenshots/02_sample_spiking.png) · [03_eis_nis.png](screenshots/03_eis_nis.png) · [04_mobile_phase.png](screenshots/04_mobile_phase.png) · [05_recovery_rpd.png](screenshots/05_recovery_rpd.png) · [06_batch_qc.png](screenshots/06_batch_qc.png)

Regenerate: `python scripts/capture_screenshots.py` (see [screenshots/README.md](screenshots/README.md)).

## Citation (calculator only)

After Zenodo publish, use the DOI from [docs/ZENODO_DOI_WORKFLOW.md](docs/ZENODO_DOI_WORKFLOW.md):

```bibtex
@software{lcms_calculator_2026,
  title = {PFAS LC-MS/MS Preparation Helper (RUO)},
  version = {lcms-tools-v1.0.0},
  url = {https://github.com/Ishola-github/lcms-calculator},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

## License

MIT — see [LICENSE](LICENSE). Software is provided *as is* without warranty; RUO workflow guidance only.

## Repository layout

```text
lcms_calculator/
├── pfas_lcmsms_calculator_app.py
├── lcms_lab_calc.py
├── lcms_presets.py
├── requirements.txt
├── LICENSE
├── README.md
├── .streamlit/config.toml
├── docs/               # release, Zenodo, Streamlit Cloud, demo media
├── examples/           # sample CSV downloads
├── screenshots/
└── scripts/
```

Release notes: [docs/RELEASE_lcms-tools-v1.0.1.md](docs/RELEASE_lcms-tools-v1.0.1.md)

Do **not** run `git add .` inside `pfas-toxicology/pfas-toxicology`.
