# Demo GIF / video

Optional media for README and GitHub release `lcms-tools-v1.0.0`.

## Suggested capture (30–60 s)

1. Sidebar: analyte preset + unit helper
2. SPE factor tab: 250 mL → 1 mL
3. Calibration prep → Generate table
4. Recovery tab: PASS/WARN display
5. Batch sequence → Generate → CSV download

## Windows (PowerShell)

```powershell
cd C:\Users\techj\Downloads\lcms_calculator
python -m streamlit run pfas_lcmsms_calculator_app.py
```

Use any screen recorder (Xbox Game Bar, OBS) → save as `docs/media/demo.gif` or `demo.mp4`.

## README embed (after file exists)

```markdown
## Demo

![PFAS LC-MS/MS prep helper demo](docs/media/demo.gif)
```

Do not commit large binaries without Git LFS if the GIF exceeds ~10 MB.
