"""Upload ARCA ZIP to Hestia server via SFTP with password auth."""
import paramiko
import sys
import os

HOST = "100.109.105.56"  # Tailscale IP del server HestiaCP
USER = "root"
PASS = "254136b+"
LOCAL_FILE = os.path.join(os.path.dirname(__file__), "dist", "ARCA_v1.5.1.zip")

# Find the web directory on the server
WEB_DIRS = [
    f"/home/{USER}/web/goxtech.com.ar/public_html/downloads/",
    f"/home/{USER}/web/goxtech.com.ar/public_html/descargas/",
    f"/home/{USER}/web/goxtech.com.ar/public_html/",
    f"/home/{USER}/web/",
]


def main():
    if not os.path.exists(LOCAL_FILE):
        print(f"ERROR: No se encuentra {LOCAL_FILE}")
        sys.exit(1)

    print(f"Conectando a {HOST} como {USER}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=10)
    print("Conectado.")

    # Find web directory
    sftp = ssh.open_sftp()

    # List what's under /home/admin/web/
    remote_dir = None
    try:
        stdin, stdout, stderr = ssh.exec_command(f"find /home/{USER}/web/ -name '*.zip' -o -name 'ARCA*' 2>/dev/null | head -20")
        existing = stdout.read().decode().strip()
        print(f"Archivos ARCA existentes:\n{existing}")
    except:
        pass

    try:
        stdin, stdout, stderr = ssh.exec_command(f"ls -la /home/{USER}/web/ 2>/dev/null")
        web_listing = stdout.read().decode().strip()
        print(f"\nContenido de /home/{USER}/web/:\n{web_listing}")
    except:
        pass

    # Try each possible directory
    for d in WEB_DIRS:
        try:
            sftp.stat(d)
            remote_dir = d
            print(f"\nDirectorio encontrado: {d}")
            break
        except FileNotFoundError:
            continue

    if not remote_dir:
        # List all domains
        try:
            stdin, stdout, stderr = ssh.exec_command(f"ls /home/{USER}/web/")
            domains = stdout.read().decode().strip()
            print(f"\nDominios disponibles:\n{domains}")
        except:
            pass
        print("No se encontro directorio de descargas. Revisá la salida de arriba.")
        sftp.close()
        ssh.close()
        sys.exit(1)

    remote_path = os.path.join(remote_dir, "ARCA_v1.5.1.zip").replace("\\", "/")
    file_size = os.path.getsize(LOCAL_FILE)
    print(f"\nSubiendo {LOCAL_FILE} ({file_size // 1024 // 1024} MB) a {remote_path}...")

    sftp.put(LOCAL_FILE, remote_path)
    print("Upload completado.")

    # Verify
    remote_stat = sftp.stat(remote_path)
    print(f"Verificacion: {remote_path} — {remote_stat.st_size} bytes")

    sftp.close()
    ssh.close()
    print("Listo!")


if __name__ == "__main__":
    main()
