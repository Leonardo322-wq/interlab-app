@echo off
:loop
REM Obtener la hora actual
for /f "tokens=1-2 delims=:" %%a in ("%time%") do set hour=%%a& set minute=%%b

REM Quitar ceros a la izquierda
set /a h=1%hour% - 100
set /a m=1%minute% - 100

REM Ejecutar a las 13:58 (1:49 PM)
if %h%==13 if %m%==58 (
    echo Ejecutando captura a las 13:58
    wscript "C:\Users\1022966950\Documents\Etiquetas\INTERLAB\oculto.vbs"
    timeout /t 65 >nul
)

timeout /t 30 >nul
goto loop
