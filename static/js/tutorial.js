const T = window.TUTORIAL;
let i = 0;

function render() {
  const s = T.steps[i];
  const simple = document.body.classList.contains('simple');
  const last = i === T.steps.length - 1;
  $('#num').textContent = i + 1;
  $('#text').textContent = simple ? s.simple : s.text;
  $('#dots').innerHTML = T.steps.map((_, k) => `<span class="pd ${k < i ? 'done' : k === i ? 'now' : ''}"></span>`).join('');
  $('#back').disabled = i === 0;
  $('#next').textContent = last ? 'I finished this lesson' : 'Next ▶';
  renderScreen(s);
}

$('#back').onclick = () => { if (i > 0) { i--; render(); } };
$('#next').onclick = async () => {
  if (i < T.steps.length - 1) { i++; render(); return; }
  await api('/api/progress', { kind: 'tutorial', key: T.slug, value: 1 });
  location.href = '/path';
};
$('#read').onclick = () => speak($('#text').textContent + ' ' + (T.steps[i].tip || ''));
document.addEventListener('qsimple', render);
render();
