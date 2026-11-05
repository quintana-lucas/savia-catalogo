# Plantilla de catálogo con pedido por WhatsApp

Sitio estático para negocios chicos: un catálogo que se arma solo desde una
planilla de Google Sheets, con carrito y pedido por WhatsApp, y que se publica
gratis con GitHub Pages. Salió del catálogo de Savia y se generalizó para
usarlo con otros clientes.

**Todo lo propio del cliente está en `config.json`.** El resto (`build.py`,
`plantilla/`, el workflow) no se toca para un cliente nuevo.

## Cliente nuevo en 8 pasos

1. **Crear el repo.** En esta plantilla, *Use this template → Create a new
   repository*. Nombre sugerido: `<cliente>-catalogo`.
2. **Logo y fotos.** Subir el logo a `assets/` (SVG, PNG o WebP) y cambiar
   `assets/favicon.ico`, `favicon-512.png`, `apple-touch-icon.png` y
   `compartir.jpg` (1200 × 630, es la vista previa al compartir el link). Las
   fotos de productos van en `img/` con nombres en minúscula, sin espacios.
3. **Editar `config.json`** (tabla de abajo). Como mínimo: `nombre`,
   `whatsapp`, `logo`, `colores` y los textos.
4. **Armar la planilla.** Copiar `data/productos.csv` a una planilla de Google
   con esas columnas: `Categoría, Nombre, Descripción, Presentación, Precio,
   Disponible, Foto`. Solo `Nombre` y `Precio` son obligatorias; un precio
   vacío muestra «Consultar» y `Disponible = no` muestra «Sin stock».
5. **Publicar la planilla.** *Archivo → Compartir → Publicar en la web →* la
   hoja de productos, formato *CSV*. Pegar ese link en `planilla_csv`.
6. **Activar GitHub Pages.** *Settings → Pages → Source: GitHub Actions*.
7. **Dominio (opcional).** Poner el dominio en `dominio`, apuntar el DNS a
   GitHub Pages y, cuando ande, `indexar: true` para que aparezca en Google.
8. **Probar.** Pestaña *Actions → Publicar catálogo → Run workflow*. Revisar
   la página en el celular: agregar un producto y mandar un pedido de prueba.

Para probar en la compu antes de subir: `python3 build.py` y abrir
`_site/index.html` (no hace falta instalar nada).

## Qué va en `config.json`

| Clave | Para qué |
|---|---|
| `nombre`, `eslogan`, `descripcion` | Título de la pestaña, resultado de Google y vista previa al compartir. |
| `whatsapp` | Número con código de país, sin `+` ni espacios: `5491112345678`. Obligatorio. |
| `instagram` | Link al perfil. Vacío = no se muestra el ícono. |
| `planilla_csv` | Link CSV de la planilla publicada. Vacío = usa `data/productos.csv`. |
| `dominio`, `indexar` | Dominio propio y si Google lo puede indexar. Mientras se prueba: `indexar: false`. |
| `logo` | Archivo y tamaño original (ancho y alto en píxeles, para que no salte al cargar). |
| `colores` | `principal` (botones), `principal_oscuro` (botón al pasar el mouse), `secundario` (detalles), `fondo`, `tarjetas`, `texto`, `texto_suave`, `bordes`, `alerta` («Sin stock»). |
| `fuentes` | Dos fuentes de [Google Fonts](https://fonts.google.com): `titulos` y `texto`. |
| `sellos` | Insignias junto al logo («Sin TACC», «Caseras»…). Cada una con `emoji` o `imagen`, y `detalle` opcional. `[]` = ninguna. |
| `mensaje_pedido`, `aviso`, `pie` | Primera línea del mensaje de WhatsApp, cartel de instrucciones y texto del pie. |
| `categorias_primero` | Categorías que van siempre arriba (por ejemplo `Ofertas`). |
| `emojis_categoria`, `emojis_producto`, `emoji_por_defecto` | Emojis que se ven si un producto no tiene foto. Para productos gana la primera palabra que aparezca en el nombre. |
| `quienes_somos`, `quienes_somos_modo` | Párrafos de «¿Quiénes somos?» y si se abren en un cartel (`modal`) o en otra página (`pagina`). `[]` = no aparece. |
| `pedidos_especiales` | Módulo opcional, ver abajo. |

## Módulos opcionales

### Pedidos especiales, catering y cotizador (incluido)

Con `"activo": true` en `pedidos_especiales` se suma la página
`pedidos-especiales.html`, un botón en el encabezado y un aviso arriba del
catálogo. Es un formulario (nombre, tipo de pedido, fecha, personas, zona,
detalle) que arma el mensaje y lo abre en WhatsApp: no necesita servidor ni
base de datos.

- `tipos`: opciones del desplegable «¿Qué necesitás?».
- `minimo_personas`: no deja enviar por debajo de ese número.
- `opciones`: menús para elegir. Si tienen `precio_por_persona`, la página
  muestra un **presupuesto estimado** (personas × precio) y lo suma al
  mensaje. Sin precio = «a consultar». Sin opciones = solo formulario de
  contacto.

Con `"activo": false` desaparece todo rastro del módulo.

### Ideas para más adelante (no están hechas)

- **Cotizador por cantidades** (por ejemplo 30 empanadas + 2 tartas): ya lo
  resuelve el carrito del catálogo, que suma el total estimado. Si hiciera
  falta un catálogo aparte para catering, se puede leer una segunda hoja de la
  misma planilla con otra URL CSV.
- **Recibir consultas por mail además de WhatsApp**: si el sitio se muda a
  Netlify, sus formularios gratis lo resuelven sin código de servidor.
- **Días de entrega o pedido mínimo** en el carrito: un par de claves más en
  `config.json` y unas líneas en `plantilla/index.html`.

## Cómo se publica

`.github/workflows/publicar.yml` corre `build.py`, que lee la planilla y
arma `_site/`, y lo sube a GitHub Pages:

- en cada `push` a `main`;
- a mano, desde *Actions → Run workflow* (con la opción «Publicar igual» si
  la planilla quedó con muchos menos productos a propósito);
- cada hora de 8 a 22, solo si la planilla cambió.

Si la planilla pierde las columnas `Nombre` o `Precio`, queda vacía o pierde
más de la mitad de los productos, **no se publica** y la página sigue como
estaba. Si falta una foto, se muestra el emoji y queda un aviso en el log.
