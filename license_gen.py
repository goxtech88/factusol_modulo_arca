"""
Generador de licencias para Factusol ARCA Sync.
USO INTERNO — Solo para GoxTech.

Genera una clave de licencia basada en el CUIT del cliente.
"""
import hmac
import hashlib
import sys

# Clave secreta (NO compartir con clientes)
LICENSE_SECRET = "GoxTech-ARCA-Sync-2026-SecretKey"


def generate_license(cuit: str) -> str:
    """Genera una clave de licencia para un CUIT dado."""
    cuit_clean = cuit.replace("-", "").replace(" ", "").strip()
    if len(cuit_clean) < 10:
        raise ValueError(f"CUIT inválido: {cuit}")

    # HMAC-SHA256 del CUIT con la clave secreta
    sig = hmac.new(
        LICENSE_SECRET.encode(),
        cuit_clean.encode(),
        hashlib.sha256,
    ).hexdigest().upper()

    # Formato: XXXX-XXXX-XXXX-XXXX (16 chars)
    key = f"{sig[:4]}-{sig[4:8]}-{sig[8:12]}-{sig[12:16]}"
    return key


def verify_license(cuit: str, license_key: str) -> bool:
    """Verifica si una clave de licencia es válida para el CUIT dado."""
    try:
        expected = generate_license(cuit)
        return license_key.strip().upper() == expected.upper()
    except Exception:
        return False


if __name__ == "__main__":
    print("\n" + "=" * 44)
    print("  Factusol ARCA Sync — Generador de Licencias")
    print("=" * 44)

    if len(sys.argv) >= 2:
        cuit = sys.argv[1]
    else:
        cuit = input("\n  Ingrese CUIT del cliente: ").strip()

    if not cuit:
        print("  ❌ CUIT vacío")
        input("\n  Presione Enter para salir...")
        sys.exit(1)

    try:
        key = generate_license(cuit)
        cuit_clean = cuit.replace("-", "").replace(" ", "").strip()
        print(f"\n  CUIT:     {cuit}")
        print(f"  Licencia: {key}")
        print("\n" + "=" * 44)
    except Exception as e:
        print(f"  ❌ Error: {e}")

    input("\n  Presione Enter para salir...")
