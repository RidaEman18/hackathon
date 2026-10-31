// Scam Dojo. Jawab server par chhupa rehta hai; "Real or Scam?" dabane par milta hai.
let current = null;   // { token, channel, sender, text }
let revealed = null;  // check ka jawab
let busy = false;

function setErr(msg) {
  const e = $('#dojo-err');
  e.textContent = msg || '';
  e.hidden = !msg;
}

// Message ko highlights ke saath DOM nodes se banao (HTML inject nahi hota).
function paint(text, highlights) {
  const box = $('#msg-text');
  box.textContent = '';
  const low = text.toLowerCase();
  const ranges = [];
  highlights.forEach(h => {
    const i = low.indexOf(h.phrase.toLowerCase());
    if (i < 0) return;
    const end = i + h.phrase.length;
    if (ranges.some(r => i < r.end && end > r.start)) return; // overlap chhod do
    ranges.push({ start: i, end, kind: h.kind, why: h.why });
  });
  ranges.sort((a, b) => a.start - b.start);
  let pos = 0;
  ranges.forEach(r => {
    if (r.start > pos) box.append(text.slice(pos, r.start));
    const m = document.createElement('mark');
    m.className = 'hl ' + r.kind;
    m.title = r.why;
    m.textContent = text.slice(r.start, r.end);
    box.append(m);
    pos = r.end;
  });
  if (pos < text.length) box.append(text.slice(pos));
}

async function loadNext() {
  if (busy) return;
  busy = true;
  setErr('');
  window.speechSynthesis?.cancel();
  $('#check').disabled = true;
  $('#next').hidden = true;
  $('#result').hidden = true;
  $('#msg-meta').textContent = 'Message aa raha hai…';
  $('#msg-text').textContent = '';
  try {
    current = await api('/api/dojo/next');
    revealed = null;
    $('#msg-meta').textContent = `${current.channel} · ${current.sender}`;
    $('#msg-text').textContent = current.text;
    $('#check').disabled = false;
  } catch (e) {
    setErr('Message nahi aa saka. Dobara koshish karein.');
    $('#next').hidden = false;
  } finally {
    busy = false;
  }
}

async function check() {
  if (!current || busy) return;
  busy = true;
  setErr('');
  $('#check').disabled = true;
  try {
    revealed = await api('/api/dojo/check', { token: current.token });
  } catch (e) {
    setErr('Jawab nahi mil saka. "Agla message" dabayein.');
    $('#next').hidden = false;
    busy = false;
    return;
  }
  busy = false;

  const r = revealed;
  paint(current.text, r.highlights);
  const v = $('#verdict');
  v.textContent = (r.is_scam ? '🚨 ' : '✅ ') + r.verdict;
  v.className = r.is_scam ? 'v-scam' : 'v-real';
  $('#headline').textContent = r.headline;
  const ul = $('#reasons');
  ul.textContent = '';
  r.highlights.forEach(h => {
    const li = document.createElement('li');
    li.className = h.kind;
    const b = document.createElement('strong');
    b.textContent = '“' + h.phrase + '” ';
    const tag = document.createElement('em');
    tag.textContent = h.kind === 'red' ? 'Red flag: ' : 'Achi nishani: ';
    li.append(b, tag, h.why);
    ul.append(li);
  });
  $('#seedhi').textContent = r.seedhi_baat;
  $('#kya').textContent = r.kya_karein;
  $('#source').textContent = r.source === 'gemini'
    ? 'Yeh message Gemini ne banaya.' : 'Yeh message pehle se likhe hue messages mein se hai.';
  $('#result').hidden = false;
  $('#next').hidden = false;
  $('#next').focus();

  // Har check par progress bhejo
  try {
    const p = await api('/api/progress', { kind: 'dojo', key: r.id, value: 1 });
    $('#tally').textContent = `Ab tak ${p.dojo} alag messages check kiye.`;
  } catch (e) { /* progress na save ho to bhi jawab dikhta rahe */ }
}

function listen() {
  if (!revealed) return;
  const r = revealed;
  const text = `${r.verdict}. ${r.seedhi_baat} Kya karein: ${r.kya_karein}`;
  if (!('speechSynthesis' in window)) { setErr('Is browser mein bol kar sunana nahi chalta.'); return; }
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = 'hi-IN';  // Roman Urdu ke liye sab se qareeb awaaz
  u.rate = (typeof speechRate === 'number') ? speechRate : 0.9;
  window.speechSynthesis.speak(u);
}

$('#check').onclick = check;
$('#next').onclick = loadNext;
$('#listen').onclick = listen;
api('/api/progress').then(p => {
  if (p.dojo) $('#tally').textContent = `Ab tak ${p.dojo} alag messages check kiye.`;
}).catch(() => {});
loadNext();
