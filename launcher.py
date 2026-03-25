"""
Launcher de escritorio — Factusol ARCA Sync
Ejecuta FastAPI en background y abre PyWebView como ventana nativa.

Multi-instancia: cada carpeta con su config.json = una empresa diferente.
"""
import sys
import os
import threading
import time
import logging
import traceback

# ---------- Log a archivo para diagnóstico ----------
LOG_FILE = "arca_debug.log"


def setup_logging():
    """Configura logging a archivo para poder diagnosticar errores en producción."""
    log_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else ".", LOG_FILE)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("arca-launcher")


# ---------- Frozen exe: fijar directorio de trabajo ----------
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))
    sys.path.insert(0, os.path.dirname(sys.executable))
    # CRITICAL: con console=False, sys.stdout y sys.stderr son None.
    # Uvicorn y otros loggers crashean al llamar .isatty() sobre None.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")

logger = setup_logging()


def start_server(host: str, port: int):
    """Inicia el servidor FastAPI con uvicorn."""
    try:
        import uvicorn
        from app.main import app as fastapi_app  # import directo, más robusto en frozen
        uvicorn.run(fastapi_app, host=host, port=port, log_level="info")
    except Exception:
        logger.exception("Error fatal al iniciar el servidor")


def wait_for_server(host: str, port: int, timeout: int = 30):
    """Espera a que el servidor esté disponible."""
    import socket

    for _ in range(timeout * 10):
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
    return False


def main():
    logger.info("=" * 50)
    logger.info("Factusol ARCA Sync - Iniciando...")
    logger.info(f"Frozen: {getattr(sys, 'frozen', False)}")
    logger.info(f"CWD: {os.getcwd()}")
    logger.info(f"Executable: {sys.executable}")
    logger.info("=" * 50)

    # Leer config
    try:
        from app.config import get_config
        config = get_config()
        host = config.get("app", {}).get("host", "127.0.0.1")
        port = config.get("app", {}).get("port", 8765)
        empresa = config.get("empresa", {}).get("razon_social", "")
        logger.info(f"Config cargada: host={host}, port={port}, empresa={empresa}")
    except Exception:
        logger.exception("Error leyendo config.json, usando valores por defecto")
        host = "127.0.0.1"
        port = 8765
        empresa = ""

    title = f"Factusol ARCA Sync - {empresa}" if empresa else "Factusol ARCA Sync"
    local_host = "127.0.0.1" if host == "0.0.0.0" else host

    # Iniciar servidor en thread background
    server_thread = threading.Thread(
        target=start_server,
        args=(host, port),
        daemon=True,
    )
    server_thread.start()

    logger.info(f"⏳ Esperando servidor en {local_host}:{port}...")
    if not wait_for_server(local_host, port):
        logger.error("❌ El servidor no arrancó a tiempo (30s timeout)")
        # Mantener abierto para leer log si hay consola
        if not getattr(sys, "frozen", False):
            sys.exit(1)
        # En frozen sin consola, intentar mostrar el error
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                "El servidor no pudo iniciarse.\n\nRevise el archivo arca_debug.log para más detalles.",
                "Factusol ARCA Sync - Error",
                0x10,  # MB_ICONERROR
            )
        except Exception:
            pass
        sys.exit(1)

    logger.info("✅ Servidor listo — abriendo ventana")

    # Abrir ventana con PyWebView
    url = f"http://{local_host}:{port}"
    try:
        import webview
        logger.info(f"Usando PyWebView para abrir: {url}")
        window = webview.create_window(
            title,
            url,
            width=1280,
            height=800,
            min_size=(900, 600),
            resizable=True,
            text_select=True,
        )
        webview.start()
        logger.info("Ventana cerrada — saliendo")
    except ImportError:
        logger.warning("PyWebView no disponible, abriendo en navegador")
        _open_in_browser(url, host, port)
    except Exception:
        logger.exception("Error con PyWebView, intentando navegador")
        _open_in_browser(url, host, port)


def _open_in_browser(url: str, host: str, port: int):
    """Fallback: abrir en Chrome modo app o navegador por defecto."""
    import subprocess
    import webbrowser

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    chrome = next((p for p in chrome_paths if os.path.exists(p)), None)

    if chrome:
        logger.info(f"Abriendo Chrome en modo app: {url}")
        subprocess.Popen([chrome, f"--app={url}", "--window-size=1280,800", "--no-first-run"])
    else:
        logger.info(f"Abriendo navegador por defecto: {url}")
        webbrowser.open(url)

    print(f"🌐 Abierto en navegador: http://{host}:{port}")
    print("Presione Ctrl+C para detener...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Error fatal no capturado")
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Error fatal:\n\n{traceback.format_exc()}\n\nRevise arca_debug.log",
                "Factusol ARCA Sync - Error",
                0x10,
            )
        except Exception:
            pass
        sys.exit(1)
