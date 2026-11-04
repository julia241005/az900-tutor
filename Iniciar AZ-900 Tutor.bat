@echo off
title AZ-900 Tutor
cd /d "%~dp0"
echo.
echo  AZ-900 Tutor
echo  -------------------------------------------
echo  Iniciando... o navegador abre em alguns segundos.
echo  Para desligar o tutor, feche esta janela.
echo.
call venv\Scripts\activate.bat
start "" cmd /c "timeout /t 12 /nobreak >nul & start http://localhost:8000"
python -m uvicorn api:app --port 8000
pause
