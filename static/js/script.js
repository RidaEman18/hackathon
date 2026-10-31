// Shared accessibility tools and speech controls for qadam.
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

async function api(path, body) {
  const r = await fetch(path, {
    method: body ? 'POST' : 'GET',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error('Request failed. Please try again.');
  return r.json();
}

let speechRate = 0.9;
function speak(text) {
  if (!('speechSynthesis' in window)) {
    const status = $('#speech-status');
    if (status) status.textContent = 'Read aloud is not supported in this browser.';
    return;
  }
  const cleanText = String(text || '').trim();
  if (!cleanText) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.lang = 'en-US';
  utterance.rate = speechRate;
  utterance.onstart = () => { if ($('#speech-status')) $('#speech-status').textContent = 'Reading…'; };
  utterance.onend = () => { if ($('#speech-status')) $('#speech-status').textContent = 'Finished reading.'; };
  utterance.onerror = () => { if ($('#speech-status')) $('#speech-status').textContent = 'Could not read this text. Please try again.'; };
  window.speechSynthesis.speak(utterance);
}
window.qadamSpeak = speak;

// Text size
let size = Number(localStorage.getItem('q-size')) || 20;
function setSize(n) {
  size = Math.min(28, Math.max(16, n));
  document.documentElement.style.fontSize = size + 'px';
  localStorage.setItem('q-size', size);
}
setSize(size);
if ($('#a-minus')) $('#a-minus').onclick = () => setSize(size - 2);
if ($('#a-plus')) $('#a-plus').onclick = () => setSize(size + 2);

// Simple words
function applySimple() {
  const on = document.body.classList.contains('simple');
  if ($('#simple-toggle')) $('#simple-toggle').setAttribute('aria-pressed', String(on));
  $$('[data-simple]').forEach(e => {
    if (!e.dataset.full) e.dataset.full = e.textContent;
    e.textContent = on ? e.dataset.simple : e.dataset.full;
  });
  document.dispatchEvent(new Event('qsimple'));
}
if (localStorage.getItem('q-simple') === '1') document.body.classList.add('simple');
if ($('#simple-toggle')) {
  $('#simple-toggle').onclick = () => {
    document.body.classList.toggle('simple');
    localStorage.setItem('q-simple', document.body.classList.contains('simple') ? '1' : '0');
    applySimple();
  };
}
applySimple();

// Read the current page and control playback.
if ($('#read-page')) $('#read-page').onclick = () => speak($('#main')?.innerText || '');
if ($('#speech-rate')) $('#speech-rate').onchange = e => { speechRate = Number(e.target.value) || 0.9; };
if ($('#speech-pause')) $('#speech-pause').onclick = () => window.speechSynthesis?.pause();
if ($('#speech-resume')) $('#speech-resume').onclick = () => window.speechSynthesis?.resume();
if ($('#speech-stop')) $('#speech-stop').onclick = () => {
  window.speechSynthesis?.cancel();
  if ($('#speech-status')) $('#speech-status').textContent = 'Reading stopped.';
};
