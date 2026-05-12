"""
Re-inyecta el bloque <section id="arca-cta">...</section> en la home publica
(goxtech.com.ar/index.html) con el contenido actualizado del snippet local.

Si el bloque ya existe, lo reemplaza. Si no existe, lo inserta antes del
cierre </body>.
"""
import os
import re
import sys
import paramiko
from datetime import datetime

JUMP_HOST = os.environ.get("ARCA_JUMP_HOST", "192.168.1.201")
JUMP_USER = os.environ.get("ARCA_JUMP_USER", "root")
JUMP_PASS = os.environ.get("ARCA_JUMP_PASS", "254136b+")

DEST_HOST = os.environ.get("ARCA_DEST_HOST", "192.168.1.212")
DEST_USER = os.environ.get("ARCA_DEST_USER", "admin")
DEST_PASS = os.environ.get("ARCA_DEST_PASS", "Goxtech2026!")

REMOTE_FILE = "/home/goxtechcomar/web/goxtech.com.ar/public_html/index.html"
LOCAL_SNIPPET = os.path.join(os.path.dirname(__file__), "web_register", "home_cta_snippet.html")


def run_remote(jump, cmd):
    """Ejecuta cmd via ssh+sudo en el destino, devuelve stdout."""
    full = (
        f"sshpass -p '{DEST_PASS}' ssh -o StrictHostKeyChecking=no "
        f"{DEST_USER}@{DEST_HOST} \"echo {DEST_PASS} | sudo -S bash -c \\\"{cmd}\\\" 2>&1\""
    )
    _, o, _ = jump.exec_command(full, timeout=60)
    return o.read().decode()


def main():
    if not os.path.exists(LOCAL_SNIPPET):
        print(f"ERROR: no se encuentra {LOCAL_SNIPPET}")
        sys.exit(1)

    snippet = open(LOCAL_SNIPPET, "r", encoding="utf-8").read().strip()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    print("=" * 70)
    print("  Re-inyectar home CTA")
    print("=" * 70)
    print(f"  Snippet local: {LOCAL_SNIPPET} ({len(snippet)} bytes)")
    print(f"  Destino:       {REMOTE_FILE}")
    print(f"  Backup:        {REMOTE_FILE}.bak.{ts}")
    print("=" * 70)

    print(f"\n[1/4] Conectando al jump {JUMP_USER}@{JUMP_HOST}...")
    jump = paramiko.SSHClient()
    jump.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jump.connect(JUMP_HOST, username=JUMP_USER, password=JUMP_PASS, timeout=15)
    print("      OK")

    # Bajar el index.html actual del destino via scp -> jump -> SFTP a local
    print(f"[2/4] Descargando index.html actual...")
    scp_pull = (
        f"sshpass -p '{DEST_PASS}' scp -O -o StrictHostKeyChecking=no "
        f"{DEST_USER}@{DEST_HOST}:{REMOTE_FILE} /tmp/_home_index_{ts}.html 2>&1"
    )
    _, o, _ = jump.exec_command(scp_pull, timeout=60)
    print("      " + (o.read().decode().strip() or "OK"))

    sftp = jump.open_sftp()
    local_tmp = os.path.join(os.path.dirname(__file__), f"_home_index_{ts}.html")
    sftp.get(f"/tmp/_home_index_{ts}.html", local_tmp)
    sftp.close()
    print(f"      Local: {local_tmp}")

    # Cargar HTML y reemplazar el bloque
    html = open(local_tmp, "r", encoding="utf-8").read()
    original_len = len(html)

    pat = re.compile(
        r'<section id="arca-cta".*?</section>',
        re.DOTALL,
    )
    if pat.search(html):
        html_new = pat.sub(lambda _m: snippet, html, count=1)
        action = "REEMPLAZADO"
    else:
        # Insertar antes de </body>
        if "</body>" in html:
            html_new = html.replace("</body>", snippet + "\n</body>", 1)
            action = "INSERTADO (antes de </body>)"
        else:
            html_new = html + "\n" + snippet + "\n"
            action = "APENDIDO"

    print(f"[3/4] HTML procesado: {action}")
    print(f"      Antes: {original_len:,} bytes · Despues: {len(html_new):,} bytes")

    out_local = os.path.join(os.path.dirname(__file__), f"_home_index_new_{ts}.html")
    with open(out_local, "w", encoding="utf-8") as f:
        f.write(html_new)

    # Subir el nuevo al jump y de ahi al destino con backup
    print(f"[4/4] Subiendo index.html nuevo al destino...")
    sftp = jump.open_sftp()
    sftp.put(out_local, f"/tmp/_home_index_new_{ts}.html")
    sftp.close()

    scp_push = (
        f"sshpass -p '{DEST_PASS}' scp -O -o StrictHostKeyChecking=no "
        f"/tmp/_home_index_new_{ts}.html {DEST_USER}@{DEST_HOST}:/tmp/ 2>&1"
    )
    _, o, _ = jump.exec_command(scp_push, timeout=60)
    print("      scp: " + (o.read().decode().strip() or "OK"))

    sudo_bash = (
        f"cp {REMOTE_FILE} {REMOTE_FILE}.bak.{ts} && "
        f"cp /tmp/_home_index_new_{ts}.html {REMOTE_FILE} && "
        f"chown goxtechcomar:goxtechcomar {REMOTE_FILE} && "
        f"chmod 644 {REMOTE_FILE} && "
        f"rm -f /tmp/_home_index_new_{ts}.html && "
        f"ls -la {REMOTE_FILE}"
    )
    full = (
        f"sshpass -p '{DEST_PASS}' ssh -o StrictHostKeyChecking=no "
        f"{DEST_USER}@{DEST_HOST} \"echo {DEST_PASS} | sudo -S bash -c '{sudo_bash}' 2>&1\""
    )
    _, o, _ = jump.exec_command(full, timeout=60)
    print(o.read().decode())

    # Cleanup
    jump.exec_command(f"rm -f /tmp/_home_index_{ts}.html /tmp/_home_index_new_{ts}.html")
    jump.close()

    # Borrar archivos locales temporales
    try:
        os.remove(local_tmp)
        os.remove(out_local)
    except OSError:
        pass

    print("\n" + "=" * 70)
    print(f"  Re-inyectado OK · https://goxtech.com.ar/")
    print("=" * 70)


if __name__ == "__main__":
    main()
