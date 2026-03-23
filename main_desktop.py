"""
Factusol Módulo ARCA — Desktop Entry Point
Inicia el servidor FastAPI y abre la UI en una ventana nativa de Windows.
"""
import sys
import threading
import time
import socket
import webbrowser
import os
import subprocess

PORT = 8765  # Puerto distinto al dev para no conflictuar


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_for_server(port, timeout=15):
    """Espera hasta que el servidor esté listo."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def start_server(port):
    import uvicorn
    from app.main import app as fastapi_app
    uvicorn.run(fastapi_app, host="127.0.0.1", port=port, log_level="warning")


def main():
    port = PORT

    # Iniciar FastAPI en thread daemon
    server_thread = threading.Thread(
        target=start_server,
        args=(port,),
        daemon=True,
    )
    server_thread.start()

    url = f"http://127.0.0.1:{port}"

    # Intentar usar pywebview (ventana nativa)
    try:
        import webview
        if not wait_for_server(port):
            raise RuntimeError("Server timeout")
        window = webview.create_window(
            "Factusol ARCA",
            url,
            width=1280,
            height=800,
            min_size=(800, 600),
        )
        webview.start()
    except Exception:
        # Fallback: abrir en el browser por defecto en modo app
        if not wait_for_server(port):
            print("Error: el servidor no pudo iniciarse")
            sys.exit(1)
        # Intentar Chrome en modo --app para que parezca app de escritorio
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        chrome = next((p for p in chrome_paths if os.path.exists(p)), None)
        if chrome:
            subprocess.Popen([
                chrome,
                f"--app={url}",
                f"--window-size=1280,800",
                "--no-first-run",
            ])
        else:
            webbrowser.open(url)

        # Mantener el proceso vivo mientras el servidor corre
        try:
            server_thread.join()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
