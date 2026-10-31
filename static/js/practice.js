// Three simulated rooms. Each step expects one action (act).
const ROOMS = {
  bank: { title: 'Demo Bank', steps: [
    { act: 'pin', coach: 'Tap "Enter PIN" to log in.', hint: 'It is the first button.', ok: 'Logged in. Your PIN stays secret in real life.' },
    { act: 'balance', coach: 'Tap "Check balance".', hint: 'It shows how much money you have.', ok: 'Your demo balance is Rs 25,000.' },
    { act: 'send', coach: 'Tap "Send money to Ammi".', hint: 'Look for the word Send.', ok: 'Now read the name and number twice.' },
    { act: 'confirm', coach: 'The name is right. Tap "Confirm".', hint: 'Last button.', ok: 'Sent! You did not break anything.' }],
    ui: [['pin', 'Enter PIN'], ['balance', 'Check balance'], ['send', 'Send money to Ammi'], ['confirm', 'Confirm']] },
  form: { title: 'Demo Form', steps: [
    { act: 'name', coach: 'Type your name in the Name box, then tap outside it.', hint: 'Use any name. It is only practice.', ok: 'Good. In real forms, match your ID card.' },
    { act: 'phone', coach: 'Type a phone number in the Phone box.', hint: 'Any number works here.', ok: 'Phone saved in the demo.' },
    { act: 'submit', coach: 'Read it again, then tap "Submit" once.', hint: 'Tap only once.', ok: 'Submitted. You did not break anything.' }],
    ui: [['name', 'Name', 'input'], ['phone', 'Phone number', 'input'], ['submit', 'Submit']] },
  video: { title: 'Demo Video Call', steps: [
    { act: 'allow', coach: 'Tap "Allow camera and mic".', hint: 'This lets others see and hear you.', ok: 'Allowed. You can see yourself now.' },
    { act: 'mute', coach: 'Tap "Mute" to turn your mic off.', hint: 'Mute means nobody can hear you.', ok: 'Muted. Nobody can hear you.' },
    { act: 'unmute', coach: 'Tap "Unmute" so they can hear you.', hint: 'Unmute is the third button.', ok: 'Unmuted. They can hear you.' },
    { act: 'join', coach: 'Tap "Join call".', hint: 'Last button.', ok: 'You joined. You did not break anything.' }],
    ui: [['allow', 'Allow camera and mic'], ['mute', 'Mute'], ['unmute', 'Unmute'], ['join', 'Join call']] },
};

let room = null, step = 0;

function show() {
  const s = ROOMS[room].steps[step];
  const done = step >= ROOMS[room].steps.length;
  $('#coach-text').textContent = done ? 'Well done! You finished this room.' : s.coach;
  $('#count').textContent = done ? '' : `Step ${step + 1} of ${ROOMS[room].steps.length}`;
  $('#hint').hidden = true;
  $('#stuck').hidden = done;
  $('#again').hidden = !done;
}

function start(r) {
  room = r; step = 0;
  $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.room === r));
  $('#room').hidden = false; $('#pick').hidden = true;
  $('#room-title').textContent = ROOMS[r].title;
  $('#out').textContent = ''; $('#out').className = 'out';
  $('#ui').innerHTML = '';
  ROOMS[r].ui.forEach(([act, label, kind]) => {
    const el = document.createElement(kind === 'input' ? 'input' : 'button');
    if (kind === 'input') { el.placeholder = label; el.setAttribute('aria-label', label); el.addEventListener('change', () => act_(act)); }
    else { el.textContent = label; el.addEventListener('click', () => act_(act)); }
    $('#ui').appendChild(el);
  });
  show();
}

function act_(act) {
  const steps = ROOMS[room].steps;
  if (step >= steps.length) return;
  const out = $('#out');
  if (act === steps[step].act) {
    out.className = 'out'; out.textContent = steps[step].ok; step++;
    if (step >= steps.length) api('/api/progress', { kind: 'practice', key: room, value: 1 });
    show();
  } else {
    out.className = 'out kind';
    out.textContent = 'That is okay. Mistakes help us learn, and nothing here is real. Right now: ' + steps[step].coach;
  }
}

$$('.tab').forEach(t => t.onclick = () => start(t.dataset.room));
$('#stuck').onclick = () => { const h = $('#hint'); h.textContent = ROOMS[room].steps[step].hint; h.hidden = false; };
$('#again').onclick = () => start(room);
