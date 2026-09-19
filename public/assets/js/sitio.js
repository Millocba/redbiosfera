/* Sitio Red Biosfera Urbana — JS mínimo, sin dependencias ni build. */
(function () {
  'use strict';

  // Aviso de envío: enviar.php redirige con ?enviado=1 (o ?error=...).
  var params = new URLSearchParams(window.location.search);

  if (params.get('enviado') === '1') {
    document.querySelectorAll('.aviso-enviado').forEach(function (el) {
      el.hidden = false;
      el.scrollIntoView({ block: 'center' });
    });
  }

  var error = params.get('error');
  if (error) {
    var form = document.querySelector('form[action="enviar.php"]');
    if (form) {
      var aviso = document.createElement('p');
      aviso.className = 'aviso-error';
      aviso.setAttribute('role', 'alert');
      aviso.style.cssText =
        'margin:0;padding:14px 18px;border-radius:999px;background:var(--color-accent-200);' +
        'color:var(--color-accent-800);font-size:15px';
      aviso.textContent = error === 'campos'
        ? 'Faltan datos obligatorios. Revisá nombre, correo y mensaje.'
        : error === 'email'
          ? 'El correo electrónico no parece válido.'
          : 'No pudimos enviar el mensaje. Probá de nuevo o escribinos a red.biosferaurbana@gmail.com.';
      form.prepend(aviso);
      aviso.scrollIntoView({ block: 'center' });
    }
  }

  // Limpia los parámetros de la URL para que un refresh no repita el aviso.
  if (params.has('enviado') || params.has('error')) {
    history.replaceState(null, '', window.location.pathname + window.location.hash);
  }
})();
