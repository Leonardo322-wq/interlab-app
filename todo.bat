@echo off
cd /d %~dp0

:: Iniciar servidor coordinador primero
start "" python coordinador_server.py

:: Esperar unos segundos para que el servidor arranque
timeout /t 3 >nul

:: Iniciar ngrok en segundo plano
start "" ngrok.exe http 5001

:: Esperar para que ngrok genere la URL
timeout /t 5 >nul

:: Ejecutar script que obtiene la URL de ngrok y la envía a Render
start "" python iniciar_ngrok_y_actualizar.py

exit
