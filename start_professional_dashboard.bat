@echo off
echo ========================================
echo Professional Packaging Reliability Dashboard
echo ========================================
echo.
echo Starting dashboard...
echo.

python -m streamlit run frontend/professional_dashboard.py --server.port 8501

pause

@REM Made with Bob
