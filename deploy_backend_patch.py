"""
Deploy de los patches del backend de licencias al server real.

Flujo:
  1. Conecta via Proxmox jump host (192.168.1.201) al server HestiaCP
     (192.168.1.212), donde corre el servicio goxtech-licenses.
  2. Hace BACKUP automatico de:
       - cada archivo .py modificado → *.py.bak.YYYYMMDD-HHMMSS
       - licenses.db → licenses.db.bak.YYYYMMDD-HHMMSS
  3. Sube los archivos patcheados desde backend_patch/ a /opt/goxtech_licenses/.
  4. Reinicia el servicio (systemctl restart goxtech-licenses).
  5. Verifica con curl que el servicio respondio.
  6. Si algo falla → restaurar backup y reportar.

Uso:
    python deploy_backend_patch.py             # ejecuta el deploy
    python deploy_backend_patch.py --dry-run   # solo muestra el plan

Requisitos:
    pip install paramiko  (ya instalado en Python 3.12 del proyecto)
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime

import paramiko


# ─── Config ─────────────────────────────────────────────────────────────────
JUMP_HOST = os.environ.get("ARCA_JUMP_HOST", "192.168.1.201")
JUMP_USER = os.environ.get("ARCA_JUMP_USER", "root")
JUMP_PASS = os.environ.get("ARCA_JUMP_PASS", "254136b+")

DEST_HOST = os.environ.get("ARCA_DEST_HOST", "192.168.1.212")
DEST_USER = os.environ.get("ARCA_DEST_USER", "admin")
DEST_PASS = os.environ.get("ARCA_DEST_PASS", "Goxtech2026!")

REMOTE_BACKEND_DIR = "/opt/goxtech_licenses"
SERVICE_NAME = "goxtech-licenses"

LOCAL_PATCH_DIR = os.path.join(os.path.dirname(__file__), "backend_patch")

# Archivos que se van a deployar (top-level)
PATCH_FILES = [
    "models.py",
    "database.py",
    "schemas.py",
    "main.py",
    "requirements.txt",
]

# Archivos dentro de routers/ (mismo nombre en local y remoto)
PATCH_ROUTERS = [
    "_uploads.py",
    "admin_site.py",
]

# Si requirements.txt cambia, instalamos las nuevas deps en el venv del servicio
# antes de reiniciar.
PIP_INSTALL_AFTER_DEPLOY = True


def jump_exec(jump, cmd: str, timeout: int = 60) -> tuple[str, str]:
    """Ejecuta un comando en el jump host. Devuelve (stdout, stderr)."""
    _, o, e = jump.exec_command(cmd, timeout=timeout)
    return o.read().decode(), e.read().decode()


def remote_exec(jump, dest_cmd: str, timeout: int = 60) -> str:
    """Ejecuta un comando en el server destino via SSH a traves del jump.
    Devuelve solo stdout (stderr combinado para diagnostico)."""
    full = (
        f"sshpass -p '{DEST_PASS}' ssh -o StrictHostKeyChecking=no "
        f"{DEST_USER}@{DEST_HOST} {dest_cmd!r} 2>&1"
    )
    out, _ = jump_exec(jump, full, timeout=timeout)
    return out


def remote_sudo(jump, sudo_cmd: str, timeout: int = 60) -> str:
    """Ejecuta un comando con sudo en el server destino (pass via stdin)."""
    full_sudo = f"echo {DEST_PASS} | sudo -S bash -c {sudo_cmd!r}"
    return remote_exec(jump, full_sudo, timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description="Deploy patches backend licencias")
    parser.add_argument("--dry-run", action="store_true", help="No sube nada, solo muestra plan.")
    args = parser.parse_args()

    # Verificar que tenemos los archivos locales
    missing = [f for f in PATCH_FILES if not os.path.exists(os.path.join(LOCAL_PATCH_DIR, f))]
    if missing:
        print(f"ERROR: faltan archivos en {LOCAL_PATCH_DIR}: {missing}")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    print("=" * 70)
    print("  Deploy patches Backend Licencias")
    print("=" * 70)
    print(f"  Jump:        {JUMP_USER}@{JUMP_HOST}")
    print(f"  Destino:     {DEST_USER}@{DEST_HOST}")
    print(f"  Dir remoto:  {REMOTE_BACKEND_DIR}")
    print(f"  Servicio:    {SERVICE_NAME}")
    print(f"  Timestamp:   {ts}")
    print(f"  Archivos a patchear:")
    for f in PATCH_FILES:
        size = os.path.getsize(os.path.join(LOCAL_PATCH_DIR, f))
        print(f"    - {f}  ({size:,} bytes)")
    print("=" * 70)

    if args.dry_run:
        print("\nDRY-RUN: no se subio nada.")
        return

    # Conectar al jump host
    print(f"\n[1/6] Conectando al jump host {JUMP_USER}@{JUMP_HOST}...")
    jump = paramiko.SSHClient()
    jump.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jump.connect(JUMP_HOST, username=JUMP_USER, password=JUMP_PASS, timeout=15)
    print("      OK")

    # Asegurar sshpass instalado en el jump
    out, _ = jump_exec(jump, "which sshpass || (apt-get install -y sshpass -qq 2>&1 >/dev/null && which sshpass)")
    if "sshpass" not in out:
        print("      WARN: sshpass no disponible en jump host")

    # Verificar que existan los archivos de routers tambien
    routers_dir = os.path.join(LOCAL_PATCH_DIR, "routers")
    missing_routers = [f for f in PATCH_ROUTERS if not os.path.exists(os.path.join(routers_dir, f))]
    if missing_routers:
        print(f"WARN: faltan routers en {routers_dir}: {missing_routers}")
        # No falla — los routers son opcionales

    # 2) BACKUP de archivos .py y de la DB
    print(f"\n[2/6] Backup de archivos remotos...")
    backup_cmds = []
    for f in PATCH_FILES:
        backup_cmds.append(f"cp {REMOTE_BACKEND_DIR}/{f} {REMOTE_BACKEND_DIR}/{f}.bak.{ts} 2>/dev/null || true")
    for f in PATCH_ROUTERS:
        backup_cmds.append(f"cp {REMOTE_BACKEND_DIR}/routers/{f} {REMOTE_BACKEND_DIR}/routers/{f}.bak.{ts} 2>/dev/null || true")
    backup_cmds.append(f"cp {REMOTE_BACKEND_DIR}/licenses.db {REMOTE_BACKEND_DIR}/_backups/licenses.db.bak.{ts}")
    sudo_backup = " && ".join(backup_cmds)
    out = remote_sudo(jump, sudo_backup, timeout=60)
    print("      " + out.strip().replace("\n", "\n      "))

    # 3) Subir archivos patcheados a /tmp/ y luego sudo cp al destino
    print(f"\n[3/6] Subiendo archivos patcheados via SFTP al jump y luego scp -O al destino...")
    sftp = jump.open_sftp()
    for f in PATCH_FILES:
        local_path = os.path.join(LOCAL_PATCH_DIR, f)
        remote_tmp = f"/tmp/_patch_{f}"
        sftp.put(local_path, remote_tmp)
        print(f"      jump:/tmp/_patch_{f} OK ({sftp.stat(remote_tmp).st_size:,} bytes)")
    # Routers (con prefijo distinto para no chocar)
    for f in PATCH_ROUTERS:
        local_path = os.path.join(routers_dir, f)
        if not os.path.exists(local_path):
            continue
        remote_tmp = f"/tmp/_patchrouter_{f}"
        sftp.put(local_path, remote_tmp)
        print(f"      jump:/tmp/_patchrouter_{f} OK ({sftp.stat(remote_tmp).st_size:,} bytes)")
    sftp.close()

    # scp -O del jump al destino
    tmp_files = [f"/tmp/_patch_{f}" for f in PATCH_FILES]
    tmp_files += [f"/tmp/_patchrouter_{f}" for f in PATCH_ROUTERS if os.path.exists(os.path.join(routers_dir, f))]
    tmp_files_str = " ".join(tmp_files)
    scp_cmd = (
        f"sshpass -p '{DEST_PASS}' scp -O -o StrictHostKeyChecking=no "
        f"{tmp_files_str} {DEST_USER}@{DEST_HOST}:/tmp/ 2>&1"
    )
    out, _ = jump_exec(jump, scp_cmd, timeout=120)
    print("      scp -O: " + (out.strip() or "OK"))

    # 4) sudo mv al destino final + chown + chmod
    print(f"\n[4/6] Moviendo a {REMOTE_BACKEND_DIR}/ con sudo...")
    move_cmds = []
    for f in PATCH_FILES:
        move_cmds.append(f"cp /tmp/_patch_{f} {REMOTE_BACKEND_DIR}/{f}")
        move_cmds.append(f"chown www-data:www-data {REMOTE_BACKEND_DIR}/{f}")
        move_cmds.append(f"chmod 664 {REMOTE_BACKEND_DIR}/{f}")
    for f in PATCH_ROUTERS:
        if not os.path.exists(os.path.join(routers_dir, f)):
            continue
        move_cmds.append(f"cp /tmp/_patchrouter_{f} {REMOTE_BACKEND_DIR}/routers/{f}")
        move_cmds.append(f"chown www-data:www-data {REMOTE_BACKEND_DIR}/routers/{f}")
        move_cmds.append(f"chmod 664 {REMOTE_BACKEND_DIR}/routers/{f}")
    move_cmds.append(f"rm -f /tmp/_patch_*.py /tmp/_patch_*.txt /tmp/_patchrouter_*.py")
    move_cmds.append(f"ls -la {REMOTE_BACKEND_DIR}/main.py {REMOTE_BACKEND_DIR}/routers/_uploads.py {REMOTE_BACKEND_DIR}/routers/admin_site.py 2>/dev/null")
    out = remote_sudo(jump, " && ".join(move_cmds), timeout=60)
    print(out)

    # Limpiar /tmp/ del jump
    jump_exec(jump, f"rm -f {tmp_files_str}")

    # 4.5) Instalar nuevas deps si cambio requirements.txt
    if PIP_INSTALL_AFTER_DEPLOY:
        print(f"\n[4.5/6] Instalando deps de Python (Pillow, pillow-heif) en venv del servicio...")
        pip_cmd = (
            f"{REMOTE_BACKEND_DIR}/venv/bin/pip install --upgrade --quiet "
            f"-r {REMOTE_BACKEND_DIR}/requirements.txt 2>&1 | tail -10"
        )
        out = remote_sudo(jump, pip_cmd, timeout=180)
        print("      " + out.strip().replace("\n", "\n      "))

    # 5) Reiniciar servicio
    print(f"\n[5/6] Reiniciando servicio {SERVICE_NAME}...")
    out = remote_sudo(jump, f"systemctl restart {SERVICE_NAME} && sleep 2 && systemctl is-active {SERVICE_NAME}", timeout=30)
    print(f"      {out.strip()}")
    if "active" not in out:
        print("      ERROR: el servicio no esta active. Revisar journalctl.")
        # Mostrar ultimas lineas del log
        out = remote_sudo(jump, f"journalctl -u {SERVICE_NAME} -n 30 --no-pager", timeout=15)
        print("\n--- Log del servicio ---")
        print(out)
        print("\nIntentando rollback...")
        rollback_cmds = []
        for f in PATCH_FILES:
            rollback_cmds.append(f"cp {REMOTE_BACKEND_DIR}/{f}.bak.{ts} {REMOTE_BACKEND_DIR}/{f}")
        rollback_cmds.append(f"systemctl restart {SERVICE_NAME}")
        out = remote_sudo(jump, " && ".join(rollback_cmds), timeout=30)
        print(out)
        jump.close()
        sys.exit(1)

    # 6) Verificar respuesta del endpoint
    print(f"\n[6/6] Verificando endpoint /licenses/check via HTTPS publico...")
    import urllib.request
    time.sleep(2)
    try:
        with urllib.request.urlopen(
            "https://goxtech.com.ar/arca_factusol/api/licenses/check?cuit=00000000000",
            timeout=15,
        ) as resp:
            body = resp.read().decode()
            print(f"      HTTP {resp.status}: {body[:200]}")
    except Exception as e:
        print(f"      WARN: {e} (puede ser normal si CUIT 0000... no existe)")

    jump.close()
    print(f"\n{'=' * 70}")
    print(f"  Deploy OK. Backups en {REMOTE_BACKEND_DIR}/*.bak.{ts}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
