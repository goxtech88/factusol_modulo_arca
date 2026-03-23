@echo off
echo ========================================
echo  Factusol ARCA - Build Desktop App
echo ========================================
echo.

:: Instalar/actualizar dependencias
echo [1/3] Instalando dependencias...
venv\Scripts\pip install pywebview pyinstaller --quiet

:: Limpiar build anterior
echo [2/3] Limpiando build anterior...
if exist dist\FactusolARCA rmdir /s /q dist\FactusolARCA
if exist build\FactusolARCA rmdir /s /q build\FactusolARCA

:: Generar el exe
echo [3/3] Generando ejecutable...
venv\Scripts\pyinstaller FactusolARCA.spec --noconfirm

echo.
if exist dist\FactusolARCA\FactusolARCA.exe (
    echo ========================================
    echo  BUILD EXITOSO
    echo  Ejecutable: dist\FactusolARCA\FactusolARCA.exe
    echo  Distribuir toda la carpeta: dist\FactusolARCA\
    echo ========================================
) else (
    echo ERROR: El build fallo. Revisa los logs arriba.
)
pause
