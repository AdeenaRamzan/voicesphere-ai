/**
 * VoiceSphere Embeddable Widget
 * Drop this on any website:
 *
 *   <script src="https://your-domain.com/widget.js"
 *           data-agent-name="Ava"
 *           data-greeting="Hi! Ask me anything."
 *           data-color="#4f46e5"
 *           data-position="bottom-right"></script>
 *
 * Runs fully isolated in a Shadow DOM so it never clashes with the host
 * site's CSS. Talks to the same backend as the main app (auto language
 * detection included) via /api/transcribe, /api/chat, /api/tts.
 */
(function () {
  var scriptTag = document.currentScript || (function () {
    var scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  var API_BASE = scriptTag.getAttribute('data-api-base') || new URL(scriptTag.src).origin;
  var AGENT_NAME = scriptTag.getAttribute('data-agent-name') || 'VoiceSphere';
  var GREETING = scriptTag.getAttribute('data-greeting') || "Hi! Click the mic or type a message.";
  var ACCENT = scriptTag.getAttribute('data-color') || '#4f46e5';
  var POSITION = scriptTag.getAttribute('data-position') || 'bottom-right'; // bottom-right | bottom-left

  var host = document.createElement('div');
  host.id = 'voicesphere-widget-host';
  document.body.appendChild(host);
  var shadow = host.attachShadow({ mode: 'open' });

  var side = POSITION === 'bottom-left' ? 'left' : 'right';

  shadow.innerHTML =
    '<style>' +
    ':host { all: initial; }' +
    '* { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }' +
    '.vs-launcher { position: fixed; bottom: 24px; ' + side + ': 24px; width: 60px; height: 60px; border-radius: 50%; ' +
      'background: ' + ACCENT + '; box-shadow: 0 6px 20px rgba(0,0,0,0.25); border: none; cursor: pointer; ' +
      'display: flex; align-items: center; justify-content: center; z-index: 999999; transition: transform 0.15s ease; }' +
    '.vs-launcher:hover { transform: scale(1.06); }' +
    '.vs-panel { position: fixed; bottom: 96px; ' + side + ': 24px; width: 340px; max-width: calc(100vw - 32px); height: 480px; ' +
      'background: #0f1220; border-radius: 16px; box-shadow: 0 12px 40px rgba(0,0,0,0.35); display: none; flex-direction: column; ' +
      'overflow: hidden; z-index: 999999; border: 1px solid rgba(255,255,255,0.08); }' +
    '.vs-panel.open { display: flex; }' +
    '.vs-header { background: ' + ACCENT + '; color: #fff; padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; }' +
    '.vs-header-title { font-size: 14px; font-weight: 600; }' +
    '.vs-header-sub { font-size: 11px; opacity: 0.85; }' +
    '.vs-close { background: transparent; border: none; color: #fff; cursor: pointer; font-size: 18px; line-height: 1; padding: 4px; }' +
    '.vs-feed { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; }' +
    '.vs-bubble { max-width: 85%; padding: 9px 12px; border-radius: 12px; font-size: 13px; line-height: 1.4; color: #e7e9f5; }' +
    '.vs-bubble.user { align-self: flex-end; background: ' + ACCENT + '; color: #fff; border-bottom-right-radius: 3px; }' +
    '.vs-bubble.assistant { align-self: flex-start; background: rgba(255,255,255,0.08); border-bottom-left-radius: 3px; }' +
    '.vs-status { font-size: 11px; color: #9aa0b4; padding: 0 14px 6px; min-height: 14px; }' +
    '.vs-inputbar { display: flex; gap: 8px; padding: 10px; border-top: 1px solid rgba(255,255,255,0.08); }' +
    '.vs-text-input { flex: 1; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; ' +
      'padding: 9px 14px; color: #fff; font-size: 13px; outline: none; }' +
    '.vs-mic-btn, .vs-send-btn { width: 36px; height: 36px; border-radius: 50%; border: none; cursor: pointer; ' +
      'display: flex; align-items: center; justify-content: center; flex-shrink: 0; background: ' + ACCENT + '; color: #fff; }' +
    '.vs-mic-btn.recording { background: #ef4444; animation: vs-pulse 1s infinite; }' +
    '@keyframes vs-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.6; } }' +
    '</style>' +
    '<button class="vs-launcher" id="vsLauncher" aria-label="Open voice assistant">' +
      '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
        '<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>' +
        '<path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line>' +
      '</svg>' +
    '</button>' +
    '<div class="vs-panel" id="vsPanel">' +
      '<div class="vs-header">' +
        '<div><div class="vs-header-title">' + AGENT_NAME + '</div><div class="vs-header-sub">Voice + text assistant</div></div>' +
        '<button class="vs-close" id="vsClose">&times;</button>' +
      '</div>' +
      '<div class="vs-feed" id="vsFeed"><div class="vs-bubble assistant">' + GREETING + '</div></div>' +
      '<div class="vs-status" id="vsStatus"></div>' +
      '<div class="vs-inputbar">' +
        '<button class="vs-mic-btn" id="vsMic" aria-label="Talk">' +
          '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">' +
            '<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>' +
            '<path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line>' +
          '</svg>' +
        '</button>' +
        '<input class="vs-text-input" id="vsInput" type="text" placeholder="Type a message..." autocomplete="off">' +
        '<button class="vs-send-btn" id="vsSend" aria-label="Send">' +
          '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
            '<line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>' +
          '</svg>' +
        '</button>' +
      '</div>' +
    '</div>';

  var launcher = shadow.getElementById('vsLauncher');
  var panel = shadow.getElementById('vsPanel');
  var closeBtn = shadow.getElementById('vsClose');
  var feed = shadow.getElementById('vsFeed');
  var status = shadow.getElementById('vsStatus');
  var micBtn = shadow.getElementById('vsMic');
  var input = shadow.getElementById('vsInput');
  var sendBtn = shadow.getElementById('vsSend');

  var currentAudio = null;
  var isRecording = false;
  var mediaRecorder = null;
  var audioChunks = [];

  launcher.addEventListener('click', function () { panel.classList.toggle('open'); });
  closeBtn.addEventListener('click', function () { panel.classList.remove('open'); });

  function addBubble(role, text) {
    var b = document.createElement('div');
    b.className = 'vs-bubble ' + role;
    b.textContent = text;
    feed.appendChild(b);
    feed.scrollTop = feed.scrollHeight;
  }

  function setStatus(text) { status.textContent = text || ''; }

  async function sendMessage(text, detectedLanguage) {
    if (!text) return;
    addBubble('user', text);
    setStatus('Thinking...');
    try {
      var chatRes = await fetch(API_BASE + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, language: detectedLanguage || null })
      });
      var chatData = await chatRes.json();
      var reply = chatData.response || 'Sorry, something went wrong.';
      addBubble('assistant', reply);
      setStatus('Speaking...');
      await playTTS(reply, detectedLanguage);
    } catch (err) {
      setStatus('Error: ' + err.message);
    } finally {
      setTimeout(function () { setStatus(''); }, 1200);
    }
  }

  async function playTTS(text, detectedLanguage) {
    try {
      var langMap = { spanish: 'es', french: 'fr', german: 'de', italian: 'it', portuguese: 'pt',
        japanese: 'ja', korean: 'ko', chinese: 'zh-CN', arabic: 'ar', hindi: 'hi', urdu: 'ur' };
      var code = langMap[(detectedLanguage || '').toLowerCase()] || 'en';
      var res = await fetch(API_BASE + '/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, lang: code })
      });
      if (!res.ok) return;
      var blob = await res.blob();
      if (currentAudio) currentAudio.pause();
      currentAudio = new Audio(URL.createObjectURL(blob));
      await currentAudio.play();
    } catch (err) { /* silent fallback to text-only */ }
  }

  sendBtn.addEventListener('click', function () {
    var text = input.value.trim();
    input.value = '';
    sendMessage(text);
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { sendBtn.click(); }
  });

  micBtn.addEventListener('click', async function () {
    if (isRecording) { mediaRecorder.stop(); return; }
    try {
      var stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = function (e) { if (e.data.size > 0) audioChunks.push(e.data); };
      mediaRecorder.onstop = async function () {
        stream.getTracks().forEach(function (t) { t.stop(); });
        isRecording = false;
        micBtn.classList.remove('recording');
        setStatus('Transcribing...');
        var blob = new Blob(audioChunks, { type: 'audio/webm' });
        var formData = new FormData();
        formData.append('file', blob, 'recording.webm');
        try {
          var res = await fetch(API_BASE + '/api/transcribe', { method: 'POST', body: formData });
          var data = await res.json();
          if (data.text && data.text.trim()) {
            await sendMessage(data.text.trim(), data.language);
          } else {
            setStatus('No speech detected');
            setTimeout(function () { setStatus(''); }, 1200);
          }
        } catch (err) {
          setStatus('Error: ' + err.message);
        }
      };
      mediaRecorder.start();
      isRecording = true;
      micBtn.classList.add('recording');
      setStatus('Listening...');
    } catch (err) {
      setStatus('Microphone access denied');
    }
  });
})();
