"""
Generador de slides para carruseles de Instagram - ARCA Sync.

Toma un YAML/JSON con la definición de cada carrusel (titulo, bullets, visual)
y produce slide_01.jpg ... slide_NN.jpg listos para subir a Google Drive.

Uso:
    python generador_slides.py --carrusel 1
    python generador_slides.py --todos
    python generador_slides.py --carrusel 3 --salida ./out

Dependencias:
    pip install pillow pyyaml

Carga los textos desde marketing/plantillas/carrusel_NN.yaml (uno por carrusel).
Si no existe, usa los defaults definidos abajo.
"""
from __future__ import annotations

import argparse
import json
import os
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# --- Configuración visual ---
WIDTH = 1080
HEIGHT = 1350  # formato 4:5 recomendado por IG
PADDING = 80

COLOR_PRIMARIO = "#0D47A1"
COLOR_ACENTO = "#FFC107"
COLOR_FONDO = "#FFFFFF"
COLOR_TEXTO = "#1A1A1A"
COLOR_TEXTO_INVERSO = "#FFFFFF"
COLOR_GRIS = "#666666"

# El script intenta usar Inter/Montserrat. Si no están, cae a la default de PIL.
FUENTES_CANDIDATAS = [
    "/usr/share/fonts/truetype/inter/Inter-Bold.ttf",
    "/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]
FUENTES_REGULAR = [
    "/usr/share/fonts/truetype/inter/Inter-Regular.ttf",
    "/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
]


BASE_DIR = Path(__file__).resolve().parent
PLANTILLAS_DIR = BASE_DIR / "plantillas"
SALIDA_DIR_DEFAULT = BASE_DIR / "salida"
ASSETS_DIR = BASE_DIR / "assets"


def cargar_fuente(tamano: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidatas = FUENTES_CANDIDATAS if bold else FUENTES_REGULAR
    for ruta in candidatas:
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, tamano)
    return ImageFont.load_default()


def wrap_texto(texto: str, fuente: ImageFont.FreeTypeFont, max_ancho: int) -> list[str]:
    palabras = texto.split()
    lineas: list[str] = []
    actual = ""
    for palabra in palabras:
        prueba = (actual + " " + palabra).strip()
        bbox = fuente.getbbox(prueba)
        if bbox[2] - bbox[0] <= max_ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def dibujar_marca(draw: ImageDraw.ImageDraw, base: Image.Image, slide_num: int, total: int):
    # Logo / marca de agua abajo
    fuente_marca = cargar_fuente(28, bold=True)
    draw.text((PADDING, HEIGHT - 70), "ARCA Sync · GoxTech", fill=COLOR_PRIMARIO, font=fuente_marca)

    fuente_handle = cargar_fuente(24, bold=False)
    handle = "@goxtech.ar"
    bbox = fuente_handle.getbbox(handle)
    ancho_handle = bbox[2] - bbox[0]
    draw.text((WIDTH - PADDING - ancho_handle, HEIGHT - 65), handle, fill=COLOR_GRIS, font=fuente_handle)

    # Indicador slide N / total
    indicador = f"{slide_num:02d} / {total:02d}"
    fuente_ind = cargar_fuente(22, bold=True)
    bbox = fuente_ind.getbbox(indicador)
    ancho_ind = bbox[2] - bbox[0]
    draw.rectangle(
        (WIDTH - PADDING - ancho_ind - 24, 30, WIDTH - PADDING + 4, 70),
        fill=COLOR_PRIMARIO,
    )
    draw.text(
        (WIDTH - PADDING - ancho_ind - 12, 36),
        indicador,
        fill=COLOR_TEXTO_INVERSO,
        font=fuente_ind,
    )


def slide_hook(titulo: str, subtitulo: str, slide_num: int, total: int) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_PRIMARIO)
    draw = ImageDraw.Draw(img)

    # Acento amarillo arriba
    draw.rectangle((0, 0, WIDTH, 12), fill=COLOR_ACENTO)

    fuente_titulo = cargar_fuente(78, bold=True)
    lineas = wrap_texto(titulo, fuente_titulo, WIDTH - 2 * PADDING)
    y = HEIGHT // 2 - (len(lineas) * 90) // 2
    for linea in lineas:
        bbox = fuente_titulo.getbbox(linea)
        ancho = bbox[2] - bbox[0]
        draw.text(((WIDTH - ancho) // 2, y), linea, fill=COLOR_TEXTO_INVERSO, font=fuente_titulo)
        y += 95

    if subtitulo:
        fuente_sub = cargar_fuente(36, bold=False)
        lineas_sub = wrap_texto(subtitulo, fuente_sub, WIDTH - 2 * PADDING)
        y += 30
        for linea in lineas_sub:
            bbox = fuente_sub.getbbox(linea)
            ancho = bbox[2] - bbox[0]
            draw.text(((WIDTH - ancho) // 2, y), linea, fill=COLOR_ACENTO, font=fuente_sub)
            y += 48

    # Reemplazo de la marca con colores invertidos
    fuente_marca = cargar_fuente(28, bold=True)
    draw.text((PADDING, HEIGHT - 70), "ARCA Sync · GoxTech", fill=COLOR_ACENTO, font=fuente_marca)
    fuente_handle = cargar_fuente(24, bold=False)
    handle = "@goxtech.ar  →  desliza"
    bbox = fuente_handle.getbbox(handle)
    ancho_handle = bbox[2] - bbox[0]
    draw.text((WIDTH - PADDING - ancho_handle, HEIGHT - 65), handle, fill=COLOR_TEXTO_INVERSO, font=fuente_handle)

    indicador = f"{slide_num:02d} / {total:02d}"
    fuente_ind = cargar_fuente(22, bold=True)
    bbox = fuente_ind.getbbox(indicador)
    ancho_ind = bbox[2] - bbox[0]
    draw.rectangle((WIDTH - PADDING - ancho_ind - 24, 30, WIDTH - PADDING + 4, 70), fill=COLOR_ACENTO)
    draw.text((WIDTH - PADDING - ancho_ind - 12, 36), indicador, fill=COLOR_PRIMARIO, font=fuente_ind)

    return img


def slide_contenido(titulo: str, bullets: list[str], slide_num: int, total: int) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_FONDO)
    draw = ImageDraw.Draw(img)

    # Barra de título
    draw.rectangle((0, 0, 12, HEIGHT), fill=COLOR_PRIMARIO)

    fuente_titulo = cargar_fuente(56, bold=True)
    lineas_titulo = wrap_texto(titulo, fuente_titulo, WIDTH - 2 * PADDING)
    y = 140
    for linea in lineas_titulo:
        draw.text((PADDING, y), linea, fill=COLOR_PRIMARIO, font=fuente_titulo)
        y += 70

    # Separador
    y += 20
    draw.rectangle((PADDING, y, PADDING + 100, y + 6), fill=COLOR_ACENTO)
    y += 50

    fuente_bullet = cargar_fuente(40, bold=False)
    for bullet in bullets:
        lineas = wrap_texto(bullet, fuente_bullet, WIDTH - 2 * PADDING - 50)
        for i, linea in enumerate(lineas):
            prefijo = "•  " if i == 0 else "    "
            draw.text((PADDING, y), prefijo + linea, fill=COLOR_TEXTO, font=fuente_bullet)
            y += 56
        y += 16

    dibujar_marca(draw, img, slide_num, total)
    return img


def slide_numero_gigante(numero: str, etiqueta: str, slide_num: int, total: int) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_PRIMARIO)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH, 12), fill=COLOR_ACENTO)

    fuente_num = cargar_fuente(280, bold=True)
    bbox = fuente_num.getbbox(numero)
    ancho = bbox[2] - bbox[0]
    alto = bbox[3] - bbox[1]
    draw.text(((WIDTH - ancho) // 2, (HEIGHT - alto) // 2 - 80), numero, fill=COLOR_ACENTO, font=fuente_num)

    fuente_etiqueta = cargar_fuente(44, bold=True)
    lineas = wrap_texto(etiqueta, fuente_etiqueta, WIDTH - 2 * PADDING)
    y = HEIGHT // 2 + 180
    for linea in lineas:
        bbox = fuente_etiqueta.getbbox(linea)
        ancho_l = bbox[2] - bbox[0]
        draw.text(((WIDTH - ancho_l) // 2, y), linea, fill=COLOR_TEXTO_INVERSO, font=fuente_etiqueta)
        y += 58

    fuente_marca = cargar_fuente(28, bold=True)
    draw.text((PADDING, HEIGHT - 70), "ARCA Sync · GoxTech", fill=COLOR_ACENTO, font=fuente_marca)
    return img


def slide_cta(titulo: str, lineas_cta: list[str], slide_num: int, total: int) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_FONDO)
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, WIDTH, 200), fill=COLOR_PRIMARIO)
    fuente_titulo = cargar_fuente(62, bold=True)
    lineas_t = wrap_texto(titulo, fuente_titulo, WIDTH - 2 * PADDING)
    y = 60
    for linea in lineas_t:
        bbox = fuente_titulo.getbbox(linea)
        ancho = bbox[2] - bbox[0]
        draw.text(((WIDTH - ancho) // 2, y), linea, fill=COLOR_TEXTO_INVERSO, font=fuente_titulo)
        y += 72

    fuente_cta = cargar_fuente(42, bold=True)
    y = 350
    for linea in lineas_cta:
        lineas_w = wrap_texto(linea, fuente_cta, WIDTH - 2 * PADDING)
        for sub in lineas_w:
            bbox = fuente_cta.getbbox(sub)
            ancho = bbox[2] - bbox[0]
            draw.text(((WIDTH - ancho) // 2, y), sub, fill=COLOR_TEXTO, font=fuente_cta)
            y += 60
        y += 20

    # Pegar QR si existe
    qr_path = ASSETS_DIR / "qr_whatsapp.png"
    if qr_path.exists():
        qr = Image.open(qr_path).convert("RGBA")
        qr.thumbnail((360, 360))
        img.paste(qr, ((WIDTH - qr.width) // 2, HEIGHT - 480), qr)

    dibujar_marca(draw, img, slide_num, total)
    return img


def renderizar_slide(definicion: dict, slide_num: int, total: int) -> Image.Image:
    tipo = definicion.get("tipo", "contenido")
    if tipo == "hook":
        return slide_hook(definicion["titulo"], definicion.get("subtitulo", ""), slide_num, total)
    if tipo == "numero":
        return slide_numero_gigante(definicion["numero"], definicion.get("etiqueta", ""), slide_num, total)
    if tipo == "cta":
        return slide_cta(definicion["titulo"], definicion.get("lineas", []), slide_num, total)
    return slide_contenido(definicion["titulo"], definicion.get("bullets", []), slide_num, total)


def cargar_definicion_carrusel(numero: int) -> dict:
    yaml_path = PLANTILLAS_DIR / f"carrusel_{numero:02d}.yaml"
    json_path = PLANTILLAS_DIR / f"carrusel_{numero:02d}.json"
    if yaml_path.exists():
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise SystemExit("Falta dependencia: pip install pyyaml") from exc
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError(f"No se encontró {yaml_path} ni {json_path}")


def generar_carrusel(numero: int, salida_dir: Path) -> Path:
    definicion = cargar_definicion_carrusel(numero)
    slides = definicion["slides"]
    total = len(slides)

    nombre_carpeta = f"carrusel_{numero:02d}_{definicion['slug']}"
    out = salida_dir / nombre_carpeta
    out.mkdir(parents=True, exist_ok=True)

    for i, slide_def in enumerate(slides, start=1):
        img = renderizar_slide(slide_def, i, total)
        archivo = out / f"slide_{i:02d}.jpg"
        img.save(archivo, "JPEG", quality=92, optimize=True)
        print(f"  ✓ {archivo.name}")

    caption_path = out / "caption.txt"
    caption_path.write_text(definicion.get("caption", "") + "\n\n" + definicion.get("hashtags", ""), encoding="utf-8")

    meta = {
        "nombre": nombre_carpeta,
        "titulo": definicion.get("titulo", ""),
        "fecha_publicacion": definicion.get("fecha_publicacion", ""),
        "hora": definicion.get("hora", "10:00"),
        "status": "pendiente",
    }
    meta_path = out / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"✅ Carrusel {numero:02d} generado en {out}")
    return out


def main():
    parser = argparse.ArgumentParser(description="Generador de slides para carruseles de IG")
    parser.add_argument("--carrusel", type=int, help="Número de carrusel (1-8)")
    parser.add_argument("--todos", action="store_true", help="Genera los 8 carruseles")
    parser.add_argument("--salida", type=Path, default=SALIDA_DIR_DEFAULT, help="Directorio de salida")
    args = parser.parse_args()

    args.salida.mkdir(parents=True, exist_ok=True)

    if args.todos:
        for n in range(1, 9):
            try:
                generar_carrusel(n, args.salida)
            except FileNotFoundError as e:
                print(f"⚠️  Carrusel {n}: {e}")
    elif args.carrusel:
        generar_carrusel(args.carrusel, args.salida)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
