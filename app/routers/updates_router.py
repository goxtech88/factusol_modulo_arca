"""
Router para gestion de actualizaciones del sistema.
Verifica la ultima version disponible en el servidor web de GoxTech,
descarga el ZIP y aplica la actualizacion preservando configuraciones.
"""
import os
import sys
import logging
import tempfile
import zipfile
import subprocess
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/updates", tags=["updates"])
log = logging.getLogger("updates")

MANIFEST_URL = "https://goxtechlabs.com.ar/downloads/arca-latest.json"

# Archivos y carpetas que NO se reemplazan durante una actualizacion
PRESERVE = {"config.json", "arca.db", "license.json", "license.key", "certs"}


def _get_current_version() -> str:
    """Obtiene la version actual de la app."""
    try:
        from app.main import app
        return app.version
    except Exception:
        return "0.0.0"


def _compare_versions(current: str, remote: str) -> bool:
    """Retorna True si remote es mas nueva que current."""
    try:
        cur = [int(x) for x in current.split(".")]
        rem = [int(x) for x in remote.split(".")]
        return rem > cur
    except Exception:
        return False


@router.get("/check")
def check_for_updates(current_user: User = Depends(get_current_user)):
    """Verifica si hay una version mas nueva disponible."""
    import urllib.request
    import json

    current = _get_current_version()

    try:
        req = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "ARCA-Updater"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            manifest = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        log.error(f"Error al verificar actualizaciones: {e}")
        raise HTTPException(status_code=502, detail=f"No se pudo conectar al servidor de actualizaciones: {str(e)}")

    remote_version = manifest.get("version", "0.0.0")
    has_update = _compare_versions(current, remote_version)

    return {
        "current_version": current,
        "latest_version": remote_version,
        "has_update": has_update,
        "download_url": manifest.get("url", ""),
        "changelog": manifest.get("changelog", ""),
        "date": manifest.get("date", ""),
    }


@router.post("/apply")
def apply_update(current_user: User = Depends(get_current_user)):
    """
    Descarga la ultima version, la extrae y genera un script de actualizacion.
    El script espera a que ARCA.exe se cierre, reemplaza los archivos
    (preservando config, DB, certs y licencia) y reinicia la app.

    Solo funciona en modo produccion (exe empaquetado con PyInstaller).
    """
    import urllib.request
    import json

    # Solo en produccion (exe)
    if not getattr(sys, "frozen", False):
        raise HTTPException(
            status_code=400,
            detail="Las actualizaciones solo funcionan en el ejecutable de produccion.",
        )

    # 1. Obtener manifest
    try:
        req = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "ARCA-Updater"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            manifest = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al obtener manifest: {str(e)}")

    remote_version = manifest.get("version", "0.0.0")
    current = _get_current_version()

    if not _compare_versions(current, remote_version):
        return {"status": "up_to_date", "message": f"Ya estas en la version mas reciente ({current})"}

    download_url = manifest.get("url", "")
    if not download_url:
        raise HTTPException(status_code=500, detail="URL de descarga no disponible en el manifest")

    # 2. Descargar ZIP a temp
    temp_dir = tempfile.mkdtemp(prefix="arca_update_")
    zip_path = os.path.join(temp_dir, f"ARCA_v{remote_version}.zip")

    log.info(f"Descargando actualizacion v{remote_version} desde {download_url}...")
    try:
        req = urllib.request.Request(download_url, headers={"User-Agent": "ARCA-Updater"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(zip_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al descargar: {str(e)}")

    zip_size = os.path.getsize(zip_path)
    log.info(f"Descargado: {zip_path} ({zip_size // 1024 // 1024} MB)")

    # 3. Extraer ZIP
    extract_dir = os.path.join(temp_dir, "extracted")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al extraer ZIP: {str(e)}")

    # Buscar la carpeta ARCA dentro del ZIP (puede estar como subcarpeta)
    source_dir = extract_dir
    for item in os.listdir(extract_dir):
        candidate = os.path.join(extract_dir, item)
        if os.path.isdir(candidate) and os.path.exists(os.path.join(candidate, "ARCA.exe")):
            source_dir = candidate
            break

    if not os.path.exists(os.path.join(source_dir, "ARCA.exe")):
        raise HTTPException(status_code=500, detail="El ZIP no contiene ARCA.exe - formato invalido")

    # 4. Generar update.bat
    app_dir = os.path.dirname(sys.executable)
    bat_path = os.path.join(temp_dir, "update.bat")

    # Lista de archivos/carpetas a preservar
    preserve_cmds = []
    for item in PRESERVE:
        preserve_cmds.append(f'if exist "{app_dir}\\{item}" move /y "{app_dir}\\{item}" "{temp_dir}\\preserve_{item}" >nul 2>nul')

    restore_cmds = []
    for item in PRESERVE:
        restore_cmds.append(f'if exist "{temp_dir}\\preserve_{item}" move /y "{temp_dir}\\preserve_{item}" "{app_dir}\\{item}" >nul 2>nul')

    bat_content = f"""@echo off
chcp 65001 >nul
echo.
echo ============================================
echo   ARCA - Actualizando a v{remote_version}
echo   No cierre esta ventana...
echo ============================================
echo.

echo Esperando a que ARCA.exe se cierre...
:wait_loop
tasklist /FI "IMAGENAME eq ARCA.exe" 2>NUL | find /I "ARCA.exe" >NUL
if not errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_loop
)

echo ARCA.exe cerrado. Iniciando actualizacion...
timeout /t 1 /nobreak >nul

echo [1/4] Preservando configuracion...
{chr(10).join(preserve_cmds)}

echo [2/4] Copiando archivos nuevos...
xcopy /s /e /y /q "{source_dir}\\*" "{app_dir}\\" >nul
if errorlevel 1 (
    echo ERROR: No se pudieron copiar los archivos nuevos.
    echo Restaurando configuracion...
    {chr(10).join(restore_cmds)}
    pause
    exit /b 1
)

echo [3/4] Restaurando configuracion...
{chr(10).join(restore_cmds)}

echo [4/4] Reiniciando ARCA...
echo.
echo ============================================
echo   Actualizacion completada: v{remote_version}
echo   Reiniciando en 3 segundos...
echo ============================================
timeout /t 3 /nobreak >nul

start "" "{app_dir}\\ARCA.exe"

rmdir /s /q "{temp_dir}" >nul 2>nul
exit /b 0
"""

    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)

    log.info(f"Script de actualizacion generado: {bat_path}")

    # 5. Lanzar el bat y programar cierre de la app
    subprocess.Popen(
        ["cmd.exe", "/c", bat_path],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    log.info("Cerrando ARCA para aplicar actualizacion...")

    # Programar shutdown de la app en 2 segundos
    import threading
    def _shutdown():
        import time
        time.sleep(2)
        os._exit(0)

    threading.Thread(target=_shutdown, daemon=True).start()

    return {
        "status": "updating",
        "message": f"Descarga completada. Actualizando a v{remote_version}... La app se reiniciara automaticamente.",
        "new_version": remote_version,
    }
