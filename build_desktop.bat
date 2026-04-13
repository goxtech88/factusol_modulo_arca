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

:: ============================================================
:: IMPORTANTE: Compilamos en un directorio LOCAL (fuera de OneDrive)
:: para evitar errores "Acceso denegado" por bloqueo de archivos
:: sincronizados. El resultado se copia de vuelta al finalizar.
::
:: Usamos "python -m PyInstaller" en vez de "pyinstaller.exe"
:: para evitar "Fatal error in launcher" en rutas con espacios.
:: ============================================================
set LOCAL_BUILD=C:\temp\arca_build
set LOCAL_DIST=%LOCAL_BUILD%\dist
set LOCAL_WORK=%LOCAL_BUILD%\work
set PY=venv\Scripts\python.exe

:: Instalar/actualizar dependencias de build
echo [1/5] Verificando dependencias de build...
%PY% -m pip install pywebview pyinstaller --quiet 2>nul

:: Limpiar directorio de build local
echo [2/5] Preparando directorio de build local...
if exist "%LOCAL_BUILD%" rmdir /s /q "%LOCAL_BUILD%" 2>nul
mkdir "%LOCAL_BUILD%" 2>nul
mkdir "%LOCAL_DIST%" 2>nul
mkdir "%LOCAL_WORK%" 2>nul

:: Build principal: ARCA.exe
echo [3/5] Compilando ARCA.exe (app principal)...
%PY% -m PyInstaller arca.spec --noconfirm --distpath "%LOCAL_DIST%" --workpath "%LOCAL_WORK%"
if %ERRORLEVEL% neq 0 (
    echo.
    echo   ERROR: Fallo la compilacion de ARCA.exe
    echo   Revisa los errores arriba.
    pause
    exit /b 1
)
echo.

:: Build herramientas
echo [4/5] Compilando herramientas...
echo   - CertGen.exe (generador de certificados)...
%PY% -m PyInstaller CertGen.spec --noconfirm --distpath "%LOCAL_DIST%" --workpath "%LOCAL_WORK%" 2>nul
echo   - LicenseGen.exe (generador de licencias - USO INTERNO)...
%PY% -m PyInstaller LicenseGen.spec --noconfirm --distpath "%LOCAL_DIST%" --workpath "%LOCAL_WORK%" 2>nul
echo.

:: Copiar resultado de vuelta al proyecto
echo [5/5] Copiando resultado a dist\...

:: Limpiar dist anterior (con reintentos por si OneDrive bloquea)
if exist dist\ARCA (
    rmdir /s /q dist\ARCA 2>nul
    timeout /t 2 /nobreak >nul
    if exist dist\ARCA rmdir /s /q dist\ARCA 2>nul
)
if not exist dist mkdir dist 2>nul

if exist "%LOCAL_DIST%\ARCA" (
    xcopy /s /e /i /y /q "%LOCAL_DIST%\ARCA" dist\ARCA >nul
)
if exist "%LOCAL_DIST%\CertGen.exe" copy /y "%LOCAL_DIST%\CertGen.exe" dist\ >nul 2>nul
if exist "%LOCAL_DIST%\LicenseGen.exe" copy /y "%LOCAL_DIST%\LicenseGen.exe" dist\ >nul 2>nul

:: Limpiar directorio temporal
rmdir /s /q "%LOCAL_BUILD%" 2>nul

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
