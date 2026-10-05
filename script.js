/* Clínica Diamond Lux — interações mínimas */
(function () {
  'use strict';

  /* ── Menu mobile ────────────────────────────────────────── */
  var burger = document.getElementById('burger');
  var nav = document.getElementById('nav');

  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      burger.classList.toggle('is-on', open);
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    });

    nav.addEventListener('click', function (e) {
      if (e.target.closest('.nav__a')) {
        nav.classList.remove('is-open');
        burger.classList.remove('is-on');
        burger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ── Link ativo conforme a seção visível ────────────────── */
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav__a'));
  var sections = links
    .map(function (a) { return document.querySelector(a.getAttribute('href')); })
    .filter(Boolean);

  if (sections.length && 'IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) {
          a.classList.toggle('is-on', a.getAttribute('href') === '#' + en.target.id);
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* ── Reveal ao entrar na viewport ───────────────────────── */
  var revealables = document.querySelectorAll('.rv');

  if (!('IntersectionObserver' in window)) {
    revealables.forEach(function (el) { el.classList.add('is-in'); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add('is-in');
      io.unobserve(en.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

  revealables.forEach(function (el) { io.observe(el); });

  // Rede de segurança: em aba aberta em segundo plano o navegador congela o
  // IntersectionObserver, e o que está na primeira dobra ficaria invisível.
  setTimeout(function () {
    revealables.forEach(function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight) {
        el.classList.add('is-in');
        io.unobserve(el);
      }
    });
  }, 900);


  /* ── Formulário de avaliação ────────────────────────────── */
  var WHATS = '5511999460403';
  var form = document.getElementById('lead');

  function so(v) { return v.replace(/\D/g, ''); }

  function mascaraTelefone(v) {
    var d = so(v).slice(0, 11);
    if (d.length <= 10) return d.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3').replace(/[-\s()]*$/, '');
    return d.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3').replace(/-$/, '');
  }

  function mascaraCPF(v) {
    var d = so(v).slice(0, 11);
    return d.replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d{1,2})$/, '$1-$2');
  }

  function cpfValido(v) {
    var d = so(v);
    if (d.length !== 11 || /^(\d)\1{10}$/.test(d)) return false;
    for (var t = 9; t < 11; t++) {
      var soma = 0;
      for (var i = 0; i < t; i++) soma += +d[i] * (t + 1 - i);
      var dig = (soma * 10) % 11 % 10;
      if (dig !== +d[t]) return false;
    }
    return true;
  }

  if (form) {
    var tel = document.getElementById('f-tel');
    var cpf = document.getElementById('f-cpf');
    tel.addEventListener('input', function () { tel.value = mascaraTelefone(tel.value); });
    cpf.addEventListener('input', function () { cpf.value = mascaraCPF(cpf.value); });

    var REGRAS = [
      ['f-nome', function (v) { return v.trim().split(/\s+/).length >= 2; }, 'Escreva seu nome e sobrenome.'],
      ['f-tel', function (v) { return so(v).length >= 10; }, 'Telefone incompleto.'],
      ['f-email', function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()); }, 'E-mail inválido.'],
      ['f-cpf', cpfValido, 'CPF inválido.'],
      ['f-nasc', function (v) { return !!v && new Date(v) < new Date(); }, 'Informe a data de nascimento.'],
      ['f-sexo', function (v) { return !!v; }, 'Selecione uma opção.'],
      ['f-end', function (v) { return v.trim().length >= 6; }, 'Informe seu endereço.'],
      ['f-ok', null, 'Precisamos da sua autorização para entrar em contato.']
    ];

    function erro(id, msg) {
      var campo = document.getElementById(id);
      var alvo = document.getElementById('e-' + id);
      if (alvo) alvo.textContent = msg || '';
      var caixa = campo.closest('.fld');
      if (caixa) caixa.classList.toggle('is-bad', !!msg);
      return !msg;
    }

    function checa(id, teste, msg) {
      var campo = document.getElementById(id);
      if (!teste) return erro(id, campo.checked ? '' : msg);
      return erro(id, teste(campo.value) ? '' : msg);
    }

    REGRAS.forEach(function (r) {
      var campo = document.getElementById(r[0]);
      campo.addEventListener('blur', function () { checa(r[0], r[1], r[2]); });
      campo.addEventListener('input', function () {
        if (campo.closest('.fld') && campo.closest('.fld').classList.contains('is-bad')) checa(r[0], r[1], r[2]);
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true, primeiro = null;
      REGRAS.forEach(function (r) {
        if (!checa(r[0], r[1], r[2])) { ok = false; primeiro = primeiro || document.getElementById(r[0]); }
      });
      if (!ok) { primeiro.focus(); return; }

      var d = new FormData(form);
      var nasc = (d.get('nascimento') || '').split('-');
      var linhas = [
        'Opa, vim do site! Quero agendar uma avaliação.',
        '',
        'Nome: ' + d.get('nome'),
        'Telefone: ' + d.get('telefone'),
        'E-mail: ' + d.get('email'),
        'CPF: ' + d.get('cpf'),
        'Nascimento: ' + (nasc.length === 3 ? nasc[2] + '/' + nasc[1] + '/' + nasc[0] : ''),
        'Sexo: ' + d.get('sexo'),
        'Endereço: ' + d.get('endereco')
      ];
      if ((d.get('mensagem') || '').trim()) linhas.push('', 'Mensagem: ' + d.get('mensagem').trim());

      window.open('https://wa.me/' + WHATS + '?text=' + encodeURIComponent(linhas.join('\n')), '_blank', 'noopener');
      document.getElementById('formOk').hidden = false;
      form.reset();
    });
  }

  /* ── Lux, assistente da clínica ─────────────────────────── */
  var botBar = document.getElementById('botBar');
  var botWin = document.getElementById('botWin');

  var RESPOSTAS = {
    procedimentos:
      'A clínica trabalha com harmonização glútea, subcisão de celulite com cânula, PRP e PRF, toxina botulínica, terapia capilar (capacete de LED I9 Profissional e ativos PHD Victa), limpeza de pele, protocolos faciais e rejuvenescimento.\n\nQual deles te interessa?',
    avaliacao:
      'Na primeira consulta a profissional avalia a sua pele e entende o que você quer tratar. O protocolo e o número de sessões saem dessa avaliação.\n\nPara marcar, chame no WhatsApp (11) 99946-0403 ou preencha o formulário no fim da página.',
    capilar:
      'A terapia capilar usa o capacete de LED I9 Profissional, um equipamento de fotobiomodulação, combinado com ativos da linha PHD Victa. O protocolo é montado na avaliação, de acordo com o seu caso.',
    celulite:
      'A subcisão é feita com cânula e libera as traves fibrosas que puxam a pele para dentro e formam os furinhos. Na sequência é aplicado um ativo para preencher a depressão. A indicação e o número de sessões saem da avaliação.',
    toxina:
      'A toxina botulínica é aplicada para suavizar as linhas de expressão. A dosagem e os pontos de aplicação são definidos para o seu rosto.',
    gluteo:
      'A harmonização glútea trabalha o contorno e o volume da região. As técnicas são escolhidas caso a caso, a partir da avaliação.',
    prp:
      'PRP e PRF são preparados a partir do seu próprio sangue: uma pequena coleta é centrifugada para concentrar plaquetas e fibrina, que depois são aplicadas. Por serem do próprio paciente, não há material de terceiros envolvido.',
    limpeza:
      'A limpeza de pele inclui higienização profunda, extração e finalização com ativos escolhidos para o seu tipo de pele.',
    local:
      'A clínica fica na R. do Oratório, 3735, Alto da Mooca, São Paulo/SP, CEP 03195-100.\n\nA estrutura tem recepção, cantinho do café e sala de tratamentos, e dá para ver as fotos aqui mesmo no site.',
    agendar:
      'O agendamento é por WhatsApp, no (11) 99946-0403. Você também pode preencher o formulário no fim da página que a clínica entra em contato com os horários disponíveis.',
    horario:
      'Para saber os horários livres da semana, chame a clínica no WhatsApp (11) 99946-0403.',
    preco:
      'Os valores dependem do protocolo e da quantidade de sessões, e isso é definido na avaliação. Chame no WhatsApp (11) 99946-0403 para falar sobre o seu caso.',
    fallback:
      'Essa pergunta precisa de avaliação profissional, então não vou responder por aqui. Fale com a clínica pelo WhatsApp (11) 99946-0403.'
  };

  var ROTULOS = {
    procedimentos: 'Quais procedimentos vocês fazem?',
    avaliacao: 'Como funciona a primeira avaliação?',
    capilar: 'Como é a terapia capilar?',
    celulite: 'O que é a subcisão de celulite?',
    local: 'Onde fica a clínica?',
    agendar: 'Como faço para agendar?'
  };

  function acha(q) {
    var t = q.toLowerCase();
    if (/agend|marcar|hor[aá]rio de atend|consulta|vaga/.test(t)) return RESPOSTAS.agendar;
    if (/hor[aá]rio|funciona|abre|fecha|atende que dia/.test(t)) return RESPOSTAS.horario;
    if (/pre[cç]o|valor|quanto custa|or[cç]amento|caro|parcel/.test(t)) return RESPOSTAS.preco;
    if (/onde|endere[cç]o|local|chegar|fica|mooca|estacion/.test(t)) return RESPOSTAS.local;
    if (/capil|cabelo|queda|calv|i9|phd|victa|alopec/.test(t)) return RESPOSTAS.capilar;
    if (/celulit|subcis|furinho|traves|c[aâ]nula/.test(t)) return RESPOSTAS.celulite;
    if (/botox|toxina|botul|ruga|linha de expres/.test(t)) return RESPOSTAS.toxina;
    if (/gl[uú]te|bumbum|harmoniza/.test(t)) return RESPOSTAS.gluteo;
    if (/prp|prf|plasma|fibrina|plaqueta/.test(t)) return RESPOSTAS.prp;
    if (/limpeza|pele|acne|cravo|poro/.test(t)) return RESPOSTAS.limpeza;
    if (/avalia|primeira|come[cç]|consulta inicial/.test(t)) return RESPOSTAS.avaliacao;
    if (/procedimento|tratament|servi[cç]o|fazem|oferec/.test(t)) return RESPOSTAS.procedimentos;
    return null;
  }

  function fala(texto, quem) {
    var caixa = document.getElementById('botMsgs');
    var m = document.createElement('p');
    m.className = 'bot__m bot__m--' + quem;
    m.textContent = texto;
    caixa.appendChild(m);
    caixa.scrollTop = caixa.scrollHeight;
  }

  function pergunta(chave, texto) {
    fala(texto || ROTULOS[chave] || chave, 'eu');
    var r = RESPOSTAS[chave] || acha(chave) || RESPOSTAS.fallback;
    setTimeout(function () { fala(r, 'bot'); }, 420);
  }

  if (botBar && botWin) {
    botBar.addEventListener('click', function () {
      var aberto = botWin.classList.toggle('is-open');
      botBar.setAttribute('aria-expanded', String(aberto));
      if (aberto) document.getElementById('botIn').focus();
    });
    document.getElementById('botClose').addEventListener('click', function () {
      botWin.classList.remove('is-open');
      botBar.setAttribute('aria-expanded', 'false');
      botBar.focus();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && botWin.classList.contains('is-open')) {
        botWin.classList.remove('is-open');
        botBar.setAttribute('aria-expanded', 'false');
      }
    });

    document.getElementById('botSug').addEventListener('click', function (e) {
      var b = e.target.closest('.bot__s');
      if (!b) return;
      pergunta(b.dataset.q);
    });

    document.getElementById('botForm').addEventListener('submit', function (e) {
      e.preventDefault();
      var campo = document.getElementById('botIn');
      var v = campo.value.trim();
      if (!v) return;
      campo.value = '';
      pergunta(v, v);
    });
  }

  /* ── Esteiras: carrosséis que correm sozinhos ───────────── */
  var semMovimento = window.matchMedia('(prefers-reduced-motion: reduce)');
  var VELOCIDADE = 26;   // pixels por segundo

  Array.prototype.forEach.call(document.querySelectorAll('[data-carr]'), function (carr) {
    var trilho = carr.querySelector('[data-carr-trilho]');
    var originais = Array.prototype.slice.call(trilho.children);
    if (!originais.length) return;

    // Uma cópia da fila inteira: quando a primeira acaba, a segunda já está
    // na tela, então dá para voltar ao início sem ninguém perceber.
    originais.forEach(function (item) {
      var copia = item.cloneNode(true);
      copia.setAttribute('aria-hidden', 'true');
      trilho.appendChild(copia);
    });

    var metade = 0, pausado = false, naTela = true, sobra = 0, anterior = 0;

    function medir() {
      metade = trilho.scrollWidth / 2;
      // Começa em 1px: na posição 0 a volta para trás dispararia sozinha.
      if (trilho.scrollLeft < 1) trilho.scrollLeft = 1;
    }

    function dobra() {
      if (!metade) return;
      if (trilho.scrollLeft >= metade) trilho.scrollLeft -= metade;        // passou do fim
      else if (trilho.scrollLeft <= 0) trilho.scrollLeft += metade - 1;    // voltou antes do início
    }

    function passo() {
      var item = trilho.firstElementChild;
      var vao = parseFloat(getComputedStyle(trilho).columnGap) || 16;
      return (item.getBoundingClientRect().width + vao) * 2;   // dois cards por clique
    }

    function anda(agora) {
      var dt = anterior ? Math.min(agora - anterior, 64) : 16;
      anterior = agora;
      if (!pausado && naTela && !semMovimento.matches) {
        sobra += (VELOCIDADE * dt) / 1000;
        var px = Math.floor(sobra);
        if (px) { sobra -= px; trilho.scrollLeft += px; dobra(); }
      }
      requestAnimationFrame(anda);
    }

    function pausa(ms) {
      pausado = true;
      clearTimeout(trilho._p);
      if (ms) trilho._p = setTimeout(function () { pausado = false; }, ms);
    }

    carr.querySelector('[data-carr-ant]').addEventListener('click', function () {
      pausa(1400); trilho.scrollBy({ left: -passo(), behavior: 'smooth' });
    });
    carr.querySelector('[data-carr-prox]').addEventListener('click', function () {
      pausa(1400); trilho.scrollBy({ left: passo(), behavior: 'smooth' });
    });

    // para enquanto a pessoa está lendo, mexendo ou navegando pelo teclado
    carr.addEventListener('pointerenter', function () { pausa(); });
    carr.addEventListener('pointerleave', function () { pausado = false; });
    carr.addEventListener('focusin', function () { pausa(); });
    carr.addEventListener('focusout', function () { pausado = false; });
    trilho.addEventListener('touchstart', function () { pausa(); }, { passive: true });
    trilho.addEventListener('touchend', function () { pausa(2600); }, { passive: true });
    trilho.addEventListener('scroll', function () {
      clearTimeout(trilho._s);
      trilho._s = setTimeout(dobra, 120);
    });

    window.addEventListener('resize', medir);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { naTela = es[0].isIntersecting; })
        .observe(carr);
    }

    medir();
    requestAnimationFrame(anda);
  });

  /* ── Ano no rodapé ──────────────────────────────────────── */
  var yr = document.getElementById('yr');
  if (yr) yr.textContent = String(new Date().getFullYear());
})();
