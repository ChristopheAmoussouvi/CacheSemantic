# Enhanced Support Analytics Dashboard - PowerShell Startup Script
# Launches the Streamlit application with comprehensive KPIs and analytics

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "          Enhanced Support Analytics Dashboard" -ForegroundColor Yellow
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting comprehensive support analytics with:" -ForegroundColor Green
Write-Host "  - Key Performance Indicators (CSAT, FCR, AHT, NPS)" -ForegroundColor White
Write-Host "  - Customer Satisfaction Trends with dual y-axes" -ForegroundColor White
Write-Host "  - Channel Performance Analysis (Phone, Email, Chat, Social, Branch)" -ForegroundColor White
Write-Host "  - Agent Performance Metrics and Rankings" -ForegroundColor White
Write-Host "  - Advanced Filtering (Time, Channel, Agent, Category)" -ForegroundColor White
Write-Host "  - Ticket Analytics with Interactive Charts" -ForegroundColor White
Write-Host ""

# Check if Windows Terminal is available
$wtPath = Get-Command wt -ErrorAction SilentlyContinue

if ($wtPath) {
    Write-Host "Launching in Windows Terminal..." -ForegroundColor Green
    # Use Windows Terminal with new tab
    wt -d $PSScriptRoot powershell -Command "streamlit run app.py --server.port 8501; Read-Host 'Press Enter to exit'"
} else {
    Write-Host "Windows Terminal not found. Using current PowerShell session..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opening browser to: http://localhost:8501" -ForegroundColor Magenta
    Write-Host "Navigate to: 'Support Analytics' tab for enhanced dashboard" -ForegroundColor Magenta
    Write-Host ""
    
    # Launch Streamlit
    streamlit run app.py --server.port 8501
}

Read-Host "Press Enter to exit"