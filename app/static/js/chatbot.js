// Chatbot flotante JS para Gridi 
(function() {
  // --- Elementos ---
  const fab = document.createElement('div');
  fab.id = 'chatbot-fab';
  fab.innerHTML = '<img src="/static/images/gridi_avatar.png" alt="Gridi" />';
  document.body.appendChild(fab);

  // Mensaje flotante de ayuda
  const helpMsg = document.createElement('div');
  helpMsg.id = 'chatbot-help-msg';
  helpMsg.textContent = '¿Necesitas ayuda?';
  document.body.appendChild(helpMsg);

  const windowDiv = document.createElement('div');
  windowDiv.id = 'chatbot-window';
  windowDiv.innerHTML = `
    <div id="chatbot-header">
      <img src="/static/images/gridi_avatar.png" alt="Gridi" />
      Gridi
      <span style="flex:1"></span>
      <button id="chatbot-close-btn" style="background:none;border:none;font-size:20px;color:#fff;cursor:pointer;">&times;</button>
    </div>
    <div id="chatbot-messages"></div>
    <form id="chatbot-input-row">
      <input id="chatbot-input" type="text" placeholder="Pregúntame sobre AgroGrid..." autocomplete="off" />
      <button id="chatbot-send-btn" type="submit">Enviar</button>
    </form>
  `;
  document.body.appendChild(windowDiv);

  // --- Logica de mostrar/ocultar ---
  fab.addEventListener('click', () => {
    windowDiv.classList.add('active');
    helpMsg.classList.add('hide');
    setTimeout(() => {
      document.getElementById('chatbot-input').focus();
    }, 200);
  });
  document.getElementById('chatbot-close-btn').addEventListener('click', () => {
    windowDiv.classList.remove('active');
    setTimeout(() => {
      helpMsg.classList.remove('hide');
    }, 350);
  });

  // --- Logica de mensajeria ---
  const messagesDiv = document.getElementById('chatbot-messages');
  const input = document.getElementById('chatbot-input');
  const form = document.getElementById('chatbot-input-row');

  function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chatbot-message ' + sender;
    const bubble = document.createElement('div');
    bubble.className = 'chatbot-bubble';
    bubble.innerText = text;
    msgDiv.appendChild(bubble);
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  async function sendMessage(e) {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    appendMessage(text, 'user');
    input.value = '';
    appendMessage('Gridi está pensando...','bot');
    try {
      const res = await fetch('/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      // Remueve "Gridi está pensando..."
      messagesDiv.removeChild(messagesDiv.lastChild);
      appendMessage(data.response, 'bot');
    } catch(err) {
      messagesDiv.removeChild(messagesDiv.lastChild);
      appendMessage('Ocurrió un error. Intenta de nuevo.', 'bot');
    }
  }

  form.addEventListener('submit', sendMessage);
})();
