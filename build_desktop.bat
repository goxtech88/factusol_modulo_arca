@echo off
echo ================================================
echo   Factusol ARCA Sync - Build de Produccion
echo   GoxTech S.R.L.
echo ================================================
echo.

:: Verificar que el venv existe
if not exist venv\Scripts\python.exe (
    echo ERROR: No se encontro el entorno virtual en venv\
    echo Crear con: python -m venv venv
    pause
    exit /b 1
)

:: Instalar/actualizar dependencias de build
echo [1/4] Verificando dependencias de build...
venv\Scripts\pip install pywebview pyinstaller --quiet 2>nul

:: Limpiar builds anteriores
echo [2/4] Limpiando builds anteriores...
if exist dist\ARCA rmdir /s /q dist\ARCA
if exist build\ARCA rmdir /s /q build\ARCA
if exist dist\CertGen.exe del /q dist\CertGen.exe
if exist dist\LicenseGen.exe del /q dist\LicenseGen.exe
if exist build\CertGen rmdir /s /q build\CertGen
if exist build\LicenseGen rmdir /s /q build\LicenseGen

:: Build principal: ARCA.exe (carpeta)
echo [3/4] Compilando ARCA.exe (app principal)...
venv\Scripts\pyinstaller arca.spec --noconfirm
echo.

:: Build herramientas (archivos unicos)
echo [4/4] Compilando herramientas...
echo   - CertGen.exe (generador de certificados)...
venv\Scripts\pyinstaller CertGen.spec --noconfirm 2>nul
echo   - LicenseGen.exe (generador de licencias - USO INTERNO)...
venv\Scripts\pyinstaller LicenseGen.spec --noconfirm 2>nul
echo.

:: Verificar resultado
echo ================================================
if exist dist\ARCA\ARCA.exe (
    echo   BUILD EXITOSO
    echo.
    echo   App principal:
    echo     dist\ARCA\           ^<-- Copiar esta carpeta al cliente
    echo     dist\ARCA\ARCA.exe   ^<-- Ejecutable principal
    echo.
    if exist dist\CertGen.exe (
        echo   Herramientas:
        echo     dist\CertGen.exe     ^<-- Generador de certificados
    )
    if exist dist\LicenseGen.exe (
        echo     dist\LicenseGen.exe  ^<-- Generador de licencias [INTERNO]
    )
    echo.
    echo   Para distribuir al cliente:
    echo     1. Copiar carpeta dist\ARCA\ al servidor
    echo     2. Generar certificados con CertGen.exe
    echo     3. Generar licencia con LicenseGen.exe
    echo     4. Ejecutar ARCA.exe en el servidor
) else (
    echo   ERROR: El build fallo. Revisa los logs arriba.
)
echo ================================================
echo.
pause
