@echo off
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo No Windows virtual environment found. Creating venv...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create the virtual environment. Is Python installed and on PATH?
        goto :keep_open
    )
    call "%~dp0venv\Scripts\activate.bat"
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements.
        goto :keep_open
    )
) else (
    call "%~dp0venv\Scripts\activate.bat"
)

echo Virtual environment activated.
echo Python: 
where python

:keep_open
echo %CMDCMDLINE% | find /I "/c" >nul
if not errorlevel 1 (
    echo.
    cmd /k
)
