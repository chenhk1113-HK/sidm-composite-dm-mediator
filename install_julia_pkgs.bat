@echo off
cd /d C:\Users\lamkuenai\projects\sidm-composite-dm-mediator
"C:\Users\lamkuenai\AppData\Local\Programs\Julia-1.13.0\bin\julia.exe" --project="C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\.venv-sidm-bench\julia_env" -e "import Pkg; Pkg.instantiate()"
