@echo off
cd /d %~dp0..
python -m pip install -r requirements.txt
python -m uvicorn src.backend.app.main:app --reload --host 127.0.0.1 --port 8080