/* Sitio Red Biosfera Urbana — JS mínimo, sin dependencias ni build. */
(function () {
  'use strict';

  // GitHub Pages sirve sólo archivos estáticos: ahí no existe enviar.php.
  // En ese caso el sitio funciona como muestra y los formularios no envían.
  var DEMO = /\.github\.io$/i.test(location.hostname) ||
             document.documentElement.hasAttribute('data-demo');

  var params = new URLSearchParams(window.location.search);

  function mostrarGracias(form) {
    var aviso = (form || document).querySelector('.aviso-enviado') ||
                document.querySelector('.aviso-enviado');
    if (aviso) {
      aviso.hidden = false;
      aviso.scrollIntoView({ block: 'center' });
    }
  }

  if (DEMO) {
    var banda = document.createElement('p');
    banda.setAttribute('role', 'note');
    banda.style.cssText =
      'margin:0;padding:10px 16px;text-align:center;font-size:13px;line-height:1.5;' +
      'background:var(--color-accent-200);color:var(--color-accent-800)';
    banda.textContent = 'Versión de muestra: el diseño es el definitivo, pero los ' +
      'formularios no envían mensajes porque esta vista no tiene servidor.';
    var lamina = document.querySelector('.lamina');
    if (lamina) { lamina.insertBefore(banda, lamina.firstChild); }

    document.querySelectorAll('form[action="enviar.php"]').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!form.reportValidity()) { return; }
        mostrarGracias(form);
        form.reset();
      });
    });
    return;
  }

  // Sitio real: enviar.php redirige con ?enviado=1 (o ?error=...).
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
