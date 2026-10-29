/**
 * Interactive Séance & Spirit Communion Engine for Ofrenda AI
 * Bridges the mortal realm and memory via local Gemma 2 inference.
 */

let isCommuning = false;

window.resetSeanceChat = function(altar) {
  const history = document.getElementById('chat-history');
  if (!history) return;
  history.innerHTML = '';

  // Initial welcome reflection from the spirit
  const welcomeMsg = document.createElement('div');
  welcomeMsg.className = 'msg msg-spirit';
  welcomeMsg.innerHTML = `
    <div class="msg-author">${altar.name.toUpperCase()} (${altar.years})</div>
    <div>I see the warm candlelight you have lit, and the marigold petals marking a path through the dark. What is on your mind as you sit before the altar tonight?</div>
  `;
  history.appendChild(welcomeMsg);
};

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const history = document.getElementById('chat-history');

  if (!form || !input) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text || isCommuning) return;

    if (!currentAltar) return;

    // Append user message
    const userMsg = document.createElement('div');
    userMsg.className = 'msg msg-user';
    userMsg.innerHTML = `
      <div class="msg-author" style="color:#d1b8eb;">VISITOR AT THE OFRENDA</div>
      <div>${escapeHtml(text)}</div>
    `;
    history.appendChild(userMsg);
    input.value = '';
    history.scrollTop = history.scrollHeight;

    // Show shimmering spirit waiting indicator
    const spiritMsg = document.createElement('div');
    spiritMsg.className = 'msg msg-spirit';
    spiritMsg.innerHTML = `
      <div class="msg-author">${currentAltar.name.toUpperCase()}</div>
      <div class="spirit-text-typing" style="font-style:italic;color:#d4a373;">
        🕯️ The amber flame flickers as your words reach across the veil...
      </div>
      <div class="spirit-metrics" style="font-size:0.75rem;color:#9b82ad;margin-top:6px;display:none;"></div>
    `;
    history.appendChild(spiritMsg);
    history.scrollTop = history.scrollHeight;

    isCommuning = true;

    try {
      const res = await fetch(`/api/altars/${currentAltar.id}/commune`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      const data = await res.json();
      const textContainer = spiritMsg.querySelector('.spirit-text-typing');
      const metricsContainer = spiritMsg.querySelector('.spirit-metrics');

      textContainer.style.fontStyle = 'normal';
      textContainer.style.color = '#f7e6ca';

      // Typewriter animation
      await streamTypewriter(textContainer, data.text || "May peace be with you.");

      if (metricsContainer) {
        metricsContainer.style.display = 'block';
        metricsContainer.innerHTML = `
          <span>✦ Model: <strong>${data.model}</strong></span> &bull; 
          <span>Latency: <strong>${data.latency_seconds}s</strong></span> &bull; 
          <span style="color:#38b000;">${data.privacy}</span>
        `;
      }

      history.scrollTop = history.scrollHeight;
    } catch (err) {
      console.error('Commune error:', err);
      const textContainer = spiritMsg.querySelector('.spirit-text-typing');
      textContainer.textContent = "The candle flame wavered in a sudden cold gust. Please try whispering your remembrance once more.";
    } finally {
      isCommuning = false;
    }
  });
});

function streamTypewriter(element, text, speed = 16) {
  return new Promise((resolve) => {
    element.textContent = '';
    let i = 0;
    const interval = setInterval(() => {
      element.textContent += text.charAt(i);
      i++;
      if (i >= text.length) {
        clearInterval(interval);
        resolve();
      }
    }, speed);
  });
}

function escapeHtml(string) {
  const div = document.createElement('div');
  div.innerText = string;
  return div.innerHTML;
}
