# Red Biosfera Urbana — sitio web

Sitio institucional de la Red Biosfera Urbana (Córdoba, Argentina): educación
ambiental e inteligencia territorial con escuelas y barrios.

Es un sitio **estático** (HTML + CSS + JavaScript, sin framework ni paso de
compilación) con un único archivo PHP para procesar los formularios. Está
pensado para funcionar tal cual en el **hosting compartido de Hostinger**, que
no ejecuta Node ni procesos en segundo plano.

## Primer paso

El repositorio Git todavía no está inicializado. Ejecutá una vez, con doble clic
o desde la consola:



Eso crea el repositorio, hace el primer commit y te muestra los comandos para
subirlo a GitHub.

## Estructura

```
.
├── init-repo.cmd     Crea el repositorio Git (ejecutar una sola vez)
├── build.py          Regenera public/ a partir del mockup de design/
├── design/           Diseño base original (mockup v4 standalone) y sus piezas
├── src/static/       Archivos escritos a mano que se copian tal cual a public/
│   ├── .htaccess         Reglas de Apache (HTTPS, URLs limpias, caché, cabeceras)
│   ├── enviar.php        Receptor de los formularios
│   ├── config.example.php Plantilla de configuración (copiar a config.php)
│   ├── favicon.svg
│   ├── robots.txt
│   └── assets/
│       ├── css/ajustes.css   Correcciones de accesibilidad y responsive
│       └── js/sitio.js       JS mínimo (avisos de envío)
└── public/           Sitio listo para subir a public_html  ← esto es lo que se despliega
```

`public/` está versionado a propósito: Hostinger no compila nada, así que lo
que se sube es exactamente lo que hay en esa carpeta.

## Páginas

| Archivo | Sección |
|---|---|
| `index.html` | Inicio: propuesta, corte del territorio, metodología, novedades |
| `institucional.html` | Quiénes somos, enfoque, equipo y distinciones |
| `proyectos.html` | Diagnóstico territorial y líneas de trabajo |
| `participar.html` | Formulario de voluntariado y donaciones |
| `contacto.html` | Formulario de contacto y correos institucionales |
| `movil.html` | Vista compacta heredada del mockup |
| `404.html` | Página de error |

## Trabajar en el sitio

**Cambios de contenido, estilos o comportamiento:** editá directamente los
archivos de `public/`. No hace falta nada más; abrí el HTML en el navegador o
levantá un servidor local:

```bash
cd public
python3 -m http.server 8000     # http://localhost:8000
```

Para probar también el PHP de los formularios:

```bash
cd public
cp config.example.php config.php
php -S localhost:8000
```

**Regenerar desde el mockup:** `build.py` vuelve a desempaquetar
`design/Red Biosfera Urbana v4 (standalone).html` y reconstruye `public/`.
Sirve cuando llega una versión nueva del diseño, pero **pisa los cambios
manuales hechos en los HTML generados**. Los archivos de `src/static/` nunca
se pisan: se copian tal cual.

```bash
python3 build.py
RBU_SITIO="https://redbiosferaurbana.org/" python3 build.py   # fija canonical y sitemap
```

## Sistema de diseño

El mockup trae el sistema "Organic": tipografías Caprasimo (títulos) y Figtree
(texto), paleta tierra/verde y componentes en CSS plano.

- `public/assets/css/organic.css` — tokens y componentes (generado, no editar a mano)
- `public/assets/css/sitio.css` — estilos específicos de estas pantallas (generado)
- `public/assets/css/ajustes.css` — ajustes propios del sitio real (editable)

Las fuentes están alojadas localmente en `public/assets/fonts/`: no hay pedidos
a Google Fonts ni a ningún CDN.

## Despliegue

Ver [DEPLOY.md](DEPLOY.md).

## Pendientes de contenido

El diseño marca con un cartel naranja lo que todavía falta definir: novedades
reales, roles del equipo, personería jurídica, cifras de impacto y medios de
donación. Para ocultar todos esos carteles de una vez, cambiá en cada página
`<body data-pendientes="on">` por `data-pendientes="off"`.
