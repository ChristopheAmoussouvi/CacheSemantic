@echo off
REM Script de démarrage pour l'Agent IA d'Analyse de Données

echo ========================================
echo   Agent IA - Analyse de Données
echo ========================================
echo.

REM Vérifier si le fichier .env existe
if not exist .env (
    echo ATTENTION: Fichier .env manquant!
    echo Copiez .env.example vers .env et configurez votre clé API OpenAI
    echo.
    pause
    exit /b 1
)

REM Démarrer l'application Streamlit
echo Démarrage de l'application...
echo Ouvrez votre navigateur sur: http://localhost:8501
echo.
echo Pour arrêter l'application, appuyez sur Ctrl+C
echo.

streamlit run app.py

pause
