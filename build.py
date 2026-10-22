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
