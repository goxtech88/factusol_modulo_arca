"""
Deploy generico de un HTML al servidor goxtech.com.ar.

Topologia: Mi PC -> 192.168.1.201 (jump) -> 192.168.1.212 (HestiaCP)

Uso:
    python deploy_html_page.py <local_file> <remote_dir> [<remote_filename>]

Ej:
    python deploy_html_page.py web_register/modulo-arca-v3.html modulo-arca index.html
    python deploy_html_page.py web_register/power-bi-v3.html power-bi index.html
"""
import argparse
import os
import sys
from datetime import datetime

import paramiko

JUMP_HOST = os.environ.get("ARCA_JUMP_HOST", "192.168.1.201")
JUMP_USER = os.environ.get("ARCA_JUMP_USER", "root")
JUMP_PASS = os.environ.get("ARCA_JUMP_PASS", "254136b+")

DEST_HOST = os.environ.get("ARCA_DEST_HOST", "192.168.1.212")
DEST_USER = os.environ.get("ARCA_DEST_USER", "admin")
DEST_PASS = os.environ.get("ARCA_DEST_PASS", "Goxtech2026!")

WEB_ROOT = "/home/goxtechcomar/web/goxtech.com.ar/public_html"


def main():
    parser = argparse.ArgumentParser(description="Deploy HTML al sitio publico")
    parser.add_argument("local_file", help="Path local al HTML")
    parser.add_argument("remote_dir", help="Subdir bajo public_html (ej: modulo-arca)")
    parser.add_argument("remote_filename", nargs="?", default="index.html",
                        help="Nombre final remoto (default: index.html)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    local_path = os.path.abspath(args.local_file)
    if not os.path.exists(local_path):
        print(f"ERROR: no se encuentra {local_path}")
        sys.exit(1)

    remote_dir = f"{WEB_ROOT}/{args.remote_dir.strip('/')}"
    remote_file = args.remote_filename
    public_url = f"https://goxtech.com.ar/{args.remote_dir.strip('/')}/"

    size = os.path.getsize(local_path)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    tmp_name = f"_deploy_{ts}.html"

    print("=" * 70)
    print(f"  Deploy HTML")
    print("=" * 70)
    print(f"  Local:       {local_path}")
    print(f"  Tamano:      {size:,} bytes")
    print(f"  Destino:     {remote_dir}/{remote_file}")
    print(f"  Public URL:  {public_url}")
    print(f"  Backup:      {remote_dir}/{remote_file}.bak.{ts}")
    print("=" * 70)

    if args.dry_run:
        print("\nDRY-RUN: no se subio nada.")
        return

    print(f"\n[1/4] Conectando al jump {JUMP_USER}@{JUMP_HOST}...")
    jump = paramiko.SSHClient()
    jump.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jump.connect(JUMP_HOST, username=JUMP_USER, password=JUMP_PASS, timeout=15)
    print("      OK")

    print(f"[2/4] Subiendo a /tmp/{tmp_name} del jump via SFTP...")
    sftp = jump.open_sftp()
    sftp.put(local_path, f"/tmp/{tmp_name}")
    sftp.close()
    print(f"      OK")

    print(f"[3/4] scp -O al destino {DEST_HOST}:/tmp/ ...")
    scp_cmd = (
        f"sshpass -p '{DEST_PASS}' scp -O -o StrictHostKeyChecking=no "
        f"/tmp/{tmp_name} {DEST_USER}@{DEST_HOST}:/tmp/ 2>&1"
    )
    _, o, _ = jump.exec_command(scp_cmd, timeout=60)
    print("      " + (o.read().decode().strip() or "OK"))

    print(f"[4/4] Backup + mv al destino final ...")
    sudo_bash = (
        f"mkdir -p {remote_dir} && "
        f"if [ -f {remote_dir}/{remote_file} ]; then "
        f"  cp {remote_dir}/{remote_file} {remote_dir}/{remote_file}.bak.{ts}; "
        f"fi && "
        f"cp /tmp/{tmp_name} {remote_dir}/{remote_file} && "
        f"chown goxtechcomar:goxtechcomar {remote_dir}/{remote_file} && "
        f"chmod 644 {remote_dir}/{remote_file} && "
        f"rm -f /tmp/{tmp_name} && "
        f"ls -la {remote_dir}/{remote_file}"
    )
    full = (
        f"sshpass -p '{DEST_PASS}' ssh -o StrictHostKeyChecking=no "
        f"{DEST_USER}@{DEST_HOST} \"echo {DEST_PASS} | sudo -S bash -c '{sudo_bash}' 2>&1\""
    )
    _, o, _ = jump.exec_command(full, timeout=60)
    print(o.read().decode())

    jump.exec_command(f"rm -f /tmp/{tmp_name}")
    jump.close()

    print(f"\n[verify] HTTPS publico...")
    import urllib.request
    import time
    time.sleep(2)
    try:
        req = urllib.request.Request(public_url, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"      HTTP {resp.status}, CL={resp.headers.get('Content-Length')} bytes")
    except Exception as e:
        print(f"      WARN: {e}")

    print(f"\n{'=' * 70}")
    print(f"  Deploy OK: {public_url}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
