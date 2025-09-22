@echo off
setlocal enabledelayedexpansion

:: Définir le répertoire du script
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=!SCRIPT_DIR:~0,-1!"

:: Afficher le chemin d'exécution
echo ===================================
echo Désinstallation de Telegram Manager
echo ===================================
echo.
echo Chemin d'exécution: %~dp0
echo.

:: Vérifier si Python est disponible
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python n'est pas dans le PATH. Tentative de détection...
    set "PYTHON_PATH="
    
    :: Vérifier les emplacements courants de Python
    for %%i in ("%LOCALAPPDATA%\Programs\Python\Python3*\python.exe") do set "PYTHON_PATH=%%i"
    if not defined PYTHON_PATH (
        for %%i in ("%PROGRAMFILES%\Python3*\python.exe") do set "PYTHON_PATH=%%i"
    )
    
    if not defined PYTHON_PATH (
        echo Erreur: Python n'est pas installé ou n'est pas dans le PATH.
        echo Veuillez installer Python 3.8 ou supérieur depuis https://www.python.org/downloads/
        pause
        exit /b 1
    )
) else (
    set "PYTHON_PATH=python"
)

echo Python détecté: !PYTHON_PATH!

:: Lancer le désinstalleur Python
echo.
echo Lancement du désinstalleur...
"!PYTHON_PATH!" "%SCRIPT_DIR%\setup_uninstaller.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================
    echo Désinstallation terminée !
    echo ===================================
) else (
    echo.
    echo ===================================
    echo Erreur lors de la désinstallation
    echo ===================================
)

echo.
pause