"""
Launcher de escritorio — Factusol Módulo ARCA
Ejecuta FastAPI en background y abre PyWebView como ventana nativa.

Multi-instancia: cada carpeta con su config.json = una empresa diferente.
"""
import sys
import os
import threading
import time

# Asegurar que el directorio del exe esté en el path
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))
    sys.path.insert(0, os.path.dirname(sys.executable))


def start_server(host: str, port: int):
    """Inicia el servidor FastAPI con uvicorn."""
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level="info",
    )


def wait_for_server(host: str, port: int, timeout: int = 30):
    """Espera a que el servidor esté disponible."""
    import urllib.request
    import urllib.error

    url = f"http://{host}:{port}/"
    for _ in range(timeout * 10):
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            time.sleep(0.1)
    return False


def main():
    # Leer puerto de config (si existe)
    try:
        from app.config import get_config
        config = get_config()
        host = config.get("app", {}).get("host", "127.0.0.1")
        port = config.get("app", {}).get("port", 8765)
        empresa = config.get("empresa", {}).get("razon_social", "")
    except Exception:
        host = "127.0.0.1"
        port = 8765
        empresa = ""

    title = f"ARCA - {empresa}" if empresa else "Factusol Módulo ARCA"

    # URL local (siempre 127.0.0.1 para acceso)
    local_host = "127.0.0.1" if host == "0.0.0.0" else host

    # Iniciar servidor en thread background
    server_thread = threading.Thread(
        target=start_server,
        args=(host, port),
        daemon=True,
    )
    server_thread.start()

    # Esperar que el servidor arranque
    print(f"⏳ Esperando servidor en {local_host}:{port}...")
    if not wait_for_server(local_host, port):
        print("❌ El servidor no arrancó a tiempo")
        sys.exit(1)

    print(f"✅ Servidor listo — abriendo ventana")

    # Abrir ventana con PyWebView
    try:
        import webview
        window = webview.create_window(
            title,
            f"http://{local_host}:{port}",
            width=1280,
            height=800,
            min_size=(900, 600),
            resizable=True,
            text_select=True,
        )
        webview.start()
    except ImportError:
        # Si no hay webview, abrir en navegador
        import webbrowser
        webbrowser.open(f"http://{host}:{port}")
        print(f"🌐 Abierto en navegador: http://{host}:{port}")
        print("Presione Ctrl+C para detener...")
        try:
            server_thread.join()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
