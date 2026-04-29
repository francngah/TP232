@echo off
TITLE AgroData 237 - Lanceur Intelligent
CHCP 65001 > nul

echo.
echo  ===========================================================
echo               AGRODATA 237 - VÉRIFICATION...
echo  ===========================================================
echo.

:: Vérification et installation des dépendances
echo  [1/2] Vérification des modules Python...
pip install -r requirements.txt --quiet
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Tous les modules sont installés.
) else (
    echo  [!] Erreur lors de l'installation automatique.
    echo  Tentative de lancement quand même...
)

echo.
echo  [2/2] Lancement de l'application...
where streamlit >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    streamlit run app.py
) else (
    python -m streamlit run app.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERREUR] L'application n'a pas pu démarrer.
    echo  Vérifiez que Python est bien installé.
    pause
)
