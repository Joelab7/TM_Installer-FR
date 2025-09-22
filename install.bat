@echo off
setlocal enabledelayedexpansion

:: Définir le répertoire du script
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=!SCRIPT_DIR:~0,-1!"

:: Vérifier les privilèges administrateur
net session >nul 2>&1
if %ERRORLEVEL% == 0 (
    goto :run_as_admin
) else (
    echo Demande d'élévation des privilèges...
    set "VBS_SCRIPT=%TEMP%\~runas_install.vbs"
    
    echo Set UAC = CreateObject^("Shell.Application"^) > "!VBS_SCRIPT!"
    echo UAC.ShellExecute "cmd.exe", "/c """"%~f0""", "", "runas", 1 >> "!VBS_SCRIPT!"
    
    wscript "!VBS_SCRIPT!"
    timeout /t 2 >nul
    del /f /q "!VBS_SCRIPT!" 2>nul
    exit /b
)

:run_as_admin
:: Afficher des informations de débogage
echo [DEBUG] Installation avec les privilèges administrateur...
echo [DEBUG] Current directory: %CD%
echo [DEBUG] Windows version:
ver
echo.

:: Vérifier si le script est exécuté en tant qu'administrateur
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ce script doit être exécuté en tant qu'administrateur.
    echo Veuillez cliquer droit sur le script et sélectionner "Exécuter en tant qu'administrateur".
    pause
    exit /b 1
)

echo ===================================
echo Installing Telegram Manager
echo ===================================
echo.

echo Checking Python...

:: Essayer différentes commandes Python
set PYTHON_CMD=python
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set PYTHON_CMD=python3
    %PYTHON_CMD% --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        set PYTHON_CMD=py
        %PYTHON_CMD% --version >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo Python n'est pas installé. Tentative d'installation...
            
            where winget >nul 2>&1
            if %ERRORLEVEL% EQU 0 (
                echo Vérification de curl...
                where curl >nul 2>&1
                if %ERRORLEVEL% NEQ 0 (
                    echo Installation de curl...
                    winget install -e --id cURL.cURL
                    if %ERRORLEVEL% NEQ 0 (
                        echo [ERREUR] Impossible d'installer curl. Installation de Python annulée.
                        pause
                        exit /b 1
                    )
                )
                
                echo Téléchargement de Python 3.11.9...
                curl -o python_installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
                if %ERRORLEVEL% NEQ 0 (
                    echo [ERREUR] Échec du téléchargement de Python 3.11.9
                    pause
                    exit /b 1
                )
                
                echo Installation de Python 3.11.9...
                python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
                del python_installer.exe
                
                if %ERRORLEVEL% EQU 0 (
                    echo Python a été installé avec succès.
                    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311"
                    
                    echo Updating PATH...
                    setx PATH "%PATH%;%PYTHON_PATH%;%PYTHON_PATH%\Scripts"
                    set "PATH=%PATH%;%PYTHON_PATH%;%PYTHON_PATH%\Scripts"
                    
                    set PYTHON_CMD=python
                    echo Vérification de l'installation de Python...
                    %PYTHON_CMD% --version
                    if %ERRORLEVEL% NEQ 0 (
                        echo [ERREUR] La vérification de l'installation de Python a échoué.
                        pause
                        exit /b 1
                    )
                ) else (
                    echo [ERREUR] L'installation de Python a échoué. Code d'erreur: %ERRORLEVEL%
                    echo.
                    echo Ouverture du navigateur pour télécharger Python 3.11.9...
                    start "" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
                    echo.
                    echo ===============================================================
                    echo INSTRUCTIONS D'INSTALLATION MANUELLE DE PYTHON 3.11.9
                    echo ===============================================================
                    echo 1. Dans l'installateur, COCHEZ la case "Add Python 3.11 to PATH"
                    echo 2. Cliquez sur "Install Now"
                    echo 3. Si une alerte de contrôle de compte d'utilisateur apparaît, cliquez sur "Oui"
                    echo 4. Attendez la fin de l'installation
                    echo 5. Une fois l'installation terminée, cliquez sur "Close"
                    echo 6. Relancez ce programme d'installation
                    echo ===============================================================
                    pause
                    exit /b 1
                )
            ) else (
                echo [ERREUR] Winget n'est pas disponible. Installation automatique impossible.
                echo.
                echo Ouverture du navigateur pour télécharger Python 3.11.9...
                start "" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
                echo.
                echo ===============================================================
                echo INSTRUCTIONS D'INSTALLATION MANUELLE DE PYTHON 3.11.9
                echo ===============================================================
                echo 1. Exécutez le fichier python-3.11.9-amd64.exe téléchargé
                echo 2. IMPORTANT : Cochez la case "Add Python 3.11 to PATH"
                echo 3. Cliquez sur "Install Now"
                echo 4. Si une alerte de contrôle de compte d'utilisateur apparaît, cliquez sur "Oui"
                echo 5. Attendez la fin de l'installation
                echo 6. Une fois l'installation terminée, cliquez sur "Close"
                echo 7. Redémarrez votre ordinateur
                echo 8. Relancez ce programme d'installation
                echo ===============================================================
                pause
                exit /b 1
            )
        )
    )
)

echo Python detection: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo Vérification de la version de Python...
%PYTHON_CMD% -c "import sys; print('Version détectée:', sys.version); exit(0 if sys.version_info >= (3, 8) else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Python 3.8 ou plus élevé est requis.
    pause
    exit /b 1
)

echo Python est déjà installé. Vérification de pywin32...
%PYTHON_CMD% -c "import win32com" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo pywin32 n'est pas installé. Tentative d'installation...
    %PYTHON_CMD% -m pip install pywin32
    if %ERRORLEVEL% EQU 0 (
        echo pywin32 installé avec succès.
    ) else (
        echo [WARNING] pywin32 n'a pas pu être installé. Certains fonctionnalités pourraient ne pas fonctionner correctement.
    )
) else (
    echo pywin32 est déjà installé.
)

echo ===================================
echo Vérification de Git...
echo ===================================
:: Vérifier si Git est installé
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git n'est pas installé. Tentative d'installation...
    
    where winget >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Installation de Git via winget...
        winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements
        
        if %ERRORLEVEL% EQU 0 (
            echo Git a été installé avec succès.
            echo Mise à jour du PATH...
            setx PATH "%PATH%;C:\\Program Files\\Git\\cmd"
            set "PATH=%PATH%;C:\\Program Files\\Git\\cmd"
            
            echo Vérification de l'installation de Git...
            git --version
            if %ERRORLEVEL% NEQ 0 (
                echo [ERREUR] La vérification de l'installation de Git a échoué.
                goto :install_git_manually
            )
        ) else (
            echo [ERREUR] L'installation de Git a échoué. Code d'erreur: %ERRORLEVEL%
            goto :install_git_manually
        )
    ) else (
        echo [ERREUR] Winget n'est pas disponible. Installation automatique impossible.
        goto :install_git_manually
    )
) else (
    echo Git est déjà installé.
    git --version
)

echo.
goto :git_install_success

:install_git_manually
echo.
echo Ouverture du navigateur pour télécharger Git 2.51.0...
start "" "https://github.com/git-for-windows/git/releases/download/v2.51.0.windows.1/Git-2.51.0-64-bit.exe"
echo.
echo ===============================================================
echo INSTRUCTIONS D'INSTALLATION MANUELLE DE GIT 2.51.0
echo ===============================================================
echo 1. Exécutez le fichier Git-2.51.0-64-bit.exe téléchargé
echo 2. Suivez les étapes de l'assistant d'installation avec les paramètres par défaut
echo 3. IMPORTANT : Sélectionnez 'Git from the command line and also from 3rd-party software'
echo 4. Continuez l'installation avec les options par défaut
echo 5. Si une alerte de contrôle de compte d'utilisateur apparaît, cliquez sur "Oui"
echo 6. Une fois l'installation terminée, cliquez sur "Finish"
echo 7. Redémarrez votre ordinateur
echo 8. Relancez ce programme d'installation
echo ===============================================================
pause
exit /b 1

:git_install_success
echo.
echo Vérification de Git terminée avec succès.
echo.

echo ===================================
echo Vérification des dépendances terminée
echo ===================================
echo.

echo Launching installer...
%PYTHON_CMD% "%~dp0setup_installer.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================
    echo Installation terminée !
    echo ===================================
) else (
    echo.
    echo ===================================
    echo Installation échouée
    echo ===================================
)

echo.
pause
