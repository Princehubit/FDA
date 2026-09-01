@echo off
echo ========================================================
echo Starting NFC Fraud Guard Server & Telemetry UI
echo ========================================================

call .\venv\Scripts\activate.bat

start "FastAPI Backend" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
start "Streamlit Dashboard" cmd /k "streamlit run app/dash.py --server.port 8501"

echo Services launched in separate windows.