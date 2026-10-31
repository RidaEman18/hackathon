// English voice navigation. Every destination below is an existing Flask route.
(() => {
  const startButton = document.querySelector('#voice-start');
  if (!startButton) return;

  const status = document.querySelector('#voice-status');
  const heard = document.querySelector('#voice-heard');
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  const commands = [
    { words: ['my path', 'progress', 'dashboard'], url: '/path' },
    { words: ['practice', 'practice room'], url: '/practice' },
    { words: ['safety', 'scam', 'fraud'], url: '/safety' },
    { words: ['helper', 'help', 'assistant'], url: '/assistant' },
    { words: ['learn', 'lessons'], url: '/learn' },
    { words: ['video call', 'video lesson'], url: '/learn/video-call' },
    { words: ['banking', 'bank lesson'], url: '/learn/banking' },
    { words: ['whatsapp', 'whatsapp lesson'], url: '/learn/whatsapp' },
    { words: ['password', 'password lesson'], url: '/learn/passwords' },
    { words: ['online form', 'forms', 'form lesson'], url: '/learn/forms' },
    { words: ['scam lesson', 'spot a scam'], url: '/learn/scams' },
    { words: ['home'], url: '/' },
  ];

  startButton.addEventListener('click', () => {
    if (!SpeechRecognition) {
      status.textContent = 'Voice recognition is unavailable in this browser. Please use Chrome or Edge, or use the navigation menu.';
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    startButton.disabled = true;
    status.textContent = 'Listening… say a page name.';
    recognition.onresult = event => {
      const transcript = event.results[0][0].transcript.toLowerCase().trim();
      heard.textContent = `You said: ${transcript}`;
      const match = commands.find(command => command.words.some(word => transcript.includes(word)));
      if (match) {
        status.textContent = `Opening ${match.url === '/' ? 'Home' : match.url.replaceAll('/', ' ').trim()}…`;
        window.location.href = match.url;
      } else {
        status.textContent = 'I did not understand. Try saying Learn, Practice, Safety, My Path, or Helper.';
      }
    };
    recognition.onerror = event => {
      status.textContent = event.error === 'not-allowed'
        ? 'Microphone permission was blocked. Allow microphone access in your browser.'
        : `Microphone issue: ${event.error}. Please try again.`;
    };
    recognition.onend = () => { startButton.disabled = false; };
    try { recognition.start(); }
    catch (error) { startButton.disabled = false; status.textContent = 'Could not start the microphone. Try again.'; }
  });
})();
