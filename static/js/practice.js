// Practice rooms. Each step expects one action (act).
// Bank has an Undo button. Video call uses the real browser camera/mic permission.
// Needs $, $$, api(), qadamSpeak() from script.js.
const ROOMS = {
  bank: { title: 'Demo Bank', undo: true, app: true, steps: [
    { coach: 'Type the PIN 1234 in the box, then tap "Login".', hint: 'The demo PIN is 1234. In real life, keep your PIN secret.' },
    { coach: 'Tap "Show balance" to see how much money you have.', hint: 'It is the button just under your account number.' },
    { coach: 'Tap "Send money". Choose Ammi, type 2000 as the amount, then tap "Continue".', hint: 'Choose Ammi from the list. Type only numbers: 2000.' },
    { coach: 'Read the name and amount on this screen. If it says Ammi and Rs 2,000, tap "Confirm".', hint: 'Always check the name before you tap Confirm. If it is wrong, tap "Edit".' },
    { coach: 'Type the 6-digit code from your phone (482916) and tap "Verify".', hint: 'The bank sends this code by SMS. Never tell it to anyone, even if they say they are from the bank.' },
    { coach: 'Tap "Back to home" if you need to, then tap "Logout".', hint: 'Logout is the last button on the home screen. Always log out when you finish.' }] },
  form: { title: 'Demo Form', steps: [
    { act: 'name', coach: 'Type your name in the Name box, then tap outside it.', hint: 'Use any name. It is only practice.', ok: 'Good. In real forms, match your ID card.' },
    { act: 'phone', coach: 'Type a phone number in the Phone box, then tap outside it.', hint: 'Any number works here.', ok: 'Phone saved in the demo.' },
    { act: 'submit', coach: 'Read it again, then tap "Submit" once.', hint: 'Tap only once.', ok: "Submitted. You didn't break anything." }],
    ui: [['name', 'Name', 'input'], ['phone', 'Phone number', 'input'], ['submit', 'Submit']] },
  video: { title: 'Demo Video Call', steps: [
    { act: 'allow', coach: 'Tap "Allow camera and mic". Your browser will ask you. Tap Allow.', hint: 'This lets others see and hear you. It is the first button.', ok: 'Allowed. You can see yourself now.' },
    { act: 'mute', coach: 'Tap "Mute" to turn your mic off.', hint: 'Mute means nobody can hear you.', ok: 'Muted. Nobody can hear you.' },
    { act: 'unmute', coach: 'Tap "Unmute" so they can hear you.', hint: 'Unmute is the third button.', ok: 'Unmuted. They can hear you.' },
    { act: 'join', coach: 'Tap "Join call".', hint: 'Last button.', ok: "You joined. You didn't break anything." }],
    ui: [['allow', 'Allow camera and mic'], ['mute', 'Mute'], ['unmute', 'Unmute'], ['join', 'Join call']] },
};

let room = null, step = 0, stream = null, busy = false;

// ---------------------------------------------------------------- Bank app
// A small working demo bank. Nothing is real. The coach only watches progress,
// so the user can tap anything, make mistakes and use Back, Edit or Undo.
const PIN = '1234', OTP = '482916', TASK = { to: 'ammi', amt: 2000 };
const BENEFS = [
  { id: 'ammi', name: 'Ammi', acct: '4821' },
  { id: 'rehman', name: 'Abdul Rehman', acct: '7730' },
  { id: 'ayesha', name: 'Ayesha Khan', acct: '1195' },
];
const money = n => 'Rs ' + Number(n).toLocaleString('en-US');
let bank = null, bankHist = [];

function bankInit() {
  bank = { screen: 'login', bal: 25000, shown: false, to: '', amt: '', note: '', amtNum: 0,
    err: '', msg: '', paid: false, ref: '',
    tx: [{ d: '29 Oct', t: 'Grocery store', a: -1850 }, { d: '27 Oct', t: 'Received from Bhai', a: 5000 }, { d: '25 Oct', t: 'Mobile load', a: -500 }] };
  bankHist = [];
}
function snap() { bankHist.push(JSON.stringify({ bank, step })); }
function say(msg, kind) { const o = $('#out'); o.className = kind ? 'out kind' : 'out'; o.textContent = msg; }
// Move the coach forward (never backwards) when the user reaches step i.
function adv(i, msg) { if (step <= i) { step = i + 1; if (msg) say(msg); } }
function benef() { return BENEFS.find(b => b.id === bank.to); }
function matchesTask() { return bank.to === TASK.to && bank.amtNum === TASK.amt; }
function h(tag, cls, text, kids) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  (kids || []).forEach(k => e.appendChild(k));
  return e;
}
function bkBtn(label, fn, primary) {
  const b = h('button', primary ? 'bk-primary' : '', label);
  b.type = 'button'; b.onclick = fn; return b;
}
function bkField(label, type, value, onInput, extra) {
  const id = 'bk-' + label.toLowerCase().replace(/\W+/g, '-');
  const wrap = h('div');
  const l = h('label', 'bk-lbl', label); l.htmlFor = id;
  const i = document.createElement('input');
  i.id = id; i.type = type; i.value = value || '';
  Object.entries(extra || {}).forEach(([k, v]) => i.setAttribute(k, v));
  i.addEventListener('input', () => onInput(i.value));
  wrap.append(l, i); return { wrap, input: i };
}
function bkErr() { return bank.err ? h('div', 'bk-err', bank.err) : null; }

function renderBank() {
  const root = $('#ui'); root.innerHTML = '';
  const app = h('div', 'bk');
  const S = bank.screen;
  app.appendChild(h('div', 'bk-head', null, [h('strong', '', 'Demo Bank'), h('span', '', S === 'login' ? 'Secure login' : 'Account ending 6150')]));
  const add = (...n) => n.filter(Boolean).forEach(x => app.appendChild(x));

  if (S === 'login') {
    add(bank.msg ? h('div', 'bk-ok', bank.msg) : null, h('p', 'bk-sub', 'Welcome. Please log in to see your account.'));
    const f = bkField('PIN', 'password', '', () => {}, { inputmode: 'numeric', maxlength: '4', autocomplete: 'off', placeholder: 'Demo PIN is 1234' });
    add(f.wrap, bkErr(), bkBtn('Login', () => {
      const v = f.input.value.trim();
      if (!v) { bank.err = 'Please type your PIN.'; return renderBank(); }
      if (v !== PIN) { bank.err = 'Wrong PIN. For this practice the PIN is 1234.'; return renderBank(); }
      snap(); bank.screen = 'home'; bank.err = ''; bank.msg = '';
      adv(0, 'Logged in. In real life, never tell your PIN to anyone.');
      renderBank(); show();
    }, true));
  }

  if (S === 'home') {
    const card = h('div', 'bk-card', null, [
      h('div', 'bk-sub', 'Hello, Demo User'),
      h('div', 'bk-sub', 'Savings account ending 6150'),
      h('div', 'bk-bal', bank.shown ? money(bank.bal) : 'Rs ••••••'),
      bkBtn(bank.shown ? 'Hide balance' : 'Show balance', () => {
        snap(); bank.shown = !bank.shown;
        if (bank.shown) adv(1, 'Your balance is ' + money(bank.bal) + '. Only show it when nobody is looking.');
        renderBank(); show();
      }),
    ]);
    const tx = h('div', 'bk-card', null, [h('div', 'bk-lbl', 'Recent transactions')]);
    bank.tx.slice(0, 4).forEach(t => tx.appendChild(h('div', 'bk-row', null, [
      h('span', '', t.d + '  ' + t.t),
      h('span', t.a < 0 ? 'bk-neg' : 'bk-pos', (t.a < 0 ? '- ' : '+ ') + money(Math.abs(t.a))),
    ])));
    add(card, bkBtn('Send money', () => go('send'), true), tx, bkBtn('Logout', () => {
      snap(); bank.screen = 'login'; bank.shown = false; bank.err = '';
      bank.msg = 'You are logged out safely.';
      adv(5, 'Logged out. Always log out when you finish, especially on a shared phone.');
      renderBank(); show();
      if (step >= ROOMS.bank.steps.length) api('/api/progress', { kind: 'practice', key: 'bank', value: 1 }).catch(() => {});
    }));
  }

  if (S === 'send') {
    add(h('h3', 'bk-h3', 'Send money'));
    const sel = document.createElement('select'); sel.id = 'bk-to'; sel.setAttribute('aria-label', 'Send to');
    sel.appendChild(new Option('Choose who to send to', ''));
    BENEFS.forEach(b => sel.appendChild(new Option(b.name + '  (account ending ' + b.acct + ')', b.id)));
    sel.value = bank.to; sel.onchange = () => { bank.to = sel.value; };
    const l = h('label', 'bk-lbl', 'Send to'); l.htmlFor = 'bk-to';
    const amt = bkField('Amount (Rs)', 'text', bank.amt, v => { bank.amt = v; }, { inputmode: 'numeric', placeholder: 'For example 2000' });
    const note = bkField('Note (optional)', 'text', bank.note, v => { bank.note = v; }, { maxlength: '30', placeholder: 'For example: monthly help' });
    add(h('div', '', null, [l, sel]), amt.wrap, note.wrap, bkErr(), h('div', 'bk-btns', null, [
      bkBtn('Continue', () => {
        const n = Number(String(bank.amt).replace(/,/g, '').trim());
        if (!bank.to) { bank.err = 'Please choose who to send money to.'; return renderBank(); }
        if (!/^\d+$/.test(String(bank.amt).replace(/,/g, '').trim())) { bank.err = 'Type the amount in numbers only, like 2000.'; return renderBank(); }
        if (n <= 0) { bank.err = 'The amount must be more than zero.'; return renderBank(); }
        if (n > bank.bal) { bank.err = 'Not enough balance. You have ' + money(bank.bal) + '.'; return renderBank(); }
        snap(); bank.amtNum = n; bank.err = ''; bank.screen = 'review';
        if (matchesTask()) adv(2, 'Now read the name and amount carefully.');
        renderBank(); show();
      }, true),
      bkBtn('Back', () => go('home')),
    ]));
  }

  if (S === 'review') {
    const b = benef();
    add(h('h3', 'bk-h3', 'Please check carefully'), h('div', 'bk-card', null, [
      h('div', 'bk-row', null, [h('span', '', 'To'), h('strong', '', b.name)]),
      h('div', 'bk-row', null, [h('span', '', 'Account ending'), h('strong', '', b.acct)]),
      h('div', 'bk-row', null, [h('span', '', 'Amount'), h('strong', '', money(bank.amtNum))]),
      bank.note ? h('div', 'bk-row', null, [h('span', '', 'Note'), h('strong', '', bank.note)]) : null,
    ].filter(Boolean)), h('div', 'bk-warn', 'Money sent to a wrong person is very hard to get back. Check the name once more.'), h('div', 'bk-btns', null, [
      bkBtn('Confirm', () => {
        if (!matchesTask()) return say('For this practice, send Rs 2,000 to Ammi. Tap "Edit" and fix it.', true);
        snap(); bank.screen = 'otp'; bank.err = '';
        adv(3, 'The bank sent you a code by SMS.');
        renderBank(); show();
      }, true),
      bkBtn('Edit', () => go('send')),
    ]));
  }

  if (S === 'otp') {
    add(h('h3', 'bk-h3', 'Enter the code'), h('p', 'bk-sub', 'We sent a 6-digit code to your phone ending 0142.'),
      h('div', 'bk-sms', 'SMS from DEMO BANK: Your code is 482916. Do not share it with anyone.'));
    const f = bkField('6-digit code', 'text', '', () => {}, { inputmode: 'numeric', maxlength: '6', autocomplete: 'off', placeholder: 'Type the code' });
    add(f.wrap, h('div', 'bk-warn', 'Real bank staff will never ask for this code. If anyone asks, it is a scam.'), bkErr(), h('div', 'bk-btns', null, [
      bkBtn('Verify', () => {
        const v = f.input.value.trim();
        if (!v) { bank.err = 'Please type the 6-digit code.'; return renderBank(); }
        if (v !== OTP) { bank.err = 'That code is wrong. For this practice it is 482916.'; return renderBank(); }
        snap();
        const b = benef();
        bank.bal -= bank.amtNum; bank.paid = true; bank.err = '';
        bank.ref = 'TXN' + (480000 + Math.floor(Math.random() * 9999));
        bank.tx.unshift({ d: new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }), t: 'Sent to ' + b.name, a: -bank.amtNum });
        bank.screen = 'done';
        adv(4, "Sent " + money(bank.amtNum) + ". You didn't break anything.");
        renderBank(); show();
      }, true),
      bkBtn('Cancel', () => go('home')),
    ]));
  }

  if (S === 'done') {
    const b = benef();
    add(h('div', 'bk-tick', '✅'), h('h3', 'bk-h3', 'Payment sent'), h('div', 'bk-card', null, [
      h('div', 'bk-row', null, [h('span', '', 'Amount'), h('strong', '', money(bank.amtNum))]),
      h('div', 'bk-row', null, [h('span', '', 'To'), h('strong', '', b.name + ' (' + b.acct + ')')]),
      h('div', 'bk-row', null, [h('span', '', 'Reference'), h('strong', '', bank.ref)]),
      h('div', 'bk-row', null, [h('span', '', 'New balance'), h('strong', '', money(bank.bal))]),
    ]), h('p', 'bk-sub', 'Keep the reference number if you need to ask the bank about this payment.'),
      bkBtn('Back to home', () => go('home'), true));
  }
  root.appendChild(app);
}
function go(screen) { snap(); bank.err = ''; bank.screen = screen; renderBank(); show(); }

function bankUndo() {
  if (!bankHist.length) return;
  const wasPaid = bank.paid;
  const s = JSON.parse(bankHist.pop());
  bank = s.bank; step = s.step;
  renderBank(); show();
  say(wasPaid && !bank.paid
    ? 'Undone here in practice. Real banks usually cannot take back a payment once it is sent, so always check the name first.'
    : 'Undone. You went back one step and nothing was sent.', true);
}


function stopStream() {
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
  const v = $('#preview');
  v.srcObject = null; v.hidden = true;
}

// Does the real browser work for this action? Returns { ok, msg }.
async function realAction(act) {
  if (room !== 'video') return { ok: true };
  if (act === 'allow') {
    if (!window.isSecureContext || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      return { ok: true, msg: 'This page cannot open the camera, so we will pretend.' };
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      const v = $('#preview');
      v.srcObject = stream; v.hidden = false;
      return { ok: true };
    } catch (e) {
      if (e.name === 'NotFoundError' || e.name === 'OverconstrainedError') {
        return { ok: true, msg: 'No camera or mic found, so we will pretend. You can still practise.' };
      }
      return { ok: false, msg: 'Permission was blocked. That is okay. Click the camera icon in the address bar, choose Allow, then tap the button again.' };
    }
  }
  if (stream && act === 'mute') stream.getAudioTracks().forEach(t => (t.enabled = false));
  if (stream && act === 'unmute') stream.getAudioTracks().forEach(t => (t.enabled = true));
  return { ok: true };
}

function show() {
  const r = ROOMS[room], done = step >= r.steps.length;
  $('#coach-text').textContent = done ? 'Well done! You finished this room.' : r.steps[step].coach;
  $('#count').textContent = done ? '' : `Step ${step + 1} of ${r.steps.length}`;
  $('#hint').hidden = true;
  $('#stuck').hidden = done;
  $('#again').hidden = !done;
  $('#undo').hidden = !(r.undo && (r.app ? bankHist.length > 0 : step > 0));
}

function start(name) {
  stopStream();
  room = name; step = 0;
  $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.room === name));
  $('#room').hidden = false; $('#pick').hidden = true;
  $('#room-title').textContent = ROOMS[name].title;
  $('#out').textContent = ''; $('#out').className = 'out';
  $('#ui').innerHTML = '';
  if (ROOMS[name].app) { bankInit(); renderBank(); show(); return; }
  ROOMS[name].ui.forEach(([act, label, kind]) => {
    const el = document.createElement(kind === 'input' ? 'input' : 'button');
    if (kind === 'input') {
      el.placeholder = label; el.setAttribute('aria-label', label);
      el.addEventListener('change', () => {
        if (el.value.trim()) return doAct(act);
        const out = $('#out');
        out.className = 'out kind';
        out.textContent = 'The box is empty. Type anything, it is only practice.';
      });
    } else { el.textContent = label; el.addEventListener('click', () => doAct(act)); }
    $('#ui').appendChild(el);
  });
  show();
}

async function doAct(act) {
  const steps = ROOMS[room].steps;
  if (step >= steps.length || busy) return;
  const out = $('#out');
  if (act !== steps[step].act) {
    out.className = 'out kind';
    out.textContent = 'That is okay. Mistakes help us learn, and nothing here is real. Right now: ' + steps[step].coach;
    return;
  }
  busy = true;
  const r = await realAction(act);
  busy = false;
  if (!r.ok) { out.className = 'out kind'; out.textContent = r.msg; return; }
  out.className = 'out';
  out.textContent = steps[step].ok + (r.msg ? ' ' + r.msg : '');
  step++;
  if (step >= steps.length) {
    stopStream();
    // Progress save must never break the room if the network fails.
    api('/api/progress', { kind: 'practice', key: room, value: 1 }).catch(() => {});
  }
  show();
}

$$('.tab').forEach(t => (t.onclick = () => { location.hash = t.dataset.room; }));
$('#stuck').onclick = () => { const h = $('#hint'); h.textContent = ROOMS[room].steps[step].hint; h.hidden = false; };
$('#again').onclick = () => start(room);
$('#listen').onclick = () => {
  const t = $('#coach-text').textContent;
  if (t && window.qadamSpeak) window.qadamSpeak(t);
};
$('#undo').onclick = () => {
  if (ROOMS[room].app) return bankUndo();
  if (step === 0) return;
  const wasDone = step >= ROOMS[room].steps.length;
  step--;
  $('#out').className = 'out kind';
  $('#out').textContent = wasDone
    ? 'Undone here in practice. Real banks usually cannot take back a payment once it is sent, so always check the name first.'
    : 'Undone. Nothing was sent and your money is safe.';
  show();
};

// Open a room from the link, e.g. /practice#bank (the voice assistant can use this)
function openFromHash() {
  const name = location.hash.slice(1);
  if (ROOMS[name] && name !== room) start(name);
}
window.addEventListener('hashchange', openFromHash);
window.addEventListener('beforeunload', stopStream);
openFromHash();