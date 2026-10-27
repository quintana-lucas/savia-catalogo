#!/usr/bin/env python3
"""Genera el catálogo estático en _site/.

Fuente de productos (en orden de prioridad):
  1. La variable de entorno SHEET_CSV_URL (Google Sheets publicada como CSV).
  2. El archivo local data/productos.csv.

Otras variables de entorno (las pone la GitHub Action):
  SOLO_SI_CAMBIA=true  no publica si los productos son iguales a los de la página actual.
  FORZAR=true          publica aunque haya muchos menos productos que antes.

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
# Sin estas columnas la página saldría rota (sin productos o todo en "Consultar").
OBLIGATORIAS = ("nombre", "precio")
# Si quedan menos de esta fracción de los productos publicados, se frena (filas borradas por error).
MINIMO_RESPECTO_ANTERIOR = 0.5


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
    lector = csv.DictReader(io.StringIO(texto))
    encontradas = [c for c in (lector.fieldnames or []) if c]
    faltan = [c for c in OBLIGATORIAS if c not in {COLUMNAS.get(normalizar(x)) for x in encontradas}]
    if faltan:
        sys.exit(
            f"ERROR: a la planilla le faltan las columnas {', '.join(faltan)}. "
            f"Columnas encontradas: {', '.join(encontradas) or '(ninguna)'}. "
            "Revisá que nadie haya renombrado o borrado la primera fila. No se publica nada."
        )
    return list(lector)


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


def metadatos(config, titulo):
    """Canonical, Open Graph (vista previa al compartir el link) y datos estructurados para Google."""
    if not config.get("dominio"):
        return ""
    base = f"https://{config['dominio'].strip()}/"
    imagen = base + "assets/compartir.jpg"
    descripcion = config.get("descripcion") or config.get("eslogan", "")
    negocio = {
        "@context": "https://schema.org",
        "@type": "Store",
        "name": config["nombre"],
        "description": descripcion,
        "url": base,
        "logo": base + "assets/favicon-512.png",
        "image": imagen,
        "telephone": "+" + config["whatsapp"],
        "sameAs": [config["instagram"]] if config.get("instagram") else [],
    }
    etiquetas = [
        f'<link rel="canonical" href="{base}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="es_AR">',
        f'<meta property="og:site_name" content="{html.escape(config["nombre"])}">',
        f'<meta property="og:title" content="{html.escape(titulo)}">',
        f'<meta property="og:description" content="{html.escape(descripcion)}">',
        f'<meta property="og:url" content="{base}">',
        f'<meta property="og:image" content="{imagen}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<script type="application/ld+json">'
        + json.dumps(negocio, ensure_ascii=False).replace("</", "<\\/")
        + "</script>",
        # Nombre del sitio que muestra Google arriba del resultado (si no, pone el dominio)
        '<script type="application/ld+json">'
        + json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": config["nombre"],
                "alternateName": config["dominio"].strip(),
                "url": base,
            },
            ensure_ascii=False,
        ).replace("</", "<\\/")
        + "</script>",
    ]
    return "\n".join(etiquetas)


def robots_y_sitemap(config, ahora):
    """robots.txt y sitemap.xml: le dicen a Google qué puede indexar y dónde está la página."""
    if not config.get("indexar"):
        (SALIDA / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
        return
    robots = "User-agent: *\nAllow: /\n"
    if config.get("dominio"):
        base = f"https://{config['dominio'].strip()}/"
        robots += f"\nSitemap: {base}sitemap.xml\n"
        (SALIDA / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"  <url><loc>{base}</loc><lastmod>{ahora.date().isoformat()}</lastmod></url>\n"
            "</urlset>\n"
        )
    (SALIDA / "robots.txt").write_text(robots)


def productos_publicados(config):
    """Los productos de la página que está online ahora, o None si no se pueden leer."""
    if not config.get("dominio"):
        return None
    url = f"https://{config['dominio'].strip()}/productos.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:  # primera vez (todavía no existe), sin conexión, etc.
        print(f"No se pudo leer {url} ({e}). Se sigue sin comparar.")
        return None


def avisar_a_la_action(clave, valor):
    salida = os.environ.get("GITHUB_OUTPUT")
    if salida:
        with open(salida, "a") as f:
            f.write(f"{clave}={valor}\n")


def activa(variable):
    return os.environ.get(variable, "").strip().lower() == "true"


def main():
    config = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
    productos = limpiar_filas(leer_csv())
    if not productos:
        sys.exit("ERROR: la planilla no tiene productos. No se publica nada para no dejar la página vacía.")

    anteriores = productos_publicados(config)
    if anteriores is not None:
        if activa("SOLO_SI_CAMBIA") and anteriores == productos:
            print("Los productos no cambiaron: no se publica.")
            avisar_a_la_action("publicar", "false")
            return
        if len(productos) < len(anteriores) * MINIMO_RESPECTO_ANTERIOR and not activa("FORZAR"):
            sys.exit(
                f"ERROR: la página tiene {len(anteriores)} productos y la planilla solo {len(productos)}. "
                "Si fue a propósito, corré la Action a mano tildando «Publicar igual». No se publica nada."
            )

    categorias = list(dict.fromkeys(p["categoria"] for p in productos))
    ahora = datetime.now(timezone(timedelta(hours=-3)))

    # Título de la pestaña y del resultado en Google: el nombre solo dice poco.
    titulo = config.get("titulo") or " | ".join(filter(None, [config["nombre"], config.get("eslogan")]))

    plantilla = (RAIZ / "plantilla" / "index.html").read_text(encoding="utf-8")
    reemplazos = {
        "{{TITULO}}": html.escape(titulo),
        "{{METADATOS}}": metadatos(config, titulo),
        "{{NOMBRE}}": html.escape(config["nombre"]),
        "{{ESLOGAN}}": html.escape(config.get("eslogan", "")),
        "{{DESCRIPCION}}": html.escape(config.get("descripcion") or config.get("eslogan", "")),
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
    # Copia de los productos publicados: la próxima corrida la compara con la planilla.
    (SALIDA / "productos.json").write_text(json.dumps(productos, ensure_ascii=False), encoding="utf-8")
    shutil.copytree(RAIZ / "img", SALIDA / "img")
    shutil.copytree(RAIZ / "assets", SALIDA / "assets")
    # Google y algunos navegadores buscan el ícono en /favicon.ico aunque la página diga otra ruta
    shutil.copy(RAIZ / "assets" / "favicon.ico", SALIDA / "favicon.ico")
    (SALIDA / ".nojekyll").touch()

    robots_y_sitemap(config, ahora)

    if config.get("dominio"):
        (SALIDA / "CNAME").write_text(config["dominio"].strip() + "\n")

    avisar_a_la_action("publicar", "true")
    print(f"Listo: {len(productos)} productos en {len(categorias)} categorías -> _site/index.html")


if __name__ == "__main__":
    main()
