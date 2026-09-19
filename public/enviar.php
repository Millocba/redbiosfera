<?php
/**
 * Red Biosfera Urbana — receptor de los formularios de Participar y Contacto.
 *
 * Pensado para hosting compartido de Hostinger: PHP 8.x, sin Composer y sin
 * dependencias externas. Usa mail() de PHP. Si el correo no llega a destino
 * (es habitual que Gmail descarte lo que sale de mail()), configurá SMTP
 * siguiendo DEPLOY.md.
 */

declare(strict_types=1);

$config = require __DIR__ . '/config.php';

function volver(string $origen, string $query): void
{
    $permitidos = ['participar.html', 'contacto.html'];
    $destino = in_array($origen, $permitidos, true) ? $origen : 'index.html';
    header('Location: ' . $destino . '?' . $query, true, 303);
    exit;
}

$origen = $_SERVER['HTTP_REFERER'] ?? '';
$origen = basename(parse_url($origen, PHP_URL_PATH) ?: '');

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    volver($origen, 'error=metodo');
}

// Trampa antispam: los bots completan todos los campos, las personas no ven este.
if (trim((string) ($_POST['_dejar_vacio'] ?? '')) !== '') {
    volver($origen, 'enviado=1'); // respuesta silenciosa
}

$limpiar = static fn (string $v): string => trim(strip_tags($v));

$formulario = $limpiar((string) ($_POST['_formulario'] ?? 'contacto'));
$nombre     = $limpiar((string) ($_POST['nombre'] ?? ''));
$email      = $limpiar((string) ($_POST['email'] ?? ''));
$telefono   = $limpiar((string) ($_POST['telefono'] ?? ''));
$localidad  = $limpiar((string) ($_POST['localidad'] ?? ''));
$motivo     = $limpiar((string) ($_POST['motivo'] ?? ''));
$mensaje    = $limpiar((string) ($_POST['mensaje'] ?? ''));

$colaboracion = [];
foreach ((array) ($_POST['colaboracion'] ?? []) as $item) {
    $colaboracion[] = $limpiar((string) $item);
}

if ($nombre === '' || $email === '' || $mensaje === '') {
    volver($origen, 'error=campos');
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    volver($origen, 'error=email');
}

// Evita inyección de cabeceras a través del nombre o el correo.
if (preg_match('/[\r\n]/', $nombre . $email)) {
    volver($origen, 'error=campos');
}

$asunto = $formulario === 'voluntariado'
    ? 'Nueva postulación de voluntariado — ' . $nombre
    : 'Nuevo mensaje de contacto — ' . $nombre;

$lineas = [
    'Formulario: ' . $formulario,
    'Nombre: ' . $nombre,
    'Correo: ' . $email,
];
if ($telefono !== '')        { $lineas[] = 'Teléfono: ' . $telefono; }
if ($localidad !== '')       { $lineas[] = 'Localidad: ' . $localidad; }
if ($motivo !== '')          { $lineas[] = 'Motivo: ' . $motivo; }
if ($colaboracion !== [])    { $lineas[] = 'Le interesa: ' . implode(', ', $colaboracion); }
$lineas[] = '';
$lineas[] = 'Mensaje:';
$lineas[] = $mensaje;
$lineas[] = '';
$lineas[] = '---';
$lineas[] = 'Enviado el ' . date('d/m/Y H:i') . ' desde ' . ($_SERVER['HTTP_HOST'] ?? '');

$cuerpo = implode("\n", $lineas);

$cabeceras = [
    'From: ' . $config['remitente_nombre'] . ' <' . $config['remitente'] . '>',
    'Reply-To: ' . $nombre . ' <' . $email . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'MIME-Version: 1.0',
];

$ok = @mail(
    $config['destinatario'],
    '=?UTF-8?B?' . base64_encode($asunto) . '?=',
    $cuerpo,
    implode("\r\n", $cabeceras),
    '-f' . $config['remitente']
);

// Copia local, por si el correo falla: revisala desde el Administrador de archivos.
if (!empty($config['guardar_copia'])) {
    $registro = __DIR__ . '/' . $config['archivo_registro'];
    @file_put_contents(
        $registro,
        "==== " . date('c') . " ====\n" . $cuerpo . "\n\n",
        FILE_APPEND | LOCK_EX
    );
}

volver($origen, $ok ? 'enviado=1' : 'error=envio');
