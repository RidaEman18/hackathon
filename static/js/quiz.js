const Q = window.QUIZ;
const OPTS = ['Scam', 'Real', "Not sure, I'll call the bank"];
let n = 0, score = 0, locked = false;
const box = $('#quiz');

function esc(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }

function render() {
  if (n >= Q.length) return result();
  const q = Q[n];
  locked = false;
  box.innerHTML = `<p class="muted">Question ${n + 1} of ${Q.length}. Score: ${score}</p>
    <div class="phone-bubble"><small>${esc(q.from)}</small>${esc(q.msg)}</div>
    <div class="opts">${OPTS.map((o, i) => `<button data-i="${i}">${esc(o)}</button>`).join('')}</div>
    <div id="fb"></div>`;
  $$('.opts button', box).forEach(b => b.onclick = () => pick(+b.dataset.i));
}

function pick(i) {
  if (locked) return;
  locked = true;
  const q = Q[n], ok = i === q.answer;
  if (ok) score++;
  $$('.opts button', box).forEach(b => {
    if (+b.dataset.i === q.answer) b.classList.add('right');
    else if (+b.dataset.i === i) b.classList.add('wrong');
  });
  $('#fb').innerHTML = `<div class="fb"><strong>${ok ? 'Well done!' : 'Not quite, and that is okay.'}</strong> ${esc(q.why)}</div>
    <button class="btn" id="nx">${n === Q.length - 1 ? 'See my result' : 'Next question'}</button>`;
  $('#nx').onclick = () => { n++; render(); };
}

async function result() {
  const pct = Math.round(score / Q.length * 100);
  await api('/api/progress', { kind: 'quiz', key: 'scam', value: pct });
  box.innerHTML = `<h3>You got ${score} out of ${Q.length}</h3>
    <p>${pct >= 80 ? 'Great eye! You spot scams well.' : 'Good start. Read the red flags and try again.'}</p>
    <button class="btn" id="again">Try again</button> <a class="btn alt" href="/path">See my path</a>`;
  $('#again').onclick = () => { n = 0; score = 0; render(); };
}

render();
