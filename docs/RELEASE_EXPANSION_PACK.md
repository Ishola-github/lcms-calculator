# Release expansion pack — checklist

One-page index for `lcms-tools-v1.0.0` polish. All items stay in **lcms-calculator** only.

| # | Item | Status / location |
|---|------|-------------------|
| 1 | Demo GIF/video | [DEMO_MEDIA.md](DEMO_MEDIA.md) — add `docs/media/demo.gif` when recorded |
| 2 | Downloadable CSV examples | [examples/](../examples/) |
| 3 | Screenshot thumbnails | [README](../README.md) + [screenshots/](../screenshots/) — refresh after Phase 2 |
| 4 | MIT LICENSE | [LICENSE](../LICENSE) |
| 5 | Streamlit Cloud deploy | [DEPLOY_STREAMLIT_CLOUD.md](DEPLOY_STREAMLIT_CLOUD.md) + `.streamlit/config.toml` |
| 6 | Separate Zenodo DOI | [ZENODO_DOI_WORKFLOW.md](ZENODO_DOI_WORKFLOW.md) |

## Recommended commits (from `lcms_calculator` root)

```powershell
cd C:\Users\techj\Downloads\lcms_calculator

git add LICENSE .streamlit/config.toml examples/ docs/ README.md .gitignore
git commit -m "Release pack: MIT license, examples, docs, Streamlit config"
git push

# Tag already exists locally? If not:
git tag -a lcms-tools-v1.0.0 -m "LC-MS prep helper RUO v1.0.0"
git push origin lcms-tools-v1.0.0

# GitHub: create Release from tag, paste body from RELEASE_lcms-tools-v1.0.0.md
```

## Governance reminders

- RUO / manual SOP review / not regulatory submission
- Do not cite serum Zenodo `10.5281/zenodo.20348369` for this tool
- Batch sequence = planning template, not compliance automation
- Recovery flags = suggested interpretation, not validated adjudication
