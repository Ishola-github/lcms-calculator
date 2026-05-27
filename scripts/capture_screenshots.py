"""Capture Streamlit UI screenshots for README (dev utility; not shipped to users)."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "screenshots"
PORT = "8502"
URL = f"http://localhost:{PORT}"

TABS = [
    ("01_c1v1_dilution.png", "C1V1 dilution"),
    ("02_sample_spiking.png", "Sample spiking"),
    ("03_eis_nis.png", "EIS / NIS"),
    ("04_mobile_phase.png", "Mobile phase"),
    ("05_recovery_rpd.png", "Recovery / RPD"),
    ("06_batch_qc.png", "Batch QC"),
]


def wait_for_app(page, timeout_s: float = 120.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            page.goto(URL, wait_until="networkidle", timeout=15000)
            if page.locator("h1", has_text="PFAS LC-MS/MS preparation helper").count():
                page.wait_for_timeout(2500)
                return
        except Exception:
            pass
        time.sleep(2.0)
    raise RuntimeError(f"Streamlit app not ready at {URL}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ROOT / "pfas_lcmsms_calculator_app.py"),
            "--server.headless",
            "true",
            "--server.port",
            PORT,
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            wait_for_app(page)
            page.screenshot(path=str(OUT / "00_overview_c1v1.png"), full_page=True)
            for filename, label in TABS:
                page.get_by_role("tab", name=label).click()
                page.wait_for_timeout(800)
                page.screenshot(path=str(OUT / filename), full_page=True)
            browser.close()
        print(f"Wrote {len(TABS) + 1} screenshots to {OUT}")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
