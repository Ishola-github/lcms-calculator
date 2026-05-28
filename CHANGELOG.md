# Changelog

All notable changes to the PFAS LC-MS/MS Preparation Helper (RUO) are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/). This is a
research-use-only (RUO) utility; releases are workflow snapshots, not validated/regulatory artifacts.

- Concept DOI (always latest): `10.5281/zenodo.20427175`

## [lcms-tools-v1.0.6] - 2026-05-28
Version DOI: `10.5281/zenodo.20434692`

### Added
- Toxicology Method Assistant tab (template-driven prep/chromatography/MS guidance,
  SPE vs SLE helper, validation target checker) backed by `data/method_templates.json`.

### Fixed
- Docker image now copies `data/` and `.streamlit/` so the Toxicology tab loads inside
  the container (previously crashed on missing `method_templates.json`).

### Changed
- Hardened `.gitignore` (caches, build artifacts, env/secret files, local outputs).

### Verified
- Docker build, Linux smoke test, Streamlit health check (HTTP 200), in-container
  template load, and clean tree synced with `origin/main`.

## [lcms-tools-v1.0.5] - 2026-05-28
Version DOI: `10.5281/zenodo.20427176`

### Changed
- Metadata synchronization release for Zenodo archival (no functional changes).

## [lcms-tools-v1.0.4] - 2026-05-28

### Added
- Streamlit Cloud live demo link and deployment checklist.

## [lcms-tools-v1.0.3] - 2026-05-27

### Added
- Streamlit Dockerfile and WSL/Docker verification guide.

## [lcms-tools-v1.0.0 - v1.0.2] - 2026-05-27

### Added
- Phase 1: SPE concentration factor, calibration prep table, internal standard helper,
  enriched analyte presets, unit conversion helper.
- Phase 2: recovery/RPD PASS/WARN/FAIL suggested interpretation, mobile phase chemistry
  helper, batch sequence planner (RUO templates).
- Release pack: MIT license, example CSVs, docs, Streamlit config.

[lcms-tools-v1.0.6]: https://github.com/Ishola-github/lcms-calculator/releases/tag/lcms-tools-v1.0.6
[lcms-tools-v1.0.5]: https://github.com/Ishola-github/lcms-calculator/releases/tag/lcms-tools-v1.0.5
[lcms-tools-v1.0.4]: https://github.com/Ishola-github/lcms-calculator/releases/tag/lcms-tools-v1.0.4
[lcms-tools-v1.0.3]: https://github.com/Ishola-github/lcms-calculator/releases/tag/lcms-tools-v1.0.3
