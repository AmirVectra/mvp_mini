@echo off
setlocal enabledelayedexpansion

REM Get version from pyproject.toml using Python
for /f "delims=" %%v in ('python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"') do (
    set "version=%%v"
)

echo Detected version: %version%

REM Check if 'build' module is installed
python -m build --version >nul 2>&1
if errorlevel 1 (
    echo Installing 'build' module...
    python -m pip install build || goto :error
)

REM Run the build
python -m build || goto :error

REM Create versioned folder inside dist
set "target=dist\dist_%version%"
if exist "%target%" (
    echo Removing existing folder: %target%
    rmdir /s /q "%target%"
)

mkdir "%target%"

REM Move files into versioned folder
move /Y dist\*.* "%target%" >nul

echo Build artifacts moved to %target%
goto :eof

:error
echo Failed to build or move files.
exit /b 1
