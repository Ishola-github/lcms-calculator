# Screenshots

UI captures for the README and future **`lcms-tools-v1.0.0`** release. These belong to the **lcms-calculator** repo only — not the governed serum reproducibility release or its Zenodo DOI.

| File | Tab |
|------|-----|
| `00_overview_c1v1.png` | Landing view (C1V1 dilution) |
| `01_c1v1_dilution.png` | C1V1 dilution |
| `02_sample_spiking.png` | Sample spiking |
| `03_eis_nis.png` | EIS / NIS |
| `04_mobile_phase.png` | Mobile phase |
| `05_recovery_rpd.png` | Recovery / RPD |
| `06_batch_qc.png` | Batch QC checklist + CSV export |

## Regenerate (optional, dev machine)

```powershell
cd C:\Users\techj\Downloads\lcms_calculator
.\.venv\Scripts\Activate.ps1
pip install playwright
python -m playwright install chromium
python scripts\capture_screenshots.py
```

Requires a local Python venv with `requirements.txt` installed. Playwright is not part of the runtime app dependencies.
