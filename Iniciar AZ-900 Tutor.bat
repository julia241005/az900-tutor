@echo off
title Tutor de Certificacoes
cd /d "%~dp0"
echo.
echo  Tutor de Certificacoes (AZ-900, AWS CLF-C02 e outras)
echo  -------------------------------------------
echo  Iniciando... o navegador abre em alguns segundos.
echo  Escolha a certificacao no seletor da lateral.
echo  Para desligar o tutor, feche esta janela.
echo.
call venv\Scripts\activate.bat
start "" cmd /c "timeout /t 12 /nobreak >nul & start http://localhost:8000"
python -m uvicorn api:app --port 8000
pause
