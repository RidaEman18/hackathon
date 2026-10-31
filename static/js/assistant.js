const SUGGESTED = ['Is this message a scam?', 'How do I join a video call?', 'How do I send money safely?', 'What is an OTP?'];

SUGGESTED.forEach(q => {
  const b = document.createElement('button');
  b.textContent = q;
  b.onclick = () => { $('#q').value = q; ask(); };
  $('#suggest').appendChild(b);
});

async function ask() {
  const q = $('#q').value.trim();
  if (!q) { $('#q').focus(); return; }
  const a = await api('/api/assistant', { q });
  $('#a-short').textContent = a.short;
  $('#a-simple').textContent = a.simple;
  $('#a-next').textContent = a.next;
  $('#answer').hidden = false;
}

$('#go').onclick = ask;
$('#q').addEventListener('keydown', e => { if (e.key === 'Enter') ask(); });
$('#a-read').onclick = () => speak(`${$('#a-short').textContent} ${$('#a-simple').textContent} ${$('#a-next').textContent}`);
