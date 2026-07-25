/* FitAI Pro - Interactive RAG Chatbot Client */

document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.getElementById('chat-messages');

  if (chatForm && chatInput && chatMessages) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const msg = chatInput.value.trim();
      if (!msg) return;

      // Render user message
      appendMessage('user', msg);
      chatInput.value = '';

      // Render typing indicator
      const typingId = appendTypingIndicator();

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        removeTypingIndicator(typingId);
        appendMessage('bot', data.response || 'Sorry, I could not process that request.');
      } catch (err) {
        removeTypingIndicator(typingId);
        appendMessage('bot', '⚠️ Error connecting to FitAI Pro server.');
      }
    });
  }
});

function sendQuickPrompt(promptText) {
  const chatInput = document.getElementById('chat-input');
  const chatForm = document.getElementById('chat-form');
  if (chatInput && chatForm) {
    chatInput.value = promptText;
    chatForm.dispatchEvent(new Event('submit'));
  }
}

function appendMessage(sender, text) {
  const chatMessages = document.getElementById('chat-messages');
  if (!chatMessages) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = `chat-msg ${sender === 'user' ? 'user-msg' : 'bot-msg'}`;
  
  // Format simple markdown into HTML
  let formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n- /g, '<br>• ');

  msgDiv.innerHTML = `
    <div class="msg-bubble">
      ${sender === 'bot' ? '<span class="bot-badge">🤖 FitAI Pro Coach</span><br>' : ''}
      ${formatted}
    </div>
  `;

  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendTypingIndicator() {
  const chatMessages = document.getElementById('chat-messages');
  const id = 'typing-' + Date.now();
  const div = document.createElement('div');
  div.id = id;
  div.className = 'chat-msg bot-msg';
  div.innerHTML = `<div class="msg-bubble" style="color: var(--text-muted);">🤖 <i>FitAI Pro is analyzing dataset & generating answer...</i></div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const elem = document.getElementById(id);
  if (elem) elem.remove();
}
