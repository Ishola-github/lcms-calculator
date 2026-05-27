# PFAS LC-MS/MS preparation helper

Research/training utility for LC-MS/MS preparation calculations.

## Features

- C1V1 dilution calculator
- PFAS spiking helper
- EIS/NIS preparation logic
- Recovery and RPD calculations
- Mobile phase preparation helper
- Batch QC checklist and CSV export

This tool is **not** a validated regulatory reporting system and is **separate** from governed PFAS reproducibility releases (PFAS Enterprise 5.0 serum program).

## Scientific positioning

| This calculator | Governed serum release (separate repo) |
|-----------------|----------------------------------------|
| Lab helper / training utility | Reproducibility evidence |
| Preparation calculations | Frozen analytical release |
| Optional workflow support | Provenance + blind verification |

Do **not** cite the serum reproducibility Zenodo DOI for this tool. If you publish this calculator later, use its **own** repository tag and DOI (e.g. `lcms-tools-v1.0.0`).

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

## Optional separate Git repo

```powershell
cd C:\Users\techj\Downloads\lcms_calculator
git init
git add README.md requirements.txt pfas_lcmsms_calculator_app.py .gitignore
git commit -m "Initial LC-MS preparation helper (RUO)"
# git remote add origin https://github.com/Ishola-github/lcms-calculator
```

Do **not** run `git add .` inside `pfas-toxicology/pfas-toxicology`.
