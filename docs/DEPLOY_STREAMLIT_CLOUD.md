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

## Repo files used

- `requirements.txt` — `streamlit`, `pandas`
- `.streamlit/config.toml` — theme and headless defaults

## App URL wording (README / release)

> Live demo (RUO): Streamlit Community Cloud deployment for training and workflow support. Not a validated regulatory service. Review all outputs against your laboratory SOP.

## Governance note

The cloud app is the **workflow helper lane**. Do not describe it as part of the frozen serum reproducibility program or cite the serum Zenodo DOI on the calculator landing page.
