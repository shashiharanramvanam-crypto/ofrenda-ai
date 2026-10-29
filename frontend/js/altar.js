/**
 * Altar State Manager & REST Client for Ofrenda AI
 */

const API_BASE = '';
let currentAltar = null;
let allAltars = [];

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  await fetchStatus();
  await loadAltars();
  setupEventListeners();
}

async function fetchStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    const data = await res.json();
    const modelSpan = document.getElementById('engine-model-name');
    if (modelSpan) {
      modelSpan.textContent = data.model;
    }
  } catch (err) {
    console.warn('Status fetch error:', err);
  }
}

async function loadAltars() {
  try {
    const res = await fetch(`${API_BASE}/api/altars`);
    allAltars = await res.json();
    populateAltarSelector();
    if (allAltars.length > 0) {
      renderAltar(allAltars[0]);
    }
  } catch (err) {
    console.error('Error loading altars:', err);
  }
}

function populateAltarSelector() {
  const select = document.getElementById('altar-select');
  if (!select) return;
  select.innerHTML = '';
  allAltars.forEach(a => {
    const opt = document.createElement('option');
    opt.value = a.id;
    opt.textContent = `${a.name} (${a.years})`;
    select.appendChild(opt);
  });
}

function renderAltar(altar) {
  currentAltar = altar;
  document.getElementById('altar-select').value = altar.id;

  // Render Top Tier
  document.getElementById('portrait-avatar').textContent = altar.avatar || '🕯️';
  document.getElementById('portrait-years').textContent = altar.years || '';
  document.getElementById('spirit-name').textContent = altar.name;
  document.getElementById('spirit-title').textContent = altar.title;
  document.getElementById('spirit-summary').textContent = altar.summary;

  // Traits / Tags
  const tagsContainer = document.getElementById('spirit-tags');
  tagsContainer.innerHTML = '';
  if (altar.traits) {
    altar.traits.split(',').forEach(t => {
      const chip = document.createElement('span');
      chip.className = 'tag-chip';
      chip.textContent = t.trim();
      tagsContainer.appendChild(chip);
    });
  }

  // Candles
  renderCandles(altar.candles || []);

  // Offerings (Middle & Bottom Tiers)
  renderOfferings(altar.offerings || []);

  // Update Séance Chat Header
  const seanceTitle = document.getElementById('seance-spirit-name');
  if (seanceTitle) seanceTitle.textContent = altar.name;

  // Reset chat dialogue with initial spirit greeting
  window.resetSeanceChat(altar);
}

function renderCandles(candles) {
  const container = document.getElementById('candles-container');
  container.innerHTML = '';

  candles.forEach(c => {
    const item = document.createElement('div');
    item.className = `candle-item ${c.lit ? 'lit' : 'unlit'}`;
    item.dataset.candleId = c.id;

    item.innerHTML = `
      <div class="flame-container">
        <div class="candle-flame"></div>
        <div class="candle-wax"></div>
      </div>
      <div class="candle-info">
        <div><strong>${c.label}</strong></div>
        <div class="candle-status-sub">${c.lit ? 'Lit &bull; Click to extinguish' : 'Dark &bull; Click to light'}</div>
      </div>
    `;

    item.addEventListener('click', () => toggleCandle(c.id));
    container.appendChild(item);
  });
}

async function toggleCandle(candleId) {
  if (!currentAltar) return;
  try {
    const res = await fetch(`${API_BASE}/api/altars/${currentAltar.id}/candles/${candleId}/toggle`, {
      method: 'POST'
    });
    const updated = await res.json();
    
    // Play chime sound when candle is lit
    if (updated.lit && window.ofrendaAudio) {
      window.ofrendaAudio.playChime(528);
    }

    // Refresh altar
    const refreshRes = await fetch(`${API_BASE}/api/altars/${currentAltar.id}`);
    const altar = await refreshRes.json();
    renderCandles(altar.candles);
  } catch (err) {
    console.error('Candle toggle failed:', err);
  }
}

function renderOfferings(offerings) {
  const middleGrid = document.getElementById('offerings-middle');
  const bottomGrid = document.getElementById('offerings-bottom');
  
  if (middleGrid) middleGrid.innerHTML = '';
  if (bottomGrid) bottomGrid.innerHTML = '';

  offerings.forEach(off => {
    const card = document.createElement('div');
    card.className = 'offering-card';
    card.innerHTML = `
      <div class="offering-top">
        <span>${(off.type || 'offering').toUpperCase()}</span>
        <button class="delete-offering-btn" data-id="${off.id}" style="background:none;border:none;color:#ff758f;cursor:pointer;font-size:0.8rem;">✕</button>
      </div>
      <div class="offering-name">${off.name}</div>
      <div class="offering-note">${off.note || ''}</div>
    `;

    card.querySelector('.delete-offering-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      deleteOffering(off.id);
    });

    if (off.tier === 'bottom') {
      if (bottomGrid) bottomGrid.appendChild(card);
    } else {
      if (middleGrid) middleGrid.appendChild(card);
    }
  });

  // Add "+" placeholder button to middle tier
  if (middleGrid) {
    const addBtn = document.createElement('div');
    addBtn.className = 'add-offering-trigger';
    addBtn.innerHTML = `<span>+ Place New Offering</span><small style="color:#d4a373">Food, memory, or artifact</small>`;
    addBtn.addEventListener('click', () => openOfferingModal('middle'));
    middleGrid.appendChild(addBtn);
  }

  // Add "+" placeholder to bottom tier
  if (bottomGrid) {
    const addBtnBottom = document.createElement('div');
    addBtnBottom.className = 'add-offering-trigger';
    addBtnBottom.innerHTML = `<span>+ Add Earthly Element</span><small style="color:#d4a373">Water, salt, or marigold trail</small>`;
    addBtnBottom.addEventListener('click', () => openOfferingModal('bottom'));
    bottomGrid.appendChild(addBtnBottom);
  }
}

async function deleteOffering(offeringId) {
  if (!currentAltar) return;
  try {
    await fetch(`${API_BASE}/api/altars/${currentAltar.id}/offerings/${offeringId}`, {
      method: 'DELETE'
    });
    const res = await fetch(`${API_BASE}/api/altars/${currentAltar.id}`);
    const altar = await res.json();
    renderOfferings(altar.offerings);
  } catch (err) {
    console.error('Delete offering error:', err);
  }
}

function setupEventListeners() {
  // Selector
  document.getElementById('altar-select').addEventListener('change', (e) => {
    const selected = allAltars.find(a => a.id === e.target.value);
    if (selected) {
      renderAltar(selected);
      if (window.ofrendaAudio) window.ofrendaAudio.playChime(432);
    }
  });

  // Audio Toggle
  const audioBtn = document.getElementById('audio-toggle');
  if (audioBtn) {
    audioBtn.addEventListener('click', () => {
      const playing = window.ofrendaAudio.toggle();
      audioBtn.classList.toggle('playing', playing);
      audioBtn.innerHTML = playing ? '🔊 Ambient Sound: ON' : '🔈 Ambient Sound: OFF';
    });
  }

  // Export Archive Button
  const exportBtn = document.getElementById('export-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      if (!currentAltar) return;
      window.open(`${API_BASE}/api/altars/${currentAltar.id}/export`, '_blank');
    });
  }

  // New Altar Modal
  document.getElementById('btn-new-altar').addEventListener('click', () => {
    document.getElementById('modal-new-altar').style.display = 'flex';
  });

  document.getElementById('close-modal-altar').addEventListener('click', () => {
    document.getElementById('modal-new-altar').style.display = 'none';
  });

  document.getElementById('form-new-altar').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
      name: document.getElementById('in-altar-name').value,
      title: document.getElementById('in-altar-title').value,
      years: document.getElementById('in-altar-years').value,
      avatar: document.getElementById('in-altar-avatar').value || '🕯️',
      summary: document.getElementById('in-altar-summary').value,
      traits: document.getElementById('in-altar-traits').value,
      memories: document.getElementById('in-altar-memories').value,
      persona_key: 'ancestor'
    };

    const res = await fetch(`${API_BASE}/api/altars`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const created = await res.json();
    allAltars.push(created);
    populateAltarSelector();
    renderAltar(created);
    document.getElementById('modal-new-altar').style.display = 'none';
    e.target.reset();
  });

  // Offering Modal
  document.getElementById('close-modal-offering').addEventListener('click', () => {
    document.getElementById('modal-offering').style.display = 'none';
  });

  document.getElementById('form-offering').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentAltar) return;
    const offData = {
      name: document.getElementById('in-off-name').value,
      tier: document.getElementById('in-off-tier').value,
      type: document.getElementById('in-off-type').value,
      note: document.getElementById('in-off-note').value
    };

    await fetch(`${API_BASE}/api/altars/${currentAltar.id}/offerings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(offData)
    });

    const res = await fetch(`${API_BASE}/api/altars/${currentAltar.id}`);
    const altar = await res.json();
    renderOfferings(altar.offerings);
    document.getElementById('modal-offering').style.display = 'none';
    e.target.reset();
  });

  // Open Innovation Info Modal
  document.getElementById('btn-why-open').addEventListener('click', () => {
    document.getElementById('modal-why-open').style.display = 'flex';
  });

  document.getElementById('close-modal-why-open').addEventListener('click', () => {
    document.getElementById('modal-why-open').style.display = 'none';
  });
}

function openOfferingModal(tier = 'middle') {
  document.getElementById('in-off-tier').value = tier;
  document.getElementById('modal-offering').style.display = 'flex';
}
