FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY lcms_lab_calc.py lcms_presets.py pfas_lcmsms_calculator_app.py ./
COPY scripts/verify_linux.py scripts/verify_linux.py
COPY data ./data
COPY .streamlit ./.streamlit

EXPOSE 8501

# Default: smoke test (override CMD to run Streamlit)
CMD ["python", "scripts/verify_linux.py"]
