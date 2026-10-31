// Form Whisperer. Uses helpers from script.js: $, $$, api(), qadamSpeak().
(() => {
  const tpl = $('#fw-card-tpl');
  let found = [];          // fields recognised from a pasted form
  let guide = null;        // { fields, i, ok: [] }

  // ---- speech: English via the site's shared speak(); Roman Urdu via an Urdu/Hindi voice if present
  const rate = () => Number($('#speech-rate')?.value) || 0.9;
  function speakUrdu(text) {
    if (!('speechSynthesis' in window)) return;
    speechSynthesis.cancel();
    const voices = speechSynthesis.getVoices();
    const voice = voices.find(v => v.lang.toLowerCase().startsWith('ur')) || voices.find(v => v.lang.toLowerCase().startsWith('hi'));
    const u = new SpeechSynthesisUtterance(text);
    if (voice) { u.voice = voice; u.lang = voice.lang; }
    u.rate = rate();
    speechSynthesis.speak(u);
  }
  if ('speechSynthesis' in window) speechSynthesis.getVoices();   // warm up the voice list

  // ---- build a card for one field and wire its buttons
  function card(f, { note = '', onOk = null } = {}) {
    const el = tpl.content.firstElementChild.cloneNode(true);
    const q = s => $(s, el);
    q('.fw-name').textContent = f.name;
    q('.fw-en').textContent = f.english;
    q('.fw-tip-en').textContent = f.tip_en ? `Tip: ${f.tip_en}` : '';
    q('.fw-ur').textContent = f.urdu;
    q('.fw-tip-ur').textContent = f.tip ? `Madad: ${f.tip}` : '';
    if (note) { q('.fw-note').textContent = note; q('.fw-note').hidden = false; }
    q('.fw-say-en').onclick = () => qadamSpeak(`${f.name}. ${f.english} ${f.tip_en || ''}`);
    q('.fw-say-ur').onclick = () => speakUrdu(`${f.name}. ${f.urdu} ${f.tip || ''}`);
    if (!f.id) { q('.fw-practice').hidden = true; return el; }   // unknown field: nothing to practise
    q('.fw-ex').textContent = f.example;
    q('.fw-fill').placeholder = f.example;

    const run = async () => {
      const input = q('.fw-fill'), fb = q('.fw-fb');
      let r;
      try { r = await api('/api/form-whisperer/check', { field: f.id, value: input.value }); }
      catch (e) { fb.hidden = false; fb.className = 'fw-fb'; fb.textContent = e.message; return; }
      fb.hidden = false;
      fb.className = 'fw-fb' + (r.ok ? ' ok' : '');
      fb.innerHTML = '';
      for (const t of [r.en, r.ur]) { const p = document.createElement('p'); p.textContent = t; fb.appendChild(p); }
      const say = document.createElement('button');
      say.type = 'button'; say.className = 'btn alt'; say.textContent = '🔊 Listen';
      say.onclick = () => qadamSpeak(r.en);
      fb.appendChild(say);
      if (r.ok && r.normalized && r.normalized !== input.value.trim()) input.value = r.normalized;
      if (r.ok && onOk) onOk();
    };
    q('.fw-check').onclick = run;
    q('.fw-fill').addEventListener('keydown', e => { if (e.key === 'Enter') run(); });
    return el;
  }

  // ---- tabs
  function showTab(name) {
    const guideTab = name === 'guide';
    $('#fw-explain').hidden = guideTab;
    $('#fw-guide').hidden = !guideTab;
    $('#fw-tab-explain').classList.toggle('on', !guideTab);
    $('#fw-tab-guide').classList.toggle('on', guideTab);
    $('#fw-tab-explain').setAttribute('aria-selected', String(!guideTab));
    $('#fw-tab-guide').setAttribute('aria-selected', String(guideTab));
    if (guideTab) loadPresets();
  }
  $('#fw-tab-explain').onclick = () => showTab('explain');
  $('#fw-tab-guide').onclick = () => showTab('guide');

  // ---- explain one field
  ['CNIC', 'Date of birth', 'Domicile', 'Address', 'Mobile number', 'Next of kin'].forEach(label => {
    const b = document.createElement('button');
    b.type = 'button'; b.textContent = label;
    b.onclick = () => { $('#fw-q').value = label; explain(); };
    $('#fw-sug').appendChild(b);
  });

  async function explain() {
    const text = $('#fw-q').value.trim();
    if (!text) { $('#fw-q').focus(); return; }
    let f;
    try { f = await api('/api/form-whisperer', { text }); }
    catch (e) { $('#fw-res').textContent = e.message; return; }
    showField(f, f.found && f.matched === 'value' ? `What you typed looks like a ${f.name}, so I explained that field.` : '');
    if (f.alternatives?.length) {
      const p = document.createElement('p');
      p.className = 'muted';
      p.textContent = 'Did you mean: ' + f.alternatives.map(a => a.name).join(', ') + '?';
      $('#fw-res').appendChild(p);
    }
  }
  function showField(f, note) {
    const res = $('#fw-res');
    res.innerHTML = '';
    res.appendChild(card(f.found === false ? { ...f, id: '' } : f, { note }));
  }
  $('#fw-go').onclick = explain;
  $('#fw-q').addEventListener('keydown', e => { if (e.key === 'Enter') explain(); });

  // ---- paste a whole form
  $('#fw-scan').onclick = async () => {
    const text = $('#fw-paste').value.trim();
    if (!text) { $('#fw-paste').focus(); return; }
    let r;
    try { r = await api('/api/form-whisperer/scan', { text }); }
    catch (e) { $('#fw-scan-out').textContent = e.message; return; }
    found = r.fields;
    $('#fw-scan-out').textContent = `Found ${found.length} field${found.length === 1 ? '' : 's'}.` +
      (r.unknown.length ? ` I did not recognise: ${r.unknown.join(', ')}.` : '');
    const box = $('#fw-found');
    box.innerHTML = '';
    found.forEach(f => {
      const b = document.createElement('button');
      b.type = 'button'; b.textContent = f.name;
      b.onclick = () => showField(f, '');
      box.appendChild(b);
    });
    $('#fw-guide-found').hidden = !found.length;
  };
  $('#fw-guide-found').onclick = () => { showTab('guide'); startGuide(found); };

  // ---- guided form
  let presets = null;
  async function loadPresets() {
    if (presets) return;
    try { presets = (await api('/api/form-whisperer/presets')).presets; }
    catch (e) { $('#fw-presets').textContent = e.message; return; }
    presets.forEach(p => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'btn alt';
      b.textContent = `${p.title} (${p.fields.length} fields)`;
      b.onclick = () => startGuide(p.fields);
      $('#fw-presets').appendChild(b);
    });
  }
  function startGuide(fields) {
    guide = { fields, i: 0, ok: fields.map(() => false) };
    $('#fw-done').hidden = true;
    $('#fw-run').hidden = false;
    renderStep();
  }
  function renderStep() {
    const { fields, i, ok } = guide, f = fields[i];
    $('#fw-count').textContent = `Field ${i + 1} of ${fields.length}`;
    $('#fw-bar').style.width = `${(i / fields.length) * 100}%`;
    const step = $('#fw-step');
    step.innerHTML = '';
    step.appendChild(card(f, { onOk: () => { ok[i] = true; syncNav(); $('#fw-next').focus(); } }));
    syncNav();
    $('.fw-fill', step).focus({ preventScroll: true });
  }
  function syncNav() {
    const { fields, i, ok } = guide;
    $('#fw-back').disabled = i === 0;
    $('#fw-next').disabled = !ok[i];
    $('#fw-next').textContent = i === fields.length - 1 ? 'Finish ✔' : 'Next ▶';
  }
  $('#fw-back').onclick = () => { if (guide.i > 0) { guide.i--; renderStep(); } };
  $('#fw-next').onclick = async () => {
    if (!guide.ok[guide.i]) return;
    if (guide.i < guide.fields.length - 1) { guide.i++; renderStep(); return; }
    $('#fw-run').hidden = true;
    $('#fw-done').hidden = false;
    $('#fw-done-text').textContent = `You filled ${guide.fields.length} fields correctly.`;
    try { await api('/api/progress', { kind: 'practice', key: 'form', value: 1 }); } catch (e) { /* progress is optional */ }
  };
  $('#fw-stuck').onclick = () => {                      // show the example and say it aloud
    const f = guide.fields[guide.i], input = $('.fw-fill', $('#fw-step'));
    input.value = f.example;
    input.focus();
    qadamSpeak(`Try this: ${f.example}. Then press Check.`);
  };
  $('#fw-again').onclick = () => { $('#fw-done').hidden = true; $('#fw-run').hidden = true; guide = null; };
})();
