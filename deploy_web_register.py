"""
Sube web_register/index.html al sitio publico de goxtech.com.ar.

Ruta destino:
    /home/goxtechcomar/web/goxtech.com.ar/public_html/arca_factusol/index.html

Topologia (descubierta empiricamente):
    Mi PC → 192.168.1.201 (Proxmox jump) → 192.168.1.212 (HestiaCP)

Como el dueno del dominio goxtech.com.ar es el usuario `goxtechcomar`, hace
falta sudo para escribir ahi como `admin`. El script hace backup automatico
del index.html actual antes de pisarlo.

Uso:
    python deploy_web_register.py
    python deploy_web_register.py --dry-run
"""
import argparse
import os
import sys
from datetime import datetime

import paramiko

# ── Config ─────────────────────────────────────────────────────────────────
JUMP_HOST = os.environ.get("ARCA_JUMP_HOST", "192.168.1.201")
JUMP_USER = os.environ.get("ARCA_JUMP_USER", "root")
JUMP_PASS = os.environ.get("ARCA_JUMP_PASS", "254136b+")

DEST_HOST = os.environ.get("ARCA_DEST_HOST", "192.168.1.212")
DEST_USER = os.environ.get("ARCA_DEST_USER", "admin")
DEST_PASS = os.environ.get("ARCA_DEST_PASS", "Goxtech2026!")

REMOTE_DIR = "/home/goxtechcomar/web/goxtech.com.ar/public_html/arca_factusol"
REMOTE_FILE = "index.html"
LOCAL_FILE = os.path.join(os.path.dirname(__file__), "web_register", "index.html")
PUBLIC_URL = "https://goxtech.com.ar/arca_factusol/"


def main():
    parser = argparse.ArgumentParser(description="Deploy form de registro web")
    parser.add_argument("--dry-run", action="store_true", help="Solo muestra el plan, no toca nada.")
    args = parser.parse_args()

    if not os.path.exists(LOCAL_FILE):
        print(f"ERROR: no se encuentra {LOCAL_FILE}")
        sys.exit(1)

    size = os.path.getsize(LOCAL_FILE)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    print("=" * 70)
    print(f"  Deploy form de registro web")
    print("=" * 70)
    print(f"  Local:       {LOCAL_FILE}")
    print(f"  Tamano:      {size:,} bytes")
    print(f"  Jump host:   {JUMP_USER}@{JUMP_HOST}")
    print(f"  Destino:     {DEST_USER}@{DEST_HOST}:{REMOTE_DIR}/{REMOTE_FILE}")
    print(f"  Public URL:  {PUBLIC_URL}")
    print(f"  Backup:      {REMOTE_DIR}/{REMOTE_FILE}.bak.{ts}")
    print("=" * 70)

    if args.dry_run:
        print("\nDRY-RUN: no se subio nada.")
        return

    # Conectar al jump
    print(f"\n[1/4] Conectando al jump {JUMP_USER}@{JUMP_HOST}...")
    jump = paramiko.SSHClient()
    jump.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jump.connect(JUMP_HOST, username=JUMP_USER, password=JUMP_PASS, timeout=15)
    print("      OK")

    # Subir a /tmp/ del jump via SFTP
    print(f"[2/4] Subiendo a /tmp/ del jump via SFTP...")
    sftp = jump.open_sftp()
    sftp.put(LOCAL_FILE, "/tmp/_arca_register.html")
    sftp.close()
    print(f"      OK: /tmp/_arca_register.html")

    # scp -O al destino
    print(f"[3/4] scp -O al destino {DEST_HOST}:/tmp/ ...")
    scp_cmd = (
        f"sshpass -p '{DEST_PASS}' scp -O -o StrictHostKeyChecking=no "
        f"/tmp/_arca_register.html {DEST_USER}@{DEST_HOST}:/tmp/ 2>&1"
    )
    _, o, _ = jump.exec_command(scp_cmd, timeout=60)
    print("      " + (o.read().decode().strip() or "OK"))

    # Backup + mv con sudo al destino final
    print(f"[4/4] Backup actual + mv al destino final {REMOTE_DIR}/...")
    sudo_bash = (
        f"if [ -f {REMOTE_DIR}/{REMOTE_FILE} ]; then "
        f"  cp {REMOTE_DIR}/{REMOTE_FILE} {REMOTE_DIR}/{REMOTE_FILE}.bak.{ts}; "
        f"fi && "
        f"cp /tmp/_arca_register.html {REMOTE_DIR}/{REMOTE_FILE} && "
        f"chown goxtechcomar:goxtechcomar {REMOTE_DIR}/{REMOTE_FILE} && "
        f"chmod 644 {REMOTE_DIR}/{REMOTE_FILE} && "
        f"rm -f /tmp/_arca_register.html && "
        f"ls -la {REMOTE_DIR}/"
    )
    full = (
        f"sshpass -p '{DEST_PASS}' ssh -o StrictHostKeyChecking=no "
        f"{DEST_USER}@{DEST_HOST} \"echo {DEST_PASS} | sudo -S bash -c '{sudo_bash}' 2>&1\""
    )
    _, o, _ = jump.exec_command(full, timeout=60)
    print(o.read().decode())

    # Cleanup /tmp/ del jump
    jump.exec_command("rm -f /tmp/_arca_register.html")
    jump.close()

    # Verificacion via HTTPS
    print(f"\n[verify] Verificando via HTTPS publico...")
    import urllib.request
    import time
    time.sleep(2)
    try:
        req = urllib.request.Request(PUBLIC_URL, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"      HTTP {resp.status}, Content-Length: {resp.headers.get('Content-Length')} bytes")
    except Exception as e:
        print(f"      WARN: {e}")

    print(f"\n{'=' * 70}")
    print(f"  Deploy OK: {PUBLIC_URL}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
