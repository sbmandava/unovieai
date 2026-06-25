/* ===== Theme toggle (light/dark) + Mermaid SVG rendering ===== */
(function () {
  var mmSources = [];
  var mmReady = false;

  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }
  function setBtn() {
    var b = document.getElementById('themeBtn');
    if (b) b.textContent = currentTheme() === 'dark' ? '☀' : '☾';
  }

  window.toggleTheme = function () {
    var t = currentTheme() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', t);
    try { localStorage.setItem('theme', t); } catch (e) {}
    setBtn();
    renderMermaid();
  };

  function renderMermaid() {
    if (!mmReady || !window.mermaid) return;
    var blocks = Array.prototype.slice.call(document.querySelectorAll('pre.mermaid'));
    if (!blocks.length) return;
    blocks.forEach(function (b, i) {
      b.removeAttribute('data-processed');
      b.innerHTML = mmSources[i];
    });
    try {
      window.mermaid.initialize({
        startOnLoad: false,
        theme: currentTheme() === 'dark' ? 'dark' : 'default',
        securityLevel: 'loose',
        flowchart: { useMaxWidth: true, htmlLabels: true },
        sequence: { useMaxWidth: true },
        gantt: { useMaxWidth: true },
        themeVariables: { fontFamily: 'inherit' }
      });
      window.mermaid.run({ nodes: blocks });
    } catch (e) { console.warn('mermaid render', e); }
  }

  function loadMermaid() {
    var blocks = document.querySelectorAll('pre.mermaid');
    if (!blocks.length) return;
    mmSources = Array.prototype.map.call(blocks, function (b) { return b.textContent; });
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js';
    s.onload = function () { mmReady = true; renderMermaid(); };
    s.onerror = function () {
      // graceful fallback: show the diagram source as code
      Array.prototype.forEach.call(blocks, function (b, i) {
        b.classList.add('mm-failed');
        b.textContent = mmSources[i];
      });
    };
    document.head.appendChild(s);
  }

  /* ===== Scorecard logic (only on scorecard page) ===== */
  function scInit() {
    var form = document.getElementById('scorecard');
    if (!form) return;
    var KEY = 'asmm-scorecard-v1';

    function val(dim) {
      var el = form.querySelector('input[name="' + dim + '"]:checked');
      return el ? parseInt(el.value, 10) : null;
    }
    function paintSelected() {
      form.querySelectorAll('.levels label').forEach(function (l) { l.classList.remove('sel'); });
      form.querySelectorAll('.levels input:checked').forEach(function (i) {
        var lab = i.closest('label'); if (lab) lab.classList.add('sel');
      });
    }
    function compute() {
      var dims = ['d1','d2','d3','d4','d5','d6','d7','d8'];
      var vals = dims.map(val);
      var have = vals.filter(function (v) { return v !== null; });
      var gov = [val('d1'), val('d4'), val('d6')];
      var govR = document.getElementById('ro-gov');
      var capR = document.getElementById('ro-cap');
      if (gov.every(function (v) { return v !== null; })) {
        govR.textContent = 'L' + Math.min.apply(null, gov);
      } else { govR.textContent = '—'; }
      if (have.length) {
        capR.textContent = (have.reduce(function (a, b) { return a + b; }, 0) / have.length).toFixed(1);
      } else { capR.textContent = '—'; }
    }
    function save() {
      var data = {};
      form.querySelectorAll('input,textarea').forEach(function (el) {
        if (el.type === 'radio') { if (el.checked) data[el.name] = el.value; }
        else { data[el.name || el.id] = el.value; }
      });
      try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {}
      var tag = document.getElementById('savedTag');
      if (tag) { tag.textContent = 'saved ✓'; setTimeout(function(){ tag.textContent=''; }, 2200); }
    }
    function load() {
      var raw; try { raw = localStorage.getItem(KEY); } catch (e) { return; }
      if (!raw) return;
      var data = JSON.parse(raw);
      Object.keys(data).forEach(function (k) {
        var radios = form.querySelectorAll('input[name="' + k + '"]');
        if (radios.length) {
          radios.forEach(function (r) { if (r.value === data[k]) r.checked = true; });
        } else {
          var el = form.querySelector('[name="' + k + '"]') || document.getElementById(k);
          if (el) el.value = data[k];
        }
      });
      paintSelected(); compute();
    }
    form.addEventListener('change', function () { paintSelected(); compute(); });
    var sv = document.getElementById('scSave'); if (sv) sv.onclick = save;
    var pr = document.getElementById('scPrint'); if (pr) pr.onclick = function () { window.print(); };
    var rs = document.getElementById('scReset'); if (rs) rs.onclick = function () {
      if (!confirm('Clear all entries on this scorecard?')) return;
      form.reset();
      try { localStorage.removeItem(KEY); } catch (e) {}
      paintSelected(); compute();
    };
    load(); paintSelected(); compute();
  }

  document.addEventListener('DOMContentLoaded', function () {
    setBtn();
    loadMermaid();
    scInit();
  });
})();
