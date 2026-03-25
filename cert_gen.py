"""
Generador de Clave Privada (.key) y CSR (.csr) para ARCA/AFIP.
Factusol ARCA Sync — GoxTech S.R.L.

Genera los archivos necesarios para tramitar el certificado digital
en el portal de ARCA (ex AFIP).

Proceso:
  1. Este script genera la clave privada (.key) y la solicitud (.csr)
  2. Subir el .csr al portal ARCA → Administración de Certificados
  3. Descargar el certificado firmado (.crt/.pem) desde ARCA
  4. Configurar en la app: cert_path = .crt, key_path = .key
"""
import sys
import os
from datetime import datetime


def generate_key_and_csr(cuit: str, razon_social: str, output_dir: str = "."):
    """Genera clave privada RSA 2048 y CSR para ARCA."""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    cuit_clean = cuit.replace("-", "").replace(" ", "").strip()

    # 1. Generar clave privada RSA 2048
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Construir CSR con datos de ARCA
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "AR"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, razon_social),
        x509.NameAttribute(NameOID.COMMON_NAME, razon_social),
        x509.NameAttribute(NameOID.SERIAL_NUMBER, f"CUIT {cuit_clean}"),
    ])

    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(subject)
        .sign(private_key, hashes.SHA256())
    )

    # 3. Guardar archivos
    os.makedirs(output_dir, exist_ok=True)

    key_filename = f"{cuit_clean}.key"
    csr_filename = f"{cuit_clean}.req"

    key_path = os.path.join(output_dir, key_filename)
    csr_path = os.path.join(output_dir, csr_filename)

    # Guardar clave privada (sin contraseña)
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # Guardar CSR
    with open(csr_path, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))

    return key_path, csr_path


def main():
    print("\n" + "=" * 52)
    print("  Factusol ARCA Sync — Generador de Certificados")
    print("  GoxTech S.R.L.")
    print("=" * 52)

    if len(sys.argv) >= 3:
        cuit = sys.argv[1]
        razon_social = sys.argv[2]
    else:
        cuit = input("\n  CUIT del cliente: ").strip()
        razon_social = input("  Razón Social:     ").strip()

    if not cuit or not razon_social:
        print("\n  ❌ CUIT y Razón Social son obligatorios")
        input("\n  Presione Enter para salir...")
        sys.exit(1)

    cuit_clean = cuit.replace("-", "").replace(" ", "").strip()
    if len(cuit_clean) < 10:
        print(f"\n  ❌ CUIT inválido: {cuit}")
        input("\n  Presione Enter para salir...")
        sys.exit(1)

    # Directorio de salida: carpeta "certs" al lado del exe
    output_dir = os.path.join(os.getcwd(), "certs")

    try:
        key_path, csr_path = generate_key_and_csr(cuit, razon_social, output_dir)

        print(f"\n  ✅ Archivos generados en: {output_dir}")
        print(f"\n  🔑 Clave privada: {os.path.basename(key_path)}")
        print(f"  📄 CSR (solicitud): {os.path.basename(csr_path)}")
        print(f"\n  {'─' * 48}")
        print(f"  Pasos siguientes:")
        print(f"  1. Ir a https://auth.afip.gob.ar/")
        print(f"  2. Administración de Certificados Digitales")
        print(f"  3. Agregar alias y subir el archivo .csr")
        print(f"  4. Asociar al Web Service 'wsfe' (factura electrónica)")
        print(f"  5. Descargar el certificado .crt generado")
        print(f"  6. Configurar en la app:")
        print(f"     cert_path = ruta al .crt descargado")
        print(f"     key_path  = {key_path}")
        print(f"\n  ⚠️  IMPORTANTE: Guardar el .key en lugar seguro.")
        print(f"     Si se pierde, hay que generar todo de nuevo.")
    except ImportError:
        print("\n  ❌ Falta la librería 'cryptography'.")
        print("     Instalar con: pip install cryptography")
    except Exception as e:
        print(f"\n  ❌ Error: {e}")

    print("\n" + "=" * 52)
    input("\n  Presione Enter para salir...")


if __name__ == "__main__":
    main()
