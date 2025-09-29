@echo off
REM Enhanced Support Analytics Dashboard - Windows Terminal Startup Script
REM Launches the Streamlit application with comprehensive KPIs and analytics

echo.
echo ====================================================================
echo          Enhanced Support Analytics Dashboard
echo ====================================================================
echo.
echo Starting comprehensive support analytics with:
echo   - Key Performance Indicators (CSAT, FCR, AHT, NPS)
echo   - Customer Satisfaction Trends with dual y-axes
echo   - Channel Performance Analysis (Phone, Email, Chat, Social, Branch)
echo   - Agent Performance Metrics and Rankings
echo   - Advanced Filtering (Time, Channel, Agent, Category)
echo   - Ticket Analytics with Interactive Charts
echo.

REM Try to use Windows Terminal if available, otherwise use regular command prompt
where wt >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Launching in Windows Terminal...
    wt -d "%~dp0" -- cmd /c "streamlit run app.py --server.port 8501 & pause"
) else (
    echo Windows Terminal not found. Using regular command prompt...
    echo.
    echo Opening browser to: http://localhost:8501
    echo Navigate to: "Support Analytics" tab for enhanced dashboard
    echo.
    streamlit run app.py --server.port 8501
)

pause