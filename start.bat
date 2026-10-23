@echo off
cd /d "%~dp0"

@REM Create virtual environment for Python if not created
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install requirements
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Install PySWX from local source
pip install -e "../pyswx"

REM List invoke commands
invoke --list
