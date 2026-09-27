# WSL + mutmut Setup Guide

If/when the user approves WSL install for mutmut:

## Prerequisites (admin required)

```bash
# In an admin PowerShell:
wsl --install -d Ubuntu-22.04
# Reboot if requested

# After reboot, set up Linux user
```

## Inside Ubuntu WSL

```bash
# Update
sudo apt update && sudo apt upgrade -y

# Install Python + pip + mutmut
sudo apt install -y python3 python3-pip python3-venv

# Create a venv (Linux Python, NOT Windows venv)
cd /mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate

# Install project deps
pip install numpy scipy emcee dynesty sympy arviz hypothesis pytest

# Install mutmut
pip install mutmut

# Run mutmut
mutmut run --paths-to-mutate=v0.3-prelim/code/t120_16_kinematic_threshold.py \
            --tests-dir=v0.3-prelim/tests
mutmut results
```

## Why mutmut needs WSL

Per https://github.com/boxed/mutmut/issues/397, mutmut 3.x dropped
Windows native support. It uses `fork` (Unix-only process duplication)
to test mutations in parallel subprocesses.

## Alternative: cosmic-ray

If user wants Windows-native mutation testing, try `cosmic-ray`
(also uses fork internally, but has Windows workarounds).

```bash
pip install cosmic-ray
cosmic-ray new-project sidm sidm.toml
cosmic-ray exec sidm.toml
```

**Status**: NOT YET RUN. Requires admin approval for WSL install.
