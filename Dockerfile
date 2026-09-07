# sidm-composite-dm-mediator Dockerfile
#
# Reproducible environment for the v0.4-prelim T90/T95 analyses.
# Tested with Docker Desktop on Windows 11 + WSL2 backend.
#
# USAGE:
#   docker build -t sidm-bench:latest .
#   docker run --rm -v "$(pwd):/workspace" sidm-bench:latest \
#     .venv-sidm-bench/bin/python v0.3-prelim/code/t90_v10_cross_detector.py
#
# Or for an interactive shell:
#   docker run --rm -it -v "$(pwd):/workspace" sidm-bench:latest bash
#
# PHILOSOPHY:
# - Python 3.12 (matches the .venv-sidm-bench currently used in dev)
# - Install from requirements.txt for pinned reproducibility
# - WIMpy_NREFT pulled from PyPI (1.2.0)
# - Optional Julia deps NOT included (use the optional install
#   steps in CONTRIBUTING.md if you need cosmopass/camb paths)
# - All paths use POSIX /workspace; mount the repo at /workspace
#
# TIER NOTES:
# - "core" tier: required for all sidm analyses (T41, T90, T95)
# - "test" tier: required for pytest + CI
# - "docs" tier: required for PDF generation pipeline (fpdf2)
# - "optional" tier: commented out, uncomment if needed

# ----------------------------------------------------------------------------
# Stage 1: Base image with Python 3.12 + system deps
# ----------------------------------------------------------------------------
FROM python:3.12-slim AS base

# System deps (numpy/scipy need OpenBLAS, matplotlib needs libpng)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas-dev \
    libpng-dev \
    libfreetype-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# ----------------------------------------------------------------------------
# Stage 2: Install Python deps
# ----------------------------------------------------------------------------
FROM base AS deps

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt /workspace/requirements.txt

# Upgrade pip + install all deps + WIMpy_NREFT
RUN pip install --no-cache-dir --upgrade pip wheel setuptools \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir WIMpy_NREFT==1.2.0

# Copy the rest of the repo (this layer invalidates on any code change)
COPY . /workspace/

# Make the venv the active python
ENV PATH="/workspace/.venv-sidm-bench/bin:$PATH"

# Default entrypoint: show Python + WIMpy versions
CMD ["python", "-c", "import sys, WIMpy; print(f'Python {sys.version}\\nWIMpy {WIMpy.__version__}')"]
