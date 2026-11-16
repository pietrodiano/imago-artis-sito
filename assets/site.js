/* Imago Artis Edizioni — menu mobile e form contatti (nessuna dipendenza) */
(function () {
  'use strict';

  document.documentElement.classList.add('js');

  /* ---------------- Menu mobile ---------------- */
  var nav = document.querySelector('nav');
  if (nav) {
    var shop = nav.querySelector('a[href*="wa.me"]');
    var links = Array.prototype.slice.call(nav.querySelectorAll('a.nav-link'));
    var burger = document.querySelector('.nav-burger');
    var panel = document.getElementById('mobile-menu');

    if (!burger && links.length) {
      burger = document.createElement('button');
      burger.type = 'button';
      burger.className = 'nav-burger';
      burger.setAttribute('aria-label', 'Apri il menu');
      burger.setAttribute('aria-expanded', 'false');
      burger.setAttribute('aria-controls', 'mobile-menu');
      burger.innerHTML = '<span></span><span></span><span></span>';
      if (shop) shop.parentNode.insertBefore(burger, shop);
      else nav.querySelector('div').appendChild(burger);
    }

    if (!panel) {
      panel = document.createElement('div');
      panel.id = 'mobile-menu';
      panel.className = 'mobile-menu';
      panel.hidden = true;
      var html = links.map(function (a) {
        return '<a href="' + a.getAttribute('href') + '">' + a.textContent.trim() + '</a>';
      }).join('');
      if (shop) {
        html += '<a class="mm-shop" href="' + shop.href + '" target="_blank" rel="noopener">Shop su WhatsApp</a>';
      }
      panel.innerHTML = html;
      nav.appendChild(panel);
    }

    var setOpen = function (open) {
      panel.hidden = !open;
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? 'Chiudi il menu' : 'Apri il menu');
      document.body.classList.toggle('menu-open', open);
    };

    burger.addEventListener('click', function () {
      setOpen(panel.hidden);
    });
    panel.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !panel.hidden) {
        setOpen(false);
        burger.focus();
      }
    });
    document.addEventListener('click', function (e) {
      if (!panel.hidden && !nav.contains(e.target)) setOpen(false);
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 1024 && !panel.hidden) setOpen(false);
    });
  }

  /* ---------------- Form contatti ---------------- */
  var form = document.querySelector('form[data-contact]');
  if (form) {
    var status = form.querySelector('.form-status');
    var endpoint = form.getAttribute('data-endpoint');
    var address = form.getAttribute('data-email') || 'info@imagoartisedizioni.it';
    var button = form.querySelector('button[type="submit"]');

    var say = function (message, kind) {
      if (!status) return;
      status.textContent = message;
      status.className = 'form-status' + (kind ? ' is-' + kind : '');
    };

    var field = function (name) {
      return form.querySelector('[name="' + name + '"]');
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var nome = field('nome');
      var email = field('email');
      var messaggio = field('messaggio');
      var privacy = field('privacy');
      var valid = true;

      [nome, email, messaggio].forEach(function (el) {
        if (!el) return;
        var empty = !el.value.trim();
        if (el.type === 'email') empty = empty || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim());
        el.classList.toggle('field-error', empty);
        if (empty) valid = false;
      });

      if (privacy && !privacy.checked) {
        valid = false;
      }

      if (!valid) {
        say(privacy && !privacy.checked && nome.value.trim()
          ? 'Autorizza il trattamento dei dati per poter inviare il messaggio.'
          : 'Controlla i campi evidenziati.', 'error');
        return;
      }

      var oggettoSelect = field('oggetto');
      var oggetto = oggettoSelect ? oggettoSelect.options[oggettoSelect.selectedIndex].text : 'Richiesta dal sito';
      var testo =
        'Nome: ' + nome.value.trim() + '\n' +
        'Email: ' + email.value.trim() + '\n' +
        'Motivo: ' + oggetto + '\n\n' +
        messaggio.value.trim() + '\n';

      if (endpoint) {
        button.disabled = true;
        say('Invio in corso…');
        fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({
            nome: nome.value.trim(),
            email: email.value.trim(),
            oggetto: oggetto,
            messaggio: messaggio.value.trim()
          })
        }).then(function (r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          form.reset();
          say('Messaggio inviato. Ti risponderemo entro un giorno lavorativo.', 'ok');
        }).catch(function () {
          say('Invio non riuscito. Scrivi a ' + address + ' oppure su WhatsApp.', 'error');
        }).then(function () {
          button.disabled = false;
        });
        return;
      }

      var mail = 'mailto:' + address +
        '?subject=' + encodeURIComponent('Sito — ' + oggetto + ' — ' + nome.value.trim()) +
        '&body=' + encodeURIComponent(testo);
      window.location.href = mail;
      say('Si sta aprendo il tuo programma di posta con il messaggio già compilato. Se non succede, scrivi a ' + address + '.', 'ok');
    });
  }
})();
