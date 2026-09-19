# -*- coding: utf-8 -*-
"""Convierte el mockup standalone (design/) en el sitio estatico de public/."""
import re, os, json, gzip, base64, shutil, sys

SRC = "/mnt/user-data/uploads/Downloads/Red Biosfera Urbana v4 (standalone).html"
ROOT = "/home/claude/rbu/site"
PUB = os.path.join(ROOT, "public")

# ---------- 1. desempaquetar ----------
raw = open(SRC, encoding="utf-8").read().split("\n")
assets = json.loads(raw[381].strip())
doc = json.loads(raw[393].strip())

FONT_NAMES = {}
for k, v in assets.items():
    if v["mime"].startswith("font/"):
        data = base64.b64decode(v["data"])
        if v.get("compressed"):
            data = gzip.decompress(data)
        FONT_NAMES[k] = (data, "woff2")

styles = re.findall(r"<style>(.*?)</style>", doc, re.S)
tokens_css, page_css = styles[0], styles[1]
body = doc[doc.find("<x-dc>") + 6: doc.find("</x-dc>")]
body = body[body.find("</helmet>") + 9:]

# ---------- 2. nombres de fuentes legibles ----------
FONT_FILE = {
    "82408e76-19eb-4cea-9a3c-2dab6f0f6c50": "caprasimo-latin-ext.woff2",
    "4c7e1e24-cc6b-494c-9ad5-1e4c7ac24185": "caprasimo-latin.woff2",
    "8b90a54e-408c-4e34-acbb-8eceef8a5239": "figtree-latin-ext.woff2",
    "5e3700e5-2386-426d-82ff-527c7d1dff9f": "figtree-latin.woff2",
}
font_map = {k: v for k, v in FONT_FILE.items() if k in FONT_NAMES}
for k, name in font_map.items():
    tokens_css = tokens_css.replace('url("%s")' % k, 'url("../fonts/%s")' % name)

# ---------- 3. limpieza del markup ----------
def camel(attr):
    parts = attr.split("-")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

def clean(h):
    h = re.sub(r"</?sc-raw-([a-z0-9]+)", lambda m: ("</" if m.group(0).startswith("</") else "<") + m.group(1), h)
    h = re.sub(r"\bsc-camel-([a-z0-9-]+)=", lambda m: camel(m.group(1)) + "=", h)
    h = re.sub(r'\s*hint-placeholder-val="\{\{[^}]*\}\}"', "", h)
    h = re.sub(r'\s*onClick="\{\{[^}]*\}\}"', "", h)
    h = re.sub(r'\s*onSubmit="\{\{[^}]*\}\}"', "", h)
    return h

PAGES = {
    "isInicio": "index.html",
    "isInstitucional": "institucional.html",
    "isProyectos": "proyectos.html",
    "isParticipar": "participar.html",
    "isContacto": "contacto.html",
    "isMovil": "movil.html",
}

def take(cond):
    start = body.find('<sc-if value="{{ %s }}"' % cond)
    open_tag_end = body.find(">", start) + 1
    depth, i = 1, open_tag_end
    while depth:
        nxt_o = body.find("<sc-if", i)
        nxt_c = body.find("</sc-if>", i)
        if nxt_o != -1 and nxt_o < nxt_c:
            depth += 1; i = nxt_o + 6
        else:
            depth -= 1; i = nxt_c + 8
    return body[open_tag_end:i - 8]

screens = {c: take(c) for c in PAGES}

# footer (vive dentro de inicio): se extrae y se reutiliza
fs = screens["isInicio"].find("<footer")
fe = screens["isInicio"].find("</footer>") + len("</footer>")
FOOTER = screens["isInicio"][fs:fe]
screens["isInicio"] = screens["isInicio"][:fs] + screens["isInicio"][fe:]

# enlaces internos del footer
FOOTER = (FOOTER.replace('href="#institucional"', 'href="institucional.html"')
                .replace('href="#proyectos"', 'href="proyectos.html"')
                .replace('href="#participar"', 'href="participar.html"'))

# bloques condicionales del mockup -> clases reales
def unwrap_conditions(h):
    h = re.sub(r'<sc-if value="\{\{ showPending \}\}"[^>]*>(.*?)</sc-if>',
               lambda m: '<div class="nota-pendiente">%s</div>' % m.group(1), h, flags=re.S)
    h = re.sub(r'<sc-if value="\{\{ enviado \}\}"[^>]*>(.*?)</sc-if>',
               lambda m: '<div class="aviso-enviado" hidden>%s</div>' % m.group(1), h, flags=re.S)
    return h

LINKS = {"goInicio": "index.html", "goInstitucional": "institucional.html",
         "goProyectos": "proyectos.html", "goParticipar": "participar.html",
         "goContacto": "contacto.html", "goMovil": "movil.html"}

def buttons_to_links(h):
    def rep(m):
        attrs, target, text = m.group(1), m.group(2), m.group(3)
        attrs = re.sub(r'\s*type="button"', "", attrs)
        return '<a%s href="%s">%s</a>' % (attrs, LINKS[target], text)
    return re.sub(r'<button([^>]*?)\s*sc-camel-on-click="\{\{ (go\w+) \}\}"([^>]*)>(.*?)</button>',
                  lambda m: rep(re.match(r"()()()", "") or m) if False else
                  '<a%s href="%s">%s</a>' % (re.sub(r'\s*type="button"', "", m.group(1) + m.group(3)),
                                             LINKS[m.group(2)], m.group(4)),
                  h, flags=re.S)

FIELD = {"nombre": "nombre", "email": "email", "tel": "telefono",
         "loc": "localidad", "msg": "mensaje"}

FORM_ID = {"participar.html": "voluntariado", "contacto.html": "contacto"}

def wire_forms(h, fname):
    """Convierte el formulario del mockup en uno funcional contra enviar.php."""
    kind = FORM_ID.get(fname)
    if not kind or "<form" not in h:
        return h

    def form_open(m):
        tag = m.group(0)[:-1]
        tag += ' method="post" action="enviar.php" novalidate'
        return tag + '>\n          <input type="hidden" name="_formulario" value="%s">\n' \
               '          <input type="text" name="_dejar_vacio" tabindex="-1" autocomplete="off" aria-hidden="true" class="trampa-spam">' % kind
    h = re.sub(r"<form\b[^>]*>", form_open, h, count=1)

    # inputs de texto: nombre + required
    def named(m):
        tag, sid = m.group(0), m.group(1)
        key = FIELD.get(sid.split("-", 1)[1])
        if not key:
            return tag
        tag = tag[:-1] + ' name="%s"' % key
        if key in ("nombre", "email", "mensaje"):
            tag += " required"
        return tag + ">"
    h = re.sub(r'<input class="input" id="([a-z0-9]+-[a-z]+)"[^>]*>', named, h)

    # el campo de mensaje es un textarea, no un input
    def to_textarea(m):
        tag = m.group(0)
        ph = re.search(r'placeholder="([^"]*)"', tag)
        idv = re.search(r'id="([^"]*)"', tag).group(1)
        style = re.search(r'style="([^"]*)"', tag)
        st = ' style="%s"' % style.group(1) if style else ' style="min-height:110px"'
        return '<textarea class="input" id="%s" name="mensaje" rows="4" placeholder="%s" required%s></textarea>' % (
            idv, ph.group(1) if ph else "", st)
    h = re.sub(r'<input class="input" id="[a-z0-9]+-msg"[^>]*>', to_textarea, h)

    # checkboxes y radios: value a partir del texto de la etiqueta
    def valued(m):
        inp, mid, text = m.group(1), m.group(2), m.group(3)
        val = re.sub(r"<[^>]+>", "", text).strip()
        inp = inp.replace('name="colab2"', 'name="colaboracion[]"')
        inp = inp.replace('name="motivo2"', 'name="motivo"')
        inp = inp[:-1] + ' value="%s">' % val.replace('"', "&quot;")
        return inp + mid + text
    h = re.sub(r'(<input type="(?:checkbox|radio)"[^>]*>)(\s*(?:<span class="dot"></span>)?)([^<]*)',
               lambda m: valued(m), h)
    return h

NAV = """    <nav class="nav" style="padding-inline:clamp(20px,4vw,56px)">
      <a class="nav-brand" href="index.html">Red Biosfera Urbana</a>
      <a href="institucional.html"{a_inst}>Institucional</a>
      <a href="proyectos.html"{a_proy}>Proyectos</a>
      <a href="participar.html"{a_part}>Participar</a>
      <a href="contacto.html"{a_cont}>Contacto</a>
      <a class="btn btn-primary" href="participar.html#donar">Donar</a>
    </nav>"""

HEAD = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#f5ead8">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="es_AR">
<link rel="stylesheet" href="assets/css/organic.css">
<link rel="stylesheet" href="assets/css/sitio.css">
<link rel="stylesheet" href="assets/css/ajustes.css">
</head>
<body data-pendientes="on">
<a class="saltar" href="#contenido">Saltar al contenido</a>
<div class="pagina">
  <div class="lamina" data-glass>
{nav}
<main id="contenido">
{content}
</main>
{footer}
  </div>
</div>
<script src="assets/js/sitio.js" defer></script>
</body>
</html>
"""

META = {
    "index.html": ("Red Biosfera Urbana — Ciencia ciudadana para la ciudad que habitamos",
                   "Educación ambiental e inteligencia territorial en Córdoba: medimos agua, suelo, aire y vegetación junto a escuelas y barrios."),
    "institucional.html": ("Institucional — Red Biosfera Urbana",
                           "Quiénes somos, enfoque de trabajo, equipo y distinciones recibidas por la Red Biosfera Urbana."),
    "proyectos.html": ("Proyectos — Red Biosfera Urbana",
                       "Proyectos de ciencia ciudadana, monitoreo ambiental, reforestación y corredores biológicos en Córdoba."),
    "participar.html": ("Participar — Red Biosfera Urbana",
                        "Sumate como voluntario/a o colaborá con una donación a la Red Biosfera Urbana."),
    "contacto.html": ("Contacto — Red Biosfera Urbana",
                      "Escribinos para sumar tu escuela, barrio u organización a la Red Biosfera Urbana."),
    "movil.html": ("Vista móvil — Red Biosfera Urbana",
                   "Vista compacta de la Red Biosfera Urbana pensada para teléfonos."),
}

ACTIVE = {"institucional.html": "a_inst", "proyectos.html": "a_proy",
          "participar.html": "a_part", "contacto.html": "a_cont"}

SITIO = os.environ.get("RBU_SITIO", "https://TUDOMINIO/")

# copia todo lo escrito a mano (php, htaccess, ajustes.css, js)
STATIC = os.path.join(ROOT, "src", "static")
if os.path.isdir(PUB):
    shutil.rmtree(PUB)
shutil.copytree(STATIC, PUB)

os.makedirs(os.path.join(PUB, "assets/css"), exist_ok=True)
os.makedirs(os.path.join(PUB, "assets/fonts"), exist_ok=True)
os.makedirs(os.path.join(PUB, "assets/js"), exist_ok=True)

for cond, fname in PAGES.items():
    html = screens[cond]
    html = unwrap_conditions(html)
    html = buttons_to_links(html)
    html = clean(html)
    html = wire_forms(html, fname)
    navkeys = {k: "" for k in ACTIVE.values()}
    if fname in ACTIVE:
        navkeys[ACTIVE[fname]] = ' aria-current="page"'
    nav = NAV.format(**navkeys)
    title, desc = META[fname]
    canonical = SITIO + ("" if fname == "index.html" else fname[:-5])
    out = HEAD.format(title=title, desc=desc, nav=nav, content=html,
                      footer=clean(FOOTER), canonical=canonical)
    open(os.path.join(PUB, fname), "w", encoding="utf-8").write(out)
    print("->", fname, len(out))

open(os.path.join(PUB, "assets/css/organic.css"), "w", encoding="utf-8").write(tokens_css.strip() + "\n")
open(os.path.join(PUB, "assets/css/sitio.css"), "w", encoding="utf-8").write(page_css.strip() + "\n")
for k, name in font_map.items():
    open(os.path.join(PUB, "assets/fonts", name), "wb").write(FONT_NAMES[k][0])
print("fuentes:", sorted(font_map.values()))

# ---------- 4. extras generados ----------
paginas = ["", "institucional", "proyectos", "participar", "contacto", "movil"]
sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for slug in paginas:
    sitemap.append("  <url><loc>%s%s</loc><changefreq>monthly</changefreq></url>" % (SITIO, slug))
sitemap.append("</urlset>")
open(os.path.join(PUB, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sitemap) + "\n")

html404 = HEAD.format(
    title="Página no encontrada — Red Biosfera Urbana",
    desc="La página que buscás no existe o cambió de dirección.",
    canonical=SITIO,
    nav=NAV.format(a_inst="", a_proy="", a_part="", a_cont=""),
    content='''      <section style="padding:clamp(48px,8vw,120px) clamp(24px,4vw,56px);display:flex;flex-direction:column;gap:18px;align-items:flex-start">
        <span style="font-size:13px;letter-spacing:.06em;text-transform:uppercase;font-weight:600;color:var(--color-accent-2-800)">Error 404</span>
        <h1 style="font-family:var(--font-heading);font-size:clamp(34px,5vw,58px);line-height:1.08;margin:0;color:var(--color-accent-2-900)">Esta página<br>no existe.</h1>
        <p style="font-size:18px;line-height:1.7;margin:0;max-width:48ch">Puede que el enlace esté viejo o que la dirección tenga un error. Volvé al inicio o escribinos y lo revisamos.</p>
        <div style="display:flex;flex-wrap:wrap;gap:12px">
          <a class="btn btn-primary" href="index.html">Ir al inicio</a>
          <a class="btn btn-secondary" href="contacto.html">Escribirnos</a>
        </div>
      </section>''',
    footer=clean(FOOTER))
open(os.path.join(PUB, "404.html"), "w", encoding="utf-8").write(html404)
print("-> sitemap.xml, 404.html")
print("listo:", PUB)

# ---------- 5. paquete listo para subir a public_html ----------
DIST = os.path.join(ROOT, "dist")
os.makedirs(DIST, exist_ok=True)
zip_path = os.path.join(DIST, "red-biosfera-urbana-public_html")
if os.path.exists(zip_path + ".zip"):
    os.remove(zip_path + ".zip")
shutil.make_archive(zip_path, "zip", PUB)
print("-> dist/red-biosfera-urbana-public_html.zip (subir y extraer en public_html)")
