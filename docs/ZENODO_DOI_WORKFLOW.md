# Zenodo DOI workflow — `lcms-calculator` only

Use this for the **LC-MS calculator** artifact. Keep it separate from the serum reproducibility record.

## DOI separation (critical)

| Artifact | Repository | Tag / DOI |
|----------|------------|-----------|
| Serum reproducibility evidence | `pfas-enterprise-modular` | `serum-v2.0.0-temporal` · Zenodo `10.5281/zenodo.20348369` |
| LC-MS prep helper (this tool) | `lcms-calculator` | `lcms-tools-v1.0.0` · **its own Zenodo DOI** |

Never cite the serum DOI for calculator downloads, screenshots, or Streamlit demos.

## Recommended steps

1. Ensure GitHub release exists for tag `lcms-tools-v1.0.0`.
2. In Zenodo: **New upload** → link GitHub account → select `lcms-calculator`.
3. Create Zenodo record from GitHub release `lcms-tools-v1.0.0`.
4. Metadata suggestions:
   - **Title:** PFAS LC-MS/MS preparation helper (RUO)
   - **Description:** Research/training workflow utility for standards prep, SPE, calibration, IS spiking, and QC planning. Not a validated regulatory system.
   - **License:** MIT
   - **Keywords:** PFAS, LC-MS/MS, laboratory, workflow, RUO
5. Publish → copy new DOI (e.g. `10.5281/zenodo.XXXXXXX`).
6. Add to `README.md` citation block (calculator DOI only).
7. Add DOI badge to README when published.

## README citation template (after Zenodo publish)

```bibtex
@software{lcms_calculator_2026,
  author = {Ishola},
  title = {PFAS LC-MS/MS Preparation Helper (RUO)},
  year = {2026},
  version = {lcms-tools-v1.0.0},
  url = {https://github.com/Ishola-github/lcms-calculator},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

Replace `XXXXXXX` with your published Zenodo ID.
