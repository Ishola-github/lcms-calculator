# Streamlit Community Cloud deployment

Deploy **only** from `Ishola-github/lcms-calculator` — not from `pfas-enterprise-modular`.

## Prerequisites

- Public GitHub repo (or private with Streamlit Cloud access)
- Main file: `pfas_lcmsms_calculator_app.py`
- Dependencies: `requirements.txt`

## Steps

1. Go to https://share.streamlit.io/
2. **New app** → select repository `lcms-calculator`
3. Branch: `main`
4. Main file path: `pfas_lcmsms_calculator_app.py`
5. Deploy
6. Copy the generated app URL
7. Update `README.md` line `Live URL (RUO): ADD_STREAMLIT_APP_URL_HERE`
8. Commit and push README change

## Repo files used

- `requirements.txt` — `streamlit`, `pandas`
- `.streamlit/config.toml` — theme and headless defaults

## App URL wording (README / release)

> Live demo (RUO): Streamlit Community Cloud deployment for training and workflow support. Not a validated regulatory service. Review all outputs against your laboratory SOP.

## Fast end-to-end checklist

1. Create app in Streamlit Cloud using this repo and main file.
2. Verify the app loads all tabs.
3. Paste URL into `README.md`.
4. Push update:

```powershell
cd C:\Users\techj\Downloads\lcms_calculator
git add README.md
git commit -m "Add Streamlit Cloud live demo URL"
git push
```

## Governance note

The cloud app is the **workflow helper lane**. Do not describe it as part of the frozen serum reproducibility program or cite the serum Zenodo DOI on the calculator landing page.
