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

# Archivos y carpetas locales que se PRESERVAN durante una actualizacion.
# Si agregas algo aca, fijate como se nombra REALMENTE en disco.
#   - app_data.db: nombre real de la DB (database.py: DATABASE_PATH = DATA_DIR / "app_data.db")
#   - arca.db: nombre legacy mantenido por compatibilidad (en versiones <= 1.6.3
#     este nombre estaba mal en PRESERVE; al actualizar la DB no se preservaba)
PRESERVE_FILES = {
    "config.json",
    "app_data.db",
    "arca.db",           # legacy / compat
    "license.json",
    "license.key",
    "arca_debug.log",
}
PRESERVE_DIRS = {
    "certs",
    ".arca_browser",     # user-data-dir de Chrome/Edge embedded — evita re-login
}
PRESERVE = PRESERVE_FILES | PRESERVE_DIRS  # compat con codigo viejo si lo usa


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

    # 4. Generar update.bat con safety: backup ZIP + copy en vez de move + log
    app_dir = os.path.dirname(sys.executable)
    bat_path = os.path.join(temp_dir, "update.bat")
    backup_dir = os.path.join(app_dir, "backups")
    from datetime import datetime as _dt
    ts = _dt.now().strftime("%Y%m%d_%H%M%S")
    backup_zip = os.path.join(backup_dir, f"backup_pre-v{remote_version}_{ts}.zip")
    log_path = os.path.join(app_dir, f"update_{ts}.log")

    # Comandos para preservar archivos individuales (COPY en vez de move:
    # asi el original queda en su lugar y si el copy falla no perdemos nada)
    file_preserve_cmds = []
    for item in sorted(PRESERVE_FILES):
        file_preserve_cmds.append(
            f'if exist "{app_dir}\\{item}" (copy /y "{app_dir}\\{item}" "{temp_dir}\\preserve_{item}" >> "{log_path}" 2>&1 && echo   [OK] preservado {item} >> "{log_path}") else (echo   [SKIP] no existe {item} >> "{log_path}")'
        )

    # Comandos para preservar DIRECTORIOS (xcopy en vez de move — move falla
    # con directorios cuando hay handles o atributos especiales)
    dir_preserve_cmds = []
    for item in sorted(PRESERVE_DIRS):
        dir_preserve_cmds.append(
            f'if exist "{app_dir}\\{item}" (xcopy /e /i /h /y /q "{app_dir}\\{item}" "{temp_dir}\\preserve_{item}" >> "{log_path}" 2>&1 && echo   [OK] preservado dir {item} >> "{log_path}") else (echo   [SKIP] no existe dir {item} >> "{log_path}")'
        )

    # Restore: copia desde temp de vuelta. Sobrescribe el archivo (ahora vacio/nuevo)
    # con el preservado. Si no se preservo (no existia), no hace nada.
    file_restore_cmds = []
    for item in sorted(PRESERVE_FILES):
        file_restore_cmds.append(
            f'if exist "{temp_dir}\\preserve_{item}" (copy /y "{temp_dir}\\preserve_{item}" "{app_dir}\\{item}" >> "{log_path}" 2>&1 && echo   [OK] restaurado {item} >> "{log_path}")'
        )
    dir_restore_cmds = []
    for item in sorted(PRESERVE_DIRS):
        dir_restore_cmds.append(
            f'if exist "{temp_dir}\\preserve_{item}" (xcopy /e /i /h /y /q "{temp_dir}\\preserve_{item}" "{app_dir}\\{item}" >> "{log_path}" 2>&1 && echo   [OK] restaurado dir {item} >> "{log_path}")'
        )

    # Backup ZIP completo del estado actual antes de actualizar.
    # Usa powershell Compress-Archive (disponible en Win10+). Si falla,
    # continuamos igual — el preserve por archivo ya es nuestra red de seguridad.
    # Excluye carpetas pesadas: _internal/ y .arca_browser/ NO se backupean
    # (no son datos del usuario, son binarios). Solo backupeamos config + DB + certs.
    backup_items = " ".join(
        f'"{app_dir}\\{i}"' for i in sorted(PRESERVE_FILES | PRESERVE_DIRS)
    )

    bat_content = f"""@echo off
chcp 65001 >nul
echo. > "{log_path}"
echo ============================================ >> "{log_path}"
echo ARCA Update v{current} -^> v{remote_version} >> "{log_path}"
echo Inicio: %DATE% %TIME% >> "{log_path}"
echo app_dir: {app_dir} >> "{log_path}"
echo temp_dir: {temp_dir} >> "{log_path}"
echo ============================================ >> "{log_path}"

echo.
echo ============================================
echo   ARCA - Actualizando a v{remote_version}
echo   Log: {log_path}
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
echo ARCA.exe cerrado, esperando 2s extra para liberar handles...
timeout /t 2 /nobreak >nul

echo [1/5] Creando backup ZIP de la configuracion actual...
echo [1/5] Backup en {backup_zip} >> "{log_path}"
if not exist "{backup_dir}" mkdir "{backup_dir}"
powershell -NoProfile -Command "try {{ Compress-Archive -Path {backup_items} -DestinationPath '{backup_zip}' -CompressionLevel Optimal -ErrorAction Stop; Write-Host 'Backup OK' }} catch {{ Write-Host ('Backup fallo (continuo igual): ' + $_.Exception.Message) }}" >> "{log_path}" 2>&1

echo [2/5] Preservando archivos de configuracion...
echo [2/5] Preserve files >> "{log_path}"
{chr(10).join(file_preserve_cmds)}
echo [2/5] Preserve dirs >> "{log_path}"
{chr(10).join(dir_preserve_cmds)}

echo [3/5] Copiando archivos nuevos...
echo [3/5] xcopy nuevo build >> "{log_path}"
xcopy /s /e /y /q "{source_dir}\\*" "{app_dir}\\" >> "{log_path}" 2>&1
if errorlevel 1 (
    echo ERROR: No se pudieron copiar los archivos nuevos. Restaurando... >> "{log_path}"
    echo ERROR: No se pudieron copiar los archivos nuevos.
    echo Restaurando configuracion...
    {chr(10).join(file_restore_cmds)}
    {chr(10).join(dir_restore_cmds)}
    echo Update FALLO - log en {log_path}
    pause
    exit /b 1
)

echo [4/5] Restaurando configuracion preservada...
echo [4/5] Restore files >> "{log_path}"
{chr(10).join(file_restore_cmds)}
echo [4/5] Restore dirs >> "{log_path}"
{chr(10).join(dir_restore_cmds)}

echo [5/5] Reiniciando ARCA...
echo [5/5] Reinicio: %DATE% %TIME% >> "{log_path}"
echo.
echo ============================================
echo   Actualizacion completada: v{remote_version}
echo   Log: {log_path}
echo   Backup: {backup_zip}
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
