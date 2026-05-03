@echo off
echo Starting AI Packaging Reliability Copilot Dashboard...
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Run the dashboard
python -m streamlit run frontend/dashboard.py

pause

@REM Made with Bob
