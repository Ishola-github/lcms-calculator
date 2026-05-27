# Verify `lcms-calculator` in Ubuntu/WSL and Docker

Research/training utility only — separate from `pfas-enterprise-modular` serum reproducibility.

| Repo | Purpose |
|------|---------|
| `pfas-enterprise-modular` | Governed reproducibility / evidence |
| `lcms-calculator` | RUO workflow helper |

Do **not** cite serum Zenodo `10.5281/zenodo.20348369` for this tool.

---

## Option 1 — Ubuntu/WSL local (recommended first)

### 1. Open WSL

From Windows PowerShell:

```powershell
wsl
```

### 2. Go to the repo

```bash
cd /mnt/c/Users/techj/Downloads/lcms_calculator
ls
```

Expect: `README.md`, `requirements.txt`, `pfas_lcmsms_calculator_app.py`, `LICENSE`, `examples/`, `docs/`.

### 3. Create a Linux virtual environment

```bash
python3 -m venv .venv-linux
source .venv-linux/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Streamlit

```bash
streamlit run pfas_lcmsms_calculator_app.py
```

Open in Windows browser: http://localhost:8501

### 6. Manual tab check

- C1V1 dilution
- Sample spiking · SPE factor · Calibration prep · Internal standard
- EIS / NIS · Mobile phase · Recovery / RPD · Batch sequence · Batch QC
- CSV exports where available

### 7. Stop

`Ctrl+C` in the WSL terminal.

### Optional — smoke test only (no browser)

```bash
python scripts/verify_linux.py
```

Expected: `=== Linux verify: ALL PASS ===`

---

## Option 2 — Docker

Two Dockerfiles:

| File | Purpose |
|------|---------|
| `Dockerfile` | Fast **smoke test** (default CMD) |
| `Dockerfile.streamlit` | Full **Streamlit** app |

### 2A — Smoke test (CI-style)

**PowerShell:**

```powershell
cd C:\Users\techj\Downloads\lcms_calculator
docker build -t lcms-calculator-verify .
docker run --rm lcms-calculator-verify
```

**WSL:**

```bash
cd /mnt/c/Users/techj/Downloads/lcms_calculator
bash scripts/docker_verify.sh
```

Expected:

```text
=== Linux verify: ALL PASS ===
```

### 2B — Full Streamlit in Docker

**PowerShell:**

```powershell
cd C:\Users\techj\Downloads\lcms_calculator
docker build -f Dockerfile.streamlit -t lcms-calculator .
docker run --rm -p 8501:8501 lcms-calculator
```

Open: http://localhost:8501

Stop: `Ctrl+C`

### 2C — Streamlit from verify image (override CMD)

If you already built `lcms-calculator-verify`:

```powershell
docker run --rm -p 8501:8501 lcms-calculator-verify streamlit run pfas_lcmsms_calculator_app.py --server.headless=true --server.address=0.0.0.0 --server.port=8501 --browser.gatherUsageStats=false
```

Note: the verify image copies only core `.py` files; use **Dockerfile.streamlit** for a full repo copy.

---

## Docker cleanup (optional)

```powershell
docker ps -a
docker rm <container_id>
docker rmi lcms-calculator
docker rmi lcms-calculator-verify
```

---

## Governance

- OK to verify in Docker/WSL for this repo
- Manual analyst review still required
- Not EPA/ISO certified · not for regulatory submission
- No merge into governed Enterprise validation folders
