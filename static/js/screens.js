// Picture-style mock screens for lessons (generic, not any real brand's logo).
// Each screen: { cls: header colour class, title, html }. Parts have data-id so a step can point at them.
const m = (id, cls, inner) => `<div class="m ${cls}" data-id="${id}">${inner}</div>`;
const row = (id, name, sub) => m(id, 'row', `<span class="av">${name[0]}</span><span><b>${name}</b><br><small>${sub || ''}</small></span>`);
const field = (id, label, val) => m(id, 'field', `<small>${label}</small><b>${val}</b>`);
const bub = (txt, out, id) => m(id || '', 'bub ' + (out ? 'out' : 'in'), txt);

const SCREENS = {
  // WhatsApp-style chat
  wa_chats: { cls: 'green', title: 'Chats', html:
    row('ammi', 'Ammi', 'Beta, khana kha liya?') + row('', 'Ali', 'Ok 👍') + row('', 'Sara', 'Photo') + m('fab', 'fab', '💬') },
  wa_contacts: { cls: 'green', title: 'Select contact', html:
    row('ammi', 'Ammi', 'Hey there!') + row('', 'Ali', 'At work') + row('', 'Sara', 'Available') },
  wa_chat: { cls: 'green', title: 'Ammi', html:
    bub('Salam beta!') + m('', 'spacer', '') + m('', 'bar', m('box', 'input', 'Type a message') + m('send', 'send', '➤')) },
  wa_sent: { cls: 'green', title: 'Ammi', html:
    bub('Salam beta!') + bub('Salam Ammi!', true) + m('ticks', 'ticks', '✓✓ Delivered') +
    m('', 'bar', m('', 'input', 'Type a message') + m('send', 'send', '➤')) },
  // Video call
  vc_link: { cls: 'blue', title: 'Family', html:
    bub('Aaj raat 8 baje video call hai. Link:') + bub('meet.example/ammi-call', false, 'link') },
  vc_allow: { cls: 'dark', title: 'meet.example', html:
    m('', 'dialog', '<b>meet.example wants to use your camera and microphone</b>' +
      m('', 'btns', m('', 'btn2', 'Block') + m('allow', 'btn2 go', 'Allow'))) },
  vc_lobby: { cls: 'dark', title: 'Ready to join?', html:
    m('', 'tile', '🙂<br><small>You</small>') +
    m('', 'tools', m('mic', 'tool muted', '🎤') + m('', 'tool', '📷') + m('join', 'btn2 go', 'Join')) },
  // WhatsApp call
  wac_chat: { cls: 'green', title: 'Ammi', icons: m('', 'bi-i', '📹') + m('call', 'bi-i', '📞'), html:
    bub('Salam beta!') + m('', 'spacer', '') + m('', 'bar', m('', 'input', 'Type a message') + m('', 'send', '➤')) },
  wac_ring: { cls: 'dark', title: 'WhatsApp voice call', html:
    m('', 'callscreen', m('', 'bigav', 'A') + m('who', 'cwho', 'Ammi<br><small>Ringing…</small>') + m('', 'tools', m('', 'tool end', '📞'))) },
  wac_in: { cls: 'dark', title: 'WhatsApp voice call', html:
    m('', 'callscreen', m('', 'bigav', 'A') + m('', 'cwho', 'Ammi<br><small>00:42</small>') +
      m('', 'tools', m('spk', 'tool', '🔊') + m('mic', 'tool muted', '🎤') + m('end', 'tool end', '📞'))) },
  // Normal phone call
  ph_home: { cls: 'dark', title: 'Home screen', html:
    m('', 'apps', m('phoneapp', 'ap', '📞<br><small>Phone</small>') + m('', 'ap', '💬<br><small>Messages</small>') + m('', 'ap', '📷<br><small>Camera</small>') +
      m('', 'ap', '⚙️<br><small>Settings</small>') + m('', 'ap', '🌐<br><small>Browser</small>') + m('', 'ap', '🖼️<br><small>Photos</small>')) },
  ph_contacts: { cls: 'dark', title: 'Phone', html:
    m('', 'tabs2', m('', 't', 'Recents') + m('', 't on', 'Contacts') + m('', 't', 'Keypad')) +
    row('ammi', 'Ammi Jaan', '0300-1234567') + row('', 'Ali', '0301-7654321') + row('', 'Sara', '0302-1112223') },
  ph_keypad: { cls: 'dark', title: 'Phone', html:
    m('', 'tabs2', m('', 't', 'Recents') + m('', 't', 'Contacts') + m('', 't on', 'Keypad')) +
    m('num', 'numdisp', '0300 1234567') +
    m('', 'keys', ['1','2','3','4','5','6','7','8','9','*','0','#'].map(k => `<span class="k">${k}</span>`).join('')) +
    m('', 'tools', m('callbtn', 'tool lg go2', '📞')) },
  ph_incall: { cls: 'dark', title: 'Phone call', html:
    m('', 'callscreen', m('', 'bigav', 'A') + m('', 'cwho', 'Ammi Jaan<br><small>01:05</small>') +
      m('', 'tools', m('', 'tool', '🔊') + m('', 'tool', '🎤') + m('end', 'tool end', '📞'))) },
  ph_incoming: { cls: 'dark', title: 'Incoming call', html:
    m('', 'callscreen', m('', 'bigav', 'A') + m('', 'cwho', 'Ammi Jaan<br><small>Incoming call…</small>') +
      m('', 'tools', m('decline', 'tool end lg', '📞') + m('answer', 'tool go2 lg', '📞'))) },
  // Banking
  bk_store: { cls: 'blue', title: 'App Store', html:
    m('official', 'app', '🏦 <b>Demo Bank</b> <span class="ok">✔ Official</span><br><small>Demo Bank Ltd.</small>') +
    m('', 'app fake', '🏦 <b>Demo Bank Pro</b> <span class="no">⚠</span><br><small>Unknown developer</small>') },
  bk_login: { cls: 'teal', title: 'Demo Bank', html:
    '<p class="c">Enter your PIN</p>' + m('pin', 'pin', '● ● ● ●') + '<p class="c"><small>Only you know your PIN</small></p>' + m('', 'btn2 go wide', 'Login') },
  bk_send: { cls: 'teal', title: 'Send money', html:
    field('name', 'To', 'Ammi Jaan') + field('num', 'Account number', '0300-1234567') + field('', 'Amount', 'Rs 2,000') + m('', 'btn2 go wide', 'Confirm') },
  bk_home: { cls: 'teal', title: 'Demo Bank', html:
    m('', 'field', '<small>Balance</small><b>Rs 25,000</b>') + m('logout', 'btn2 wide', 'Log out') },
  // Scams
  sc_msg: { cls: 'grey', title: 'SMS: Bank', html: m('', 'bub in',
    'Dear customer, your account will be ' + m('hurry', 'inl', 'blocked in 2 hours') + '. ' +
    m('pin', 'inl', 'Send your PIN') + ' to 0300-0000000 or tap ' + m('link', 'inl', 'http://fix-now.example')) },
  sc_card: { cls: 'grey', title: 'Your bank card (back)', html:
    m('', 'card', '<small>Demo Bank</small><br>' + m('num', 'inl', 'Helpline: 111-000-000') + '<br><small>Valid thru 12/29</small>') },
  // Forms
  fm_form: { cls: 'teal', title: 'Online form', html:
    field('name', 'Name', 'Ayesha Khan') + field('cnic', 'CNIC', '42101-1234567-1') + field('mobile', 'Mobile', '0300-1234567') + m('submit', 'btn2 go wide', 'Submit') },
  // Passwords
  pw_phrase: { cls: 'teal', title: 'New password', html:
    m('field', 'field', '<small>Password</small><b>MeraGharKarachiMeinHai</b>') + m('', 'strong', 'Strong ✔') },
  pw_bad: { cls: 'teal', title: 'New password', html:
    m('field', 'field', '<small>Password</small><b>03-03-1960</b>') + m('', 'weak', 'Weak ✖ Easy to guess') },
  pw_two: { cls: 'teal', title: 'My accounts', html:
    field('email', 'Email', 'Chai-Ki-Pyali-7') + field('bank', 'Bank', 'Mera-Naya-Ghar-88') },
  pw_note: { cls: 'grey', title: 'My notebook', html:
    m('book', 'book', '<b>Passwords</b><br>Email: Chai-Ki-Pyali-7<br>Bank: Mera-Naya-Ghar-88<br><small>Keep at home</small>') },
};

// Draw the picture for one step and point at the right part.
function renderScreen(step) {
  const box = document.getElementById('screen');
  const tip = document.getElementById('tip');
  if (!step.screen && !step.shot) { box.hidden = true; tip.hidden = true; return; }
  box.hidden = false;
  if (step.shot) {
    const b = step.box || [0, 0, 100, 100];
    box.innerHTML = `<div class="shot"><img src="/static/images/lessons/${step.shot}" alt="${step.tip || 'App screenshot'}">` +
      `<div class="ring" style="left:${b[0]}%;top:${b[1]}%;width:${b[2]}%;height:${b[3]}%"></div></div>`;
  } else {
    const sc = SCREENS[step.screen];
    box.innerHTML = `<div class="mock"><div class="mbar ${sc.cls}"><span>${sc.title}</span><span class="bi">${sc.icons || ''}</span></div><div class="mbody">${sc.html}</div></div>`;
    const ids = [].concat(step.spot || []);
    if (ids.includes('all')) box.querySelector('.mbody').classList.add('spot');
    ids.forEach(id => box.querySelectorAll(`[data-id="${id}"]`).forEach(el => el.classList.add('spot')));
  }
  tip.hidden = !step.tip;
  tip.textContent = step.tip ? '👆 ' + step.tip : '';
}
