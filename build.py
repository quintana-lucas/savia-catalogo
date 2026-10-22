#!/usr/bin/env python3
"""Genera el catálogo estático en _site/.

Fuente de productos (en orden de prioridad):
  1. La variable de entorno SHEET_CSV_URL (Google Sheets publicada como CSV).
  2. El archivo local data/productos.csv.

Solo usa la biblioteca estándar de Python: no hace falta instalar nada.
"""
import csv
import html
import io
import json
import os
import shutil
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

RAIZ = Path(__file__).parent
SALIDA = RAIZ / "_site"

# Nombres de columna aceptados (sin importar mayúsculas ni tildes).
COLUMNAS = {
    "categoria": "categoria",
    "nombre": "nombre",
    "descripcion": "descripcion",
    "presentacion": "presentacion",
    "precio": "precio",
    "disponible": "disponible",
    "foto": "foto",
}


def normalizar(texto):
    reemplazos = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    return texto.strip().translate(reemplazos).lower()


def leer_csv():
    url = os.environ.get("SHEET_CSV_URL", "").strip()
    if url:
        print(f"Descargando planilla desde {url[:60]}...")
        with urllib.request.urlopen(url, timeout=30) as r:
            texto = r.read().decode("utf-8-sig")
    else:
        print("Usando data/productos.csv")
        texto = (RAIZ / "data" / "productos.csv").read_text(encoding="utf-8-sig")
    return list(csv.DictReader(io.StringIO(texto)))


def parsear_precio(valor):
    limpio = (valor or "").replace("$", "").replace(".", "").replace(",", ".").strip()
    try:
        return round(float(limpio))
    except ValueError:
        return None


def limpiar_filas(filas):
    productos = []
    for fila in filas:
        p = {}
        for clave, valor in fila.items():
            if clave is None:
                continue
            k = COLUMNAS.get(normalizar(clave))
            if k:
                p[k] = (valor or "").strip()
        if not p.get("nombre"):
            continue  # filas vacías o de notas
        p["categoria"] = p.get("categoria") or "Otros"
        p["precio"] = parsear_precio(p.get("precio"))
        p["disponible"] = normalizar(p.get("disponible", "si")) not in ("no", "0", "false", "sin stock", "agotado")
        productos.append(p)
    return productos


WA_SVG = '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.5 0-3-.4-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/>'
IG_SVG = '<path d="M7.5 2h9A5.5 5.5 0 0 1 22 7.5v9a5.5 5.5 0 0 1-5.5 5.5h-9A5.5 5.5 0 0 1 2 16.5v-9A5.5 5.5 0 0 1 7.5 2Zm0 2A3.5 3.5 0 0 0 4 7.5v9A3.5 3.5 0 0 0 7.5 20h9a3.5 3.5 0 0 0 3.5-3.5v-9A3.5 3.5 0 0 0 16.5 4h-9ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Zm5.25-3.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5Z"/>'


def redes(config):
    """Íconos del encabezado: Instagram (si está en config) y WhatsApp."""
    enlaces = []
    if config.get("instagram"):
        enlaces.append((config["instagram"], "Instagram", IG_SVG))
    enlaces.append((f"https://wa.me/{config['whatsapp']}", "WhatsApp", WA_SVG))
    return "".join(
        f'<a href="{html.escape(url)}" target="_blank" rel="noopener" aria-label="{nombre}" title="{nombre}">'
        f'<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{svg}</svg></a>'
        for url, nombre, svg in enlaces
    )


def main():
    config = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
    productos = limpiar_filas(leer_csv())
    if not productos:
        sys.exit("ERROR: la planilla no tiene productos. No se publica nada para no dejar la página vacía.")

    categorias = list(dict.fromkeys(p["categoria"] for p in productos))
    ahora = datetime.now(timezone(timedelta(hours=-3)))

    plantilla = (RAIZ / "plantilla" / "index.html").read_text(encoding="utf-8")
    reemplazos = {
        "{{NOMBRE}}": html.escape(config["nombre"]),
        "{{ESLOGAN}}": html.escape(config.get("eslogan", "")),
        "{{AVISO}}": html.escape(config.get("aviso", "")),
        "{{REDES}}": redes(config),
        "{{ROBOTS}}": "" if config.get("indexar") else '<meta name="robots" content="noindex, nofollow">',
        "{{ACTUALIZADO}}": ahora.strftime("%d/%m/%Y %H:%M"),
        "{{DATOS}}": json.dumps(
            {
                "productos": productos,
                "categorias": categorias,
                "whatsapp": config["whatsapp"],
                "mensaje": config.get("mensaje_pedido", "Hola, quiero hacer este pedido:"),
            },
            ensure_ascii=False,
        ).replace("</", "<\\/"),
    }
    for marca, valor in reemplazos.items():
        plantilla = plantilla.replace(marca, valor)

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    (SALIDA / "index.html").write_text(plantilla, encoding="utf-8")
    shutil.copytree(RAIZ / "img", SALIDA / "img")
    (SALIDA / ".nojekyll").touch()

    if config.get("dominio"):
        (SALIDA / "CNAME").write_text(config["dominio"].strip() + "\n")

    print(f"Listo: {len(productos)} productos en {len(categorias)} categorías -> _site/index.html")


if __name__ == "__main__":
    main()
