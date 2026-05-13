"""Deploy archivos SEO al root publico del sitio: robots.txt, sitemap.xml, llms.txt."""
import os
import paramiko
from datetime import datetime

JUMP_HOST = "192.168.1.201"
JUMP_USER = "root"
JUMP_PASS = "254136b+"
DEST_HOST = "192.168.1.212"
DEST_USER = "admin"
DEST_PASS = "Goxtech2026!"
REMOTE_ROOT = "/home/goxtechcomar/web/goxtech.com.ar/public_html"

FILES = [
    ("web_register/seo/robots.txt", "robots.txt", "text/plain"),
    ("web_register/seo/sitemap.xml", "sitemap.xml", "application/xml"),
    ("web_register/seo/llms.txt", "llms.txt", "text/plain"),
]

ts = datetime.now().strftime("%Y%m%d-%H%M%S")
jump = paramiko.SSHClient()
jump.set_missing_host_key_policy(paramiko.AutoAddPolicy())
jump.connect(JUMP_HOST, username=JUMP_USER, password=JUMP_PASS, timeout=15)
print(f"[jump] Conectado a {JUMP_HOST}")

sftp = jump.open_sftp()
for local, remote_name, _ct in FILES:
    local_abs = os.path.join(os.path.dirname(__file__), local)
    tmp = f"/tmp/_seo_{ts}_{remote_name}"
    sftp.put(local_abs, tmp)
    print(f"[sftp]    -> {tmp} ({os.path.getsize(local_abs)} bytes)")

    scp = f"sshpass -p '{DEST_PASS}' scp -O -o StrictHostKeyChecking=no {tmp} {DEST_USER}@{DEST_HOST}:/tmp/"
    _, o, _ = jump.exec_command(scp, timeout=60); o.read()

    sudo = (
        f"if [ -f {REMOTE_ROOT}/{remote_name} ]; then "
        f"  cp {REMOTE_ROOT}/{remote_name} {REMOTE_ROOT}/{remote_name}.bak.{ts}; "
        f"fi && "
        f"cp /tmp/_seo_{ts}_{remote_name} {REMOTE_ROOT}/{remote_name} && "
        f"chown goxtechcomar:goxtechcomar {REMOTE_ROOT}/{remote_name} && "
        f"chmod 644 {REMOTE_ROOT}/{remote_name} && "
        f"rm -f /tmp/_seo_{ts}_{remote_name}"
    )
    full = (
        f"sshpass -p '{DEST_PASS}' ssh -o StrictHostKeyChecking=no "
        f"{DEST_USER}@{DEST_HOST} \"echo {DEST_PASS} | sudo -S bash -c '{sudo}' 2>&1\""
    )
    _, o, _ = jump.exec_command(full, timeout=60); out = o.read().decode()
    print(f"[deploy]  {remote_name} OK")

    jump.exec_command(f"rm -f {tmp}")
sftp.close()
jump.close()

# Verificar HTTPS
print("\n[verify] HTTPS publico:")
import urllib.request
ua = "Mozilla/5.0 Chrome/120"
for _, name, _ in FILES:
    url = f"https://goxtech.com.ar/{name}"
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua}), timeout=10)
        print(f"  HTTP {r.status} · {url} · {len(r.read())} bytes")
    except Exception as e:
        print(f"  ERR · {url} · {e}")
