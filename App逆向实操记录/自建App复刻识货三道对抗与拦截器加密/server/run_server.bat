@echo off
cd /d "%~dp0server"
set PYTHONIOENCODING=utf-8
python -u app.py > server.log 2>&1
