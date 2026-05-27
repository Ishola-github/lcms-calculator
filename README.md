# PFAS LC-MS/MS preparation helper

Research-use-only (RUO) LC-MS/MS preparation helper for PFAS workflows, standards preparation, spiking calculations, QC planning, and laboratory support.

This utility is intentionally separate from governed reproducibility workflows and frozen analytical releases.

**Not EPA-certified.**  
**Not ISO-certified software.**  
**Not intended for regulatory submission.**  
**Not a validated reporting platform.**

## Features

- C1V1 dilution calculator
- PFAS spiking helper
- EIS/NIS preparation logic
- Recovery and RPD calculations
- Mobile phase preparation helper
- Batch QC checklist and CSV export

## Scientific positioning

| This calculator | Governed serum release (separate repo) |
|-----------------|----------------------------------------|
| Lab helper / training utility | Reproducibility evidence |
| Preparation calculations | Frozen analytical release |
| Optional workflow support | Provenance + blind verification |

Do **not** cite the serum reproducibility Zenodo DOI for this tool. If you publish this calculator later, use its **own** repository tag and DOI (e.g. `lcms-tools-v1.0.0`).

Repository: https://github.com/Ishola-github/lcms-calculator

## Setup

```powershell
cd C:\Users\techj\Downloads\lcms_calculator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run pfas_lcmsms_calculator_app.py
```

Open http://localhost:8501

## Repository layout

```text
lcms_calculator/
├── pfas_lcmsms_calculator_app.py
├── requirements.txt
├── README.md
├── examples/
└── screenshots/
```

## Screenshots (optional)

Add UI captures under `screenshots/`, then:

```powershell
git add screenshots
git commit -m "Add screenshots and usage instructions"
git push
```

Do **not** run `git add .` inside `pfas-toxicology/pfas-toxicology`.
