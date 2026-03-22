"""
Punto de entrada - Módulo ARCA para Factusol
Facturación Electrónica AFIP/ARCA

Uso:
    python main.py            → Abre interfaz gráfica
    python main.py --cli      → Modo CLI interactivo
    python main.py --check    → Verifica configuración y conexión AFIP
"""
import sys
import logging
import argparse

# ── Configurar logging antes de importar módulos ──────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("arca")


def main():
    parser = argparse.ArgumentParser(
        description="ARCA - Módulo de Facturación Electrónica AFIP para Factusol"
    )
    parser.add_argument("--cli",   action="store_true", help="Modo CLI interactivo")
    parser.add_argument("--check", action="store_true", help="Verificar configuración y AFIP")
    parser.add_argument("--pendientes", action="store_true", help="Listar facturas pendientes de CAE")
    args = parser.parse_args()

    if args.check:
        _check_config()
    elif args.pendientes:
        _listar_pendientes()
    elif args.cli:
        _modo_cli()
    else:
        _modo_gui()


# ──────────────────────────────────────────────────────────────────────────────
# Verificación de configuración
# ──────────────────────────────────────────────────────────────────────────────

def _check_config():
    """Verifica la configuración y la conexión con AFIP."""
    import config
    from pathlib import Path

    print("\n══════════════════════════════════════════")
    print("  ARCA - Verificación de Configuración")
    print("══════════════════════════════════════════\n")

    ok = True

    # CUIT
    if config.AFIP_CUIT:
        print(f"  ✓  CUIT emisor    : {config.AFIP_CUIT}")
    else:
        print("  ✗  CUIT emisor    : NO CONFIGURADO (AFIP_CUIT)")
        ok = False

    # Entorno
    print(f"  ✓  Entorno AFIP   : {config.AFIP_ENV.upper()}")

    # Certificado
    cert = Path(config.AFIP_CERT)
    if cert.exists():
        print(f"  ✓  Certificado    : {cert}")
    else:
        print(f"  ✗  Certificado    : NO ENCONTRADO → {cert}")
        ok = False

    # Clave privada
    key = Path(config.AFIP_KEY)
    if key.exists():
        print(f"  ✓  Clave privada  : {key}")
    else:
        print(f"  ✗  Clave privada  : NO ENCONTRADA → {key}")
        ok = False

    # BD Factusol
    from pathlib import Path as P
    mdb = P(config.FACTUSOL_MDB)
    if mdb.exists():
        print(f"  ✓  BD Factusol    : {mdb}")
    else:
        print(f"  ⚠  BD Factusol    : No encontrada en {mdb} (puede estar en red)")

    # Rango fechas
    from afip.fecha_cbte import describir_rango_valido
    print(f"\n  {describir_rango_valido()}")

    if not ok:
        print("\n  ✗  Hay errores de configuración. Revise el archivo .env\n")
        sys.exit(1)

    # Conexión AFIP
    print("\n  Verificando conexión con AFIP...")
    try:
        from motor_cae import MotorCAE
        motor = MotorCAE(config.FACTUSOL_MDB)
        ok_afip, msg = motor.verificar_conexion_afip()
        if ok_afip:
            print(f"  ✓  AFIP WSFE      : {msg}")
        else:
            print(f"  ✗  AFIP WSFE      : {msg}")
    except Exception as e:
        print(f"  ✗  Error AFIP      : {e}")

    print("\n══════════════════════════════════════════\n")


# ──────────────────────────────────────────────────────────────────────────────
# Modo CLI
# ──────────────────────────────────────────────────────────────────────────────

def _listar_pendientes():
    """Lista las facturas pendientes de CAE desde CLI."""
    import config
    from factusol.db import FactusolDB, FactusolDBError
    from tabulate import tabulate

    try:
        with FactusolDB(config.FACTUSOL_MDB) as db:
            facturas = db.obtener_facturas_pendientes()
    except FactusolDBError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not facturas:
        print("No hay facturas pendientes de CAE.")
        return

    rows = [
        [f.id_factura, f.tipo, f.numero, f.fecha, f.nombre_receptor, f.cuit_receptor,
         f"${f.imp_total:,.2f}"]
        for f in facturas
    ]
    print(tabulate(rows, headers=["ID", "Tipo", "Número", "Fecha", "Receptor", "CUIT", "Total"]))
    print(f"\nTotal: {len(facturas)} factura(s) pendientes de CAE")


def _modo_cli():
    """Modo interactivo CLI."""
    import config
    from factusol.db import FactusolDB, FactusolDBError
    from motor_cae import MotorCAE
    from colorama import Fore, Style, init
    init(autoreset=True)

    print(f"\n{Fore.CYAN}══════════════════════════════════════════")
    print(f"  ARCA - Facturación Electrónica AFIP/ARCA")
    print(f"  Modo CLI | Entorno: {config.AFIP_ENV.upper()}")
    print(f"══════════════════════════════════════════{Style.RESET_ALL}\n")

    while True:
        print(f"\n{Fore.WHITE}Opciones:")
        print("  1. Listar facturas pendientes de CAE")
        print("  2. Procesar UNA factura por ID")
        print("  3. Procesar TODAS las pendientes")
        print("  4. Verificar conexión AFIP")
        print("  0. Salir")
        opcion = input("\n> ").strip()

        if opcion == "0":
            print("Hasta luego.")
            break

        elif opcion == "1":
            _listar_pendientes()

        elif opcion == "2":
            id_str = input("ID de factura: ").strip()
            try:
                id_fac = int(id_str)
            except ValueError:
                print(f"{Fore.RED}ID inválido")
                continue
            try:
                with FactusolDB(config.FACTUSOL_MDB) as db:
                    factura = db.obtener_factura_por_id(id_fac)
                if not factura:
                    print(f"{Fore.RED}Factura {id_fac} no encontrada")
                    continue
                print(f"\nProcesando: {factura}")
                motor = MotorCAE(config.FACTUSOL_MDB)
                res   = motor.procesar_factura(factura)
                if res.exitoso:
                    print(f"{Fore.GREEN}✓ CAE: {res.cae} | Vto: {res.cae_fecha_vto}")
                    for adv in res.advertencias:
                        print(f"{Fore.YELLOW}  ⚠ {adv}")
                else:
                    print(f"{Fore.RED}✗ FALLO [{res.etapa_fallo}]: {'; '.join(res.errores)}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}")

        elif opcion == "3":
            try:
                with FactusolDB(config.FACTUSOL_MDB) as db:
                    facturas = db.obtener_facturas_pendientes()
            except Exception as e:
                print(f"{Fore.RED}Error: {e}")
                continue

            if not facturas:
                print("No hay facturas pendientes.")
                continue

            confirmar = input(f"¿Procesar {len(facturas)} factura(s)? (s/n): ").strip().lower()
            if confirmar != "s":
                continue

            motor = MotorCAE(config.FACTUSOL_MDB)
            aprobadas = rechazadas = 0
            for factura in facturas:
                try:
                    res = motor.procesar_factura(factura)
                    if res.exitoso:
                        aprobadas += 1
                        print(f"{Fore.GREEN}✓ {factura.numero} → {res.cae}")
                        for adv in res.advertencias:
                            print(f"{Fore.YELLOW}  ⚠ {adv}")
                    else:
                        rechazadas += 1
                        print(f"{Fore.RED}✗ {factura.numero} → {'; '.join(res.errores)}")
                except Exception as e:
                    rechazadas += 1
                    print(f"{Fore.RED}✗ {factura.numero} → Error: {e}")

            print(f"\n{Fore.CYAN}Resultado: {aprobadas} aprobadas, {rechazadas} rechazadas")

        elif opcion == "4":
            try:
                motor = MotorCAE(config.FACTUSOL_MDB)
                ok, msg = motor.verificar_conexion_afip()
                color = Fore.GREEN if ok else Fore.RED
                print(f"{color}{msg}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Modo GUI (por defecto)
# ──────────────────────────────────────────────────────────────────────────────

def _modo_gui():
    try:
        from gui.app import AppARCA
    except ImportError as e:
        log.error("No se pudo cargar la GUI: %s", e)
        print("Error: tkinter no disponible o falta dependencia.")
        print("Use: python main.py --cli")
        sys.exit(1)

    app = AppARCA()
    app.mainloop()


if __name__ == "__main__":
    main()
