# Script PowerShell de démarrage pour l'Agent IA d'Analyse de Données

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Agent IA - Analyse de Données" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si le fichier .env existe
if (-not (Test-Path ".env")) {
    Write-Host "ATTENTION: Fichier .env manquant!" -ForegroundColor Red
    Write-Host "Copiez .env.example vers .env et configurez votre clé API OpenAI" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

# Démarrer l'application Streamlit
Write-Host "Démarrage de l'application..." -ForegroundColor Green
Write-Host "Ouvrez votre navigateur sur: http://localhost:8501" -ForegroundColor Blue
Write-Host ""
Write-Host "Pour arrêter l'application, appuyez sur Ctrl+C" -ForegroundColor Yellow
Write-Host ""

try {
    streamlit run app.py
}
catch {
    Write-Host "Erreur lors du démarrage: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour fermer"
}
