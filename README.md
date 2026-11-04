# savia-catalogo

Proyecto personal de práctica para aplicar lo que vi en el learning path
[Career Essentials in GitHub](https://www.linkedin.com/learning/paths/career-essentials-in-github-professional-certificate)
de LinkedIn Learning, sobre todo **GitHub Actions** y **GitHub Pages**.

No es un producto ni un servicio comercial: es un ejercicio para aprender a
automatizar la publicación de un sitio estático. Para practicar con datos de
verdad, el caso elegido es un catálogo de productos (alimentos congelados) que
arma los pedidos como un mensaje de WhatsApp.

## Qué se practica

- **GitHub Actions**: un workflow que se dispara con `push`, a mano
  (`workflow_dispatch`, con un input) y por horario (`schedule` con cron).
- **GitHub Pages**: publicación con las Actions oficiales
  (`configure-pages`, `upload-pages-artifact`, `deploy-pages`), en vez de una rama `gh-pages`.
- **Variables de repositorio**: la Action lee `SHEET_CSV_URL` desde *Settings → Variables*.
- **Pasos condicionales**: el build decide si hay que publicar (`if:` sobre un output del paso).
- Dominio propio, `robots.txt`, `sitemap.xml` e indexación en Google.

## De dónde sale la idea: del feed RSS a una página HTML

El ejemplo del curso mantiene actualizado el **feed RSS (XML) de un podcast**:
los datos de los episodios viven en un archivo del repo, una Action los
transforma en `feed.xml` y lo publica. Lo que consume ese XML es una app de
podcasts (Spotify, Apple Podcasts), no una persona.

Acá se usa el mismo patrón, pero cambia quién lee el resultado. Un catálogo lo
mira una persona en el navegador del celular, que necesita fotos, precios,
filtros y un botón para pedir. Un archivo XML no se ve así en un navegador,
por eso la salida es una página HTML armada desde una plantilla. Nunca llegó a
haber una versión con RSS: la primera versión ya salió con CSV y HTML.

| En el curso (podcast) | En este proyecto |
|---|---|
| Archivo de datos con los episodios | `data/productos.csv` o una planilla de Google |
| Script que genera el feed | `build.py` |
| `feed.xml` (RSS) para apps de podcasts | `index.html` para el navegador, desde `plantilla/index.html` |
| Action que lo regenera y publica | `.github/workflows/publicar.yml` |

## ¿Quiénes somos?: modal o página

El texto está en `config.json`, en `quienes_somos` (una lista: cada elemento es un
párrafo). Si se borra ese campo, el botón no aparece.

Cómo se muestra lo decide la variable de repositorio `QUIENES_SOMOS`
(*Settings → Secrets and variables → Actions → Variables*):

| Valor | Resultado |
|---|---|
| `modal` (o sin la variable) | El botón del encabezado abre un cartel encima del catálogo. |
| `pagina` | El botón lleva a `quienes-somos.html`, que también entra en el `sitemap.xml`. |

Las corridas automáticas solo publican si cambió la planilla: después de cambiar
la variable, corré la Action a mano (*Actions → Publicar catálogo → Run workflow*).
Para probar en local: `QUIENES_SOMOS=pagina python build.py`.
