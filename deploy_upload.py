"""
Deploy ARCA al server publico de GoxTech (goxtechlabs.com.ar).

Topologia real (descubierta empiricamente):

    Mi PC (Windows)
        |
        |  paramiko SSH/SFTP
        v
    100.64.247.47  (Proxmox VE, root/254136b+)   <-- jump host (Tailscale; LAN 192.168.1.200)
        |
        |  sshpass + scp -O (protocolo legacy, SFTP subsystem deshabilitado)
        v
    192.168.1.212  (HestiaCP, admin/Goxtech2026!)
        |
        |  sudo cp (el dir destino es root:root)
        v
    /home/admin/web/goxtechlabs.com.ar/public_html/downloads/

El dominio goxtechlabs.com.ar resuelve a la IP publica 186.127.154.178, que
hace TLS termination en un Nginx Proxy Manager (en LXC 100 del Proxmox) y
proxea a 192.168.1.212:80. El SSH NO esta expuesto en internet — solo se
llega por LAN o Tailscale al Proxmox.

Uso:
    python deploy_upload.py                  # autodetecta version del CHANGELOG
    python deploy_upload.py --version 1.6.2
    python deploy_upload.py --dry-run        # solo muestra lo que haria
    python deploy_upload.py --no-manifest    # sube ZIP sin tocar arca-latest.json

Overrides por env var (opcional):
    ARCA_JUMP_HOST    default: 100.64.247.47  (Tailscale del Proxmox)
    ARCA_JUMP_USER    default: root
    ARCA_JUMP_PASS    default: 254136b+
    ARCA_DEST_HOST    default: 192.168.1.212
    ARCA_DEST_USER    default: admin
    ARCA_DEST_PASS    default: Goxtech2026!
    ARCA_DEST_DIR     default: /home/admin/web/goxtechlabs.com.ar/public_html/downloads/
    ARCA_PUBLIC_URL   default: https://goxtechlabs.com.ar/downloads
"""
import argparse
import json
import os
import re
import sys
from datetime import date

import paramiko


# ── Config con override por env var ────────────────────────────────────────
JUMP_HOST = os.environ.get("ARCA_JUMP_HOST", "100.64.247.47")
JUMP_USER = os.environ.get("ARCA_JUMP_USER", "root")
JUMP_PASS = os.environ.get("ARCA_JUMP_PASS", "254136b+")

DEST_HOST = os.environ.get("ARCA_DEST_HOST", "192.168.1.212")
DEST_USER = os.environ.get("ARCA_DEST_USER", "admin")
DEST_PASS = os.environ.get("ARCA_DEST_PASS", "Goxtech2026!")
DEST_DIR  = os.environ.get("ARCA_DEST_DIR",  "/home/admin/web/goxtechlabs.com.ar/public_html/downloads/")

PUBLIC_URL_BASE = os.environ.get("ARCA_PUBLIC_URL", "https://goxtechlabs.com.ar/downloads")
MANIFEST_FILENAME = "arca-latest.json"

LOCAL_DIST = os.path.join(os.path.dirname(__file__), "dist")
CHANGELOG_PATH = os.path.join(os.path.dirname(__file__), "CHANGELOG.md")


# ── Helpers ────────────────────────────────────────────────────────────────

def detect_latest_version() -> str:
    """Primera version listada en CHANGELOG.md = la mas reciente."""
    if not os.path.exists(CHANGELOG_PATH):
        return None
    with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
        m = re.search(r"^##\s+v(\d+\.\d+\.\d+)", f.read(), re.MULTILINE)
    return m.group(1) if m else None


def extract_changelog(version: str) -> str:
    """Bullet principal de la version, en una sola linea para el manifest."""
    if not os.path.exists(CHANGELOG_PATH):
        return f"v{version}: nueva version"
    with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = rf"^##\s+v{re.escape(version)}.*?$(.*?)(?=^##\s+v\d|\Z)"
    m = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if not m:
        return f"v{version}: nueva version"
    section = m.group(1).strip()
    bullet = re.search(r"^-\s+\*\*(.+?)\*\*:?\s*(.+?)$", section, re.MULTILINE)
    if bullet:
        return f"v{version}: {bullet.group(1)} - {bullet.group(2)[:200]}"
    return f"v{version}: nueva version"


def jump_exec(jump, cmd: str, timeout: int = 60) -> tuple:
    """Ejecuta un comando en el jump host y devuelve (stdout, stderr) decoded."""
    _, o, e = jump.exec_command(cmd, timeout=timeout)
    return o.read().decode(), e.read().decode()


# ── Deploy ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Deploy ARCA al server publico")
    parser.add_argument("--version", help="Version a subir (ej 1.6.2). Default: del CHANGELOG.")
    parser.add_argument("--changelog", help="Override del texto del changelog.")
    parser.add_argument("--dry-run", action="store_true", help="No sube nada, solo muestra que haria.")
    parser.add_argument("--no-manifest", action="store_true", help="Sube ZIP pero NO actualiza arca-latest.json.")
    parser.add_argument("--no-verify", action="store_true", help="Salta la verificacion final por curl.")
    args = parser.parse_args()

    version = args.version or detect_latest_version()
    if not version:
        print("ERROR: no detecte version. Pasa --version X.Y.Z")
        sys.exit(1)

    zip_name = f"ARCA_v{version}.zip"
    local_zip = os.path.join(LOCAL_DIST, zip_name)
    if not os.path.exists(local_zip):
        print(f"ERROR: no se encuentra {local_zip}")
        print(f"Generalo con: python -m PyInstaller arca.spec && powershell Compress-Archive dist/ARCA dist/{zip_name}")
        sys.exit(1)

    zip_size = os.path.getsize(local_zip)
    changelog_text = args.changelog or extract_changelog(version)
    manifest = {
        "version": version,
        "url": f"{PUBLIC_URL_BASE}/{zip_name}",
        "date": date.today().isoformat(),
        "changelog": changelog_text,
        "min_version": "1.0.0",
    }

    # ── Resumen ─────────────────────────────────────────────────────────
    print("=" * 64)
    print(f"  Deploy ARCA v{version}")
    print("=" * 64)
    print(f"  ZIP local:       {local_zip}")
    print(f"  Tamano:          {zip_size // 1024 // 1024} MB ({zip_size:,} bytes)")
    print(f"  Jump host:       {JUMP_USER}@{JUMP_HOST}    (Proxmox)")
    print(f"  Destino final:   {DEST_USER}@{DEST_HOST}    (HestiaCP)")
    print(f"  Remote dir:      {DEST_DIR}")
    print(f"  Public URL:      {manifest['url']}")
    print(f"  Manifest URL:    {PUBLIC_URL_BASE}/{MANIFEST_FILENAME}")
    print()
    print("  Manifest a publicar:")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    print("=" * 64)

    if args.dry_run:
        print("\nDRY-RUN: no se subio nada.")
        return

    # ── [1/4] Subir al jump host (Proxmox) ───────────────────────────────
    print(f"\n[1/4] Conectando al jump host {JUMP_USER}@{JUMP_HOST}...")
    jump = paramiko.SSHClient()
    jump.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        jump.connect(JUMP_HOST, username=JUMP_USER, password=JUMP_PASS, timeout=15)
    except Exception as e:
        print(f"ERROR auth en jump host: {e}")
        sys.exit(1)
    print("      OK")

    # Asegurar sshpass en el jump (lo necesitamos para el scp -O al destino)
    out, _ = jump_exec(jump, "which sshpass || (apt-get install -y sshpass -qq >/dev/null && which sshpass)", timeout=120)
    if "sshpass" not in out:
        print("      WARN: sshpass no disponible en jump host; intentando instalar...")

    # Subir el ZIP + manifest a /tmp/ del jump host via SFTP
    print(f"      Subiendo {zip_name} a /tmp/ del jump...")
    sftp = jump.open_sftp()
    remote_tmp_zip = f"/tmp/{zip_name}"
    remote_tmp_manifest = f"/tmp/{MANIFEST_FILENAME}"
    sftp.put(local_zip, remote_tmp_zip)
    uploaded_size = sftp.stat(remote_tmp_zip).st_size
    if uploaded_size != zip_size:
        print(f"ERROR: tamano en jump ({uploaded_size}) != local ({zip_size})")
        sys.exit(1)
    print(f"      OK: {uploaded_size:,} bytes en {remote_tmp_zip}")

    with sftp.open(remote_tmp_manifest, "wb") as f:
        f.write(json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"))
    sftp.close()
    print(f"      Manifest preparado en {remote_tmp_manifest}")

    # ── [2/4] Transferir del jump al destino via scp -O (legacy protocol) ──
    print(f"\n[2/4] Transfiriendo a /tmp/ del destino {DEST_USER}@{DEST_HOST} via scp -O...")
    scp_cmd = (
        f"sshpass -p '{DEST_PASS}' scp -O -o StrictHostKeyChecking=no "
        f"{remote_tmp_zip} {remote_tmp_manifest} {DEST_USER}@{DEST_HOST}:/tmp/ 2>&1"
    )
    out, err = jump_exec(jump, scp_cmd, timeout=300)
    if out.strip():
        print("      " + out.strip().replace("\n", "\n      "))

    # Verificar que el ZIP esta en /tmp/ del destino
    check_cmd = (
        f"sshpass -p '{DEST_PASS}' ssh -o StrictHostKeyChecking=no "
        f"{DEST_USER}@{DEST_HOST} 'stat -c %s /tmp/{zip_name} 2>/dev/null'"
    )
    out, _ = jump_exec(jump, check_cmd, timeout=30)
    remote_size = out.strip()
    if str(zip_size) != remote_size:
        print(f"ERROR: tamano en destino ({remote_size!r}) != local ({zip_size})")
        sys.exit(1)
    print(f"      OK: {remote_size} bytes en {DEST_HOST}:/tmp/{zip_name}")

    # ── [3/4] Mover con sudo al dir final + ajustar permisos ─────────────
    print(f"\n[3/4] sudo cp al destino final {DEST_DIR}...")
    actions = [f"cp /tmp/{zip_name} {DEST_DIR}"]
    if not args.no_manifest:
        actions.append(f"cp /tmp/{MANIFEST_FILENAME} {DEST_DIR}")
        actions.append(f"chown {DEST_USER}:{DEST_USER} {DEST_DIR}{zip_name} {DEST_DIR}{MANIFEST_FILENAME}")
        actions.append(f"chmod 644 {DEST_DIR}{zip_name} {DEST_DIR}{MANIFEST_FILENAME}")
    else:
        actions.append(f"chown {DEST_USER}:{DEST_USER} {DEST_DIR}{zip_name}")
        actions.append(f"chmod 644 {DEST_DIR}{zip_name}")
    actions.append(f"rm /tmp/{zip_name} /tmp/{MANIFEST_FILENAME}")
    actions.append(f"ls -la {DEST_DIR}")

    sudo_bash = " ; ".join(actions)
    sudo_cmd = (
        f'sshpass -p "{DEST_PASS}" ssh -o StrictHostKeyChecking=no '
        f'{DEST_USER}@{DEST_HOST} "echo {DEST_PASS} | sudo -S bash -c \'{sudo_bash}\' 2>&1"'
    )
    out, _ = jump_exec(jump, sudo_cmd, timeout=120)
    print(out)

    # Cleanup en jump host
    jump_exec(jump, f"rm -f {remote_tmp_zip} {remote_tmp_manifest}", timeout=15)
    jump.close()
    print("[3/4] OK - archivos en destino y limpieza hecha")

    # ── [4/4] Verificacion via HTTPS publico ────────────────────────────
    if args.no_verify:
        print("\n[4/4] Salteado (--no-verify)")
        return

    print(f"\n[4/4] Verificando publicacion via HTTPS...")
    import urllib.request
    import time
    time.sleep(2)

    # ZIP
    try:
        req = urllib.request.Request(manifest["url"], method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_len = int(resp.headers.get("Content-Length", "0"))
            print(f"      ZIP    {manifest['url']}")
            print(f"             HTTP {resp.status}, Content-Length: {content_len:,} bytes")
            if content_len != zip_size:
                print(f"             WARN: tamano remoto distinto al local ({zip_size:,})")
            else:
                print(f"             OK - tamanos coinciden")
    except Exception as e:
        print(f"             ERROR: {e}")

    # Manifest
    if not args.no_manifest:
        try:
            with urllib.request.urlopen(f"{PUBLIC_URL_BASE}/{MANIFEST_FILENAME}", timeout=15) as resp:
                pub_manifest = json.loads(resp.read().decode("utf-8"))
                print(f"\n      Manifest {PUBLIC_URL_BASE}/{MANIFEST_FILENAME}")
                print(f"             version publicada: {pub_manifest.get('version')}")
                if pub_manifest.get("version") == version:
                    print(f"             OK - manifest apunta a v{version}")
                else:
                    print(f"             WARN: manifest dice v{pub_manifest.get('version')}, esperaba v{version}")
        except Exception as e:
            print(f"             ERROR: {e}")

    print(f"\n{'=' * 64}")
    print(f"  Deploy completado: v{version}")
    print(f"{'=' * 64}")


if __name__ == "__main__":
    main()
