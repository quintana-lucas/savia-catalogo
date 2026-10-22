# savia-catalogo

> Nombre provisorio del negocio: **La Huerta Congelada** (se cambia en `config.json`).

Página de catálogo que se actualiza sola desde una planilla de Google Sheets
y recibe los pedidos por WhatsApp. Se publica con GitHub Pages.

## Cómo funciona

```
Google Sheets  ──(GitHub Action: 8:00, 14:00, o a mano)──▶  build.py  ──▶  GitHub Pages
```

- `config.json` — nombre, eslogan, número de WhatsApp, aviso y si Google puede indexar la página.
- `data/productos.csv` — catálogo de ejemplo. Se usa mientras no conectes la planilla.
- `plantilla/index.html` — el diseño de la página.
- `img/` — fotos de productos (opcional).
- `build.py` — arma la página en `_site/`. No necesita instalar nada.
- `.github/workflows/publicar.yml` — la Action que genera y publica.

## Puesta en marcha (una sola vez)

1. **Activar Pages.** En *Settings → Pages → Build and deployment → Source* elegí
   **GitHub Actions**.
2. **Primera publicación.** Andá a *Actions → Publicar catálogo → Run workflow*.
   En un par de minutos queda en `https://quintana-lucas.github.io/savia-catalogo/`.
3. **Poné tu WhatsApp** en `config.json`: código de país + 9 + área + número,
   sin espacios ni `+`. Ejemplo: `5491123456789`.

## Conectar la planilla de Google

1. Creá una hoja de cálculo con estas columnas en la primera fila (podés copiar
   el contenido de `data/productos.csv`):

   | Categoría | Nombre | Descripción | Presentación | Precio | Disponible | Foto |
   |---|---|---|---|---|---|---|

2. *Archivo → Compartir → Publicar en la web* → elegí la hoja → formato
   **Valores separados por comas (.csv)** → Publicar. Copiá el link.
3. En el repo: *Settings → Secrets and variables → Actions → pestaña Variables →
   New repository variable*. Nombre: `SHEET_CSV_URL`, valor: el link.
4. Corré la Action a mano para probar.

### Reglas para quien carga la planilla

- **Precio**: solo el número (`6500` o `6.500`). Vacío → muestra "Consultar".
- **Disponible**: `si` o `no`. Con `no` el producto se ve en gris y no se puede pedir.
- **Foto** (opcional): un link `https://...` a la imagen, o el nombre de un archivo
  subido a `img/` (por ejemplo `frutillas.jpg`). Sin foto, se muestra un ícono.
- Las filas sin nombre se ignoran.
- Si la planilla queda vacía por error, la Action falla a propósito y la página
  anterior sigue publicada.

## Pasar a dominio propio

1. Comprá el dominio (`.com.ar` en NIC Argentina, o `.com` en un registrador).
2. En el DNS:
   - `CNAME` de `www` → `quintana-lucas.github.io`
   - Registros `A` del dominio raíz → `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153`
3. En `config.json` agregá `"dominio": "www.tudominio.com.ar"` y cambiá
   `"indexar": true` para que Google la encuentre.
4. En *Settings → Pages → Custom domain* poné el mismo dominio y, cuando aparezca
   la opción, activá **Enforce HTTPS**.

## Probar en la compu

```bash
python3 build.py
python3 -m http.server -d _site 8000
# abrir http://localhost:8000
```

## A tener en cuenta

- GitHub pausa las Actions programadas si el repo pasa 60 días sin cambios.
  Se reactivan desde la pestaña Actions.
- El repo es público: no pongas costos ni datos internos en la hoja publicada.
