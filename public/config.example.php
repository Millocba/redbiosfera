<?php
/**
 * Copiá este archivo como config.php en el servidor y completá los valores.
 * config.php no se versiona (está en .gitignore).
 */
return [
    // A dónde llegan los formularios.
    'destinatario' => 'red.biosferaurbana@gmail.com',

    // Remitente: debe ser una casilla del MISMO dominio del hosting,
    // creada en hPanel → Correos. Si no, Hostinger rechaza el envío.
    'remitente'        => 'web@tudominio.com',
    'remitente_nombre' => 'Red Biosfera Urbana',

    // Copia en texto plano dentro del servidor (respaldo si falla el correo).
    'guardar_copia'    => true,
    'archivo_registro' => 'mensajes.log',
];
