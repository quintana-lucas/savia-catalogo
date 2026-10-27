# savia-catalogo

Catálogo de **Savia**. El nombre y los textos se cambian en `config.json`.

Página de catálogo que se genera desde una lista de productos (CSV o planilla
de Google Sheets) y recibe los pedidos por WhatsApp. Se publica con GitHub Pages.

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
