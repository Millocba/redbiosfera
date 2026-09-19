# Despliegue en Hostinger

Hostinger compartido corre **Apache + PHP** y sirve archivos: no ejecuta Node,
no corre `npm run build` ni procesos permanentes. Por eso el sitio se publica
subiendo el contenido ya construido de `public/`.

## Qué se sube

El **contenido de `public/`**, no la carpeta. Dentro de `public_html/` del
dominio tiene que quedar así:

```
public_html/
├── .htaccess
├── index.html
├── institucional.html
├── proyectos.html
├── participar.html
├── contacto.html
├── movil.html
├── 404.html
├── enviar.php
├── config.php          ← se crea en el servidor, no viene del repo
├── favicon.svg
├── robots.txt
├── sitemap.xml
└── assets/
```

No subas `design/`, `src/`, `build.py` ni los `.md`.

## Opción A — Administrador de archivos (la más simple)

1. `python3 build.py` para asegurarte de que `public/` está al día.
2. Comprimí el **contenido** de `public/` en un ZIP (incluyendo `.htaccess`,
   que muchos compresores ocultan: activá "mostrar archivos ocultos").
3. hPanel → **Archivos → Administrador de archivos** → entrá a `public_html`.
4. Subí el ZIP y usá **Extraer**. Borrá el ZIP después.

## Opción B — FTP / SFTP

1. hPanel → **Archivos → Cuentas FTP**: anotá host, usuario y puerto.
2. Con FileZilla o WinSCP, subí el contenido de `public/` a `public_html/`.
3. Configurá el cliente para que **no oculte** los archivos que empiezan con
   punto, o `.htaccess` no se sube y se pierden las URLs limpias y el HTTPS.

## Opción C — Git desde hPanel

hPanel → **Avanzado → Git**. Hostinger clona el repositorio pero **no ejecuta
ningún build**, así que el repositorio tiene que traer el sitio ya armado (por
eso `public/` está versionado).

Como Hostinger clona el repositorio completo dentro del directorio que le
indiques, al usar esta vía quedan también `design/`, `src/` y los `.md` en el
servidor. El `.htaccess` incluido bloquea el acceso a `config.php`, a los
`.log` y a los `.md`; si preferís que no exista nada de más, usá la opción A o B.

Ruta de despliegue sugerida: `public_html`, rama `main`. Después de cada push,
tocá **Deploy** (o configurá el webhook que ofrece el panel).

## Configurar los formularios

1. hPanel → **Correos → Cuentas de correo**: creá una casilla del dominio, por
   ejemplo `web@tudominio.com`. Hostinger rechaza los envíos cuyo remitente no
   pertenece al dominio alojado.
2. En `public_html/`, copiá `config.example.php` como **`config.php`** y
   completá:

```php
return [
    'destinatario'     => 'red.biosferaurbana@gmail.com',
    'remitente'        => 'web@tudominio.com',
    'remitente_nombre' => 'Red Biosfera Urbana',
    'guardar_copia'    => true,
    'archivo_registro' => 'mensajes.log',
];
```

3. Probá enviando el formulario de contacto. Deberías volver a la página con el
   aviso verde de "Gracias".

### Si el correo no llega

`mail()` de PHP sale sin autenticación y Gmail suele descartarlo. Dos caminos:

- **Recomendado:** entregar a una casilla del propio dominio
  (`contacto@tudominio.com`) y leerla desde el webmail de Hostinger, o
  redirigirla a Gmail con un reenvío configurado en hPanel.
- **SMTP autenticado:** subí [PHPMailer](https://github.com/PHPMailer/PHPMailer)
  a `public_html/lib/` y reemplazá la llamada a `mail()` en `enviar.php` por un
  envío SMTP contra `smtp.hostinger.com`, puerto 465, SSL, con el usuario y la
  contraseña de la casilla creada en el paso 1.

Mientras tanto, cada mensaje queda guardado en `public_html/mensajes.log`, que
podés leer desde el Administrador de archivos.

## HTTPS y dominio

1. hPanel → **Seguridad → SSL**: instalá el certificado gratuito y activá
   "Forzar HTTPS". El `.htaccess` ya redirige HTTP a HTTPS por las dudas.
2. Editá `public/robots.txt` y `RBU_SITIO` para que apunten al dominio real:

```bash
RBU_SITIO="https://redbiosferaurbana.org/" python3 build.py
```

   Eso actualiza las etiquetas `canonical`, las de Open Graph y `sitemap.xml`.
   Acordate de cambiar también la línea `Sitemap:` de `robots.txt`.

## Versión de PHP

hPanel → **Avanzado → Configuración de PHP**. `enviar.php` requiere **PHP 8.0
o superior** (usa tipos de retorno y arrow functions). Con 8.1, 8.2 o 8.3
funciona sin cambios.

## Lista de verificación

- [ ] `.htaccess` está en `public_html/` (revisá con "mostrar ocultos")
- [ ] `config.php` creado con el remitente del dominio
- [ ] SSL instalado y HTTPS forzado
- [ ] Formulario de contacto probado de punta a punta
- [ ] `robots.txt` y `sitemap.xml` con el dominio definitivo
- [ ] Página 404 funcionando (probá una URL inventada)
