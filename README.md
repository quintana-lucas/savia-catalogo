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
- **Pull requests** y revisión de cambios antes de mergear a `main`.
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

## Cómo funciona

```
CSV / Google Sheets  ──(GitHub Action: en cada push a main, cada hora o a mano)──▶  build.py  ──▶  GitHub Pages
```

- `config.json` — nombre, eslogan, descripción para Google, número de WhatsApp, aviso, dominio y si Google puede indexar la página (`indexar`). Con `indexar` y `dominio`, el build genera `robots.txt`, `sitemap.xml` y la vista previa para compartir el link.
- `data/productos.csv` — respaldo del catálogo. **No se usa mientras la planilla esté conectada**
  (variable `SHEET_CSV_URL`): los cambios hay que hacerlos en la planilla. Si borrás la variable,
  la página vuelve a armarse con este archivo.
- `plantilla/index.html` — el diseño de la página.
- `img/` — fotos de productos (opcional).
- `assets/` — logo, favicons e imagen para compartir el link (`compartir.jpg`).
- `build.py` — arma la página en `_site/`. No necesita instalar nada.
- `.github/workflows/publicar.yml` — la Action que genera y publica.

## Conectar la planilla de Google

1. Creá una hoja de cálculo con estas columnas en la primera fila (podés copiar
   el contenido de `data/productos.csv`):

   | Categoría | Nombre | Descripción | Presentación | Precio | Disponible | Foto |
   |---|---|---|---|---|---|---|

2. *Archivo → Compartir → Publicar en la web* → elegí la hoja → formato
   **Valores separados por comas (.csv)** → Publicar. Copiá el link.
3. En el repo: *Settings → Secrets and variables → Actions → pestaña Variables →
   New repository variable*. Nombre: `SHEET_CSV_URL`, valor: el link.
4. Corré la Action a mano (*Actions → Publicar catálogo → Run workflow*) para
   publicar la planilla por primera vez.

### Cuándo se actualiza la página

- **Sola, cada hora** de 8 a 22 (hora de Argentina). Si la planilla no cambió, no
  publica nada. GitHub a veces atrasa estas corridas unos minutos.
- **Al momento**: *Actions → Publicar catálogo → Run workflow*. Esperá unos 5 minutos
  después de editar la planilla, que es lo que tarda Google en actualizar la versión
  publicada.
- Si el repo pasa 60 días sin cambios, GitHub apaga la corrida automática y manda un
  mail; se vuelve a activar desde *Actions → Publicar catálogo → Enable workflow*.

### Reglas para quien carga la planilla

- **Precio**: solo el número (`6500` o `6.500`). Vacío → muestra "Consultar".
- **Disponible**: `si` o `no`. Con `no` el producto se ve en gris y no se puede pedir.
- **Foto** (opcional): un link `https://...` a la imagen, o el nombre de un archivo
  subido a `img/` (por ejemplo `frutillas.jpg`). Sin foto, se muestra un ícono.
- **Foto**: si el archivo no está en `img/`, la Action avisa en el log (warning) y se muestra el emoji del producto hasta que la subas. Si solo difiere en mayúsculas (`Acelga.JPG` y `acelga.jpg`), usa el archivo que existe.
- **Categoría «Ofertas»**: si tiene productos, aparece siempre primera, con 🔥. Si no tiene, no se muestra. Un producto puede estar en Ofertas y en su categoría a la vez (dos filas); en el pedido de WhatsApp el de oferta sale marcado «[oferta]».
- Las filas sin nombre se ignoran.
- No renombres ni borres la primera fila: si faltan las columnas **Nombre** o
  **Precio**, la Action falla y la página anterior sigue publicada.
- Si la planilla queda vacía, o con menos de la mitad de los productos que hay en
  la página, la Action también falla a propósito. Si sacaste muchos productos a
  propósito, corré la Action a mano tildando *Publicar igual*.

## Probar en la compu

```bash
python3 build.py
python3 -m http.server -d _site 8000
# abrir http://localhost:8000
```

## A tener en cuenta

- El repo es público: no pongas costos ni datos internos en la hoja publicada.
- Los textos, el nombre y el número de WhatsApp se configuran en `config.json`.
