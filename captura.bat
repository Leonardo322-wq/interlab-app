@echo off
:: Verifica si ya está corriendo como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
  echo Ejecutando como administrador...
  python "C:\Users\1022966950\Documents\Etiquetas\INTERLAB\captura.py"
  pause
) else (
  echo Solicitando permisos de administrador...
  powershell -Command "Start-Process '%~f0' -Verb runAs"
)
