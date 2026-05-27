# Release `lcms-tools-v1.0.1`

**Tag:** `lcms-tools-v1.0.1` → commit `a674022`  
**Includes:** Phase 1–2 app features + release pack (MIT LICENSE, examples, docs, Streamlit config)

---

## Paste into GitHub Release

**URL:** https://github.com/Ishola-github/lcms-calculator/releases/new  
**Choose tag:** `lcms-tools-v1.0.1`  
**Release title:** `lcms-tools-v1.0.1 — PFAS LC-MS/MS preparation helper (RUO)`

**Description (copy below):**

---

## PFAS LC-MS/MS preparation helper — lcms-tools-v1.0.1

Research/training **workflow helper** for LC-MS/MS preparation and QC planning. **Manual analyst review required.**

### Features
- Analyte presets (PFOS, PFOA, PFHxS, PFNA, PFBS, GenX) + unit helper
- C1V1, sample spiking, SPE concentration factor
- Calibration prep table + CSV export
- Internal standard spiking
- Recovery PASS/WARN/FAIL (*suggested interpretation* — configure per SOP)
- Mobile phase chemistry (NH₄OAc / formate, MeOH/ACN, recipe text)
- Batch sequence planner (1633A-style *planning template* — editable, CSV export)
- Example CSVs in `examples/`

### Governance
- **Separate** from [PFAS Enterprise](https://github.com/Ishola-github/pfas-enterprise-modular) serum reproducibility releases
- **Do not** cite serum Zenodo `10.5281/zenodo.20348369` for this tool
- Not EPA/ISO certified · not for regulatory submission · not a validated QC engine

### License
MIT — see [LICENSE](https://github.com/Ishola-github/lcms-calculator/blob/main/LICENSE)

### Run locally
```powershell
pip install -r requirements.txt
streamlit run pfas_lcmsms_calculator_app.py
```

### Docs
- [Streamlit Cloud deploy](https://github.com/Ishola-github/lcms-calculator/blob/main/docs/DEPLOY_STREAMLIT_CLOUD.md)
- [Zenodo DOI workflow (calculator only)](https://github.com/Ishola-github/lcms-calculator/blob/main/docs/ZENODO_DOI_WORKFLOW.md)

---

## Streamlit Community Cloud (5 minutes)

1. https://share.streamlit.io/ → **Create app**
2. Repository: `Ishola-github/lcms-calculator`
3. Branch: `main`
4. Main file: `pfas_lcmsms_calculator_app.py`
5. Deploy → copy public URL into README (optional commit)

## Zenodo (calculator DOI only)

1. https://zenodo.org/ → link GitHub → `lcms-calculator`
2. Create version from GitHub release **`lcms-tools-v1.0.1`**
3. License: MIT · Resource type: Software
4. Publish → add new DOI to README citation block (replace `zenodo.XXXXXXX`)
5. **Never** use serum DOI `10.5281/zenodo.20348369` for this repo

## Optional polish

- Demo: `docs/DEMO_MEDIA.md`
- Screenshots: `python scripts\capture_screenshots.py` from project folder
