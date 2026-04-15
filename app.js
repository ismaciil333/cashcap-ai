/**
 * CashCap AI — Main Application Logic
 * Chat engine, document upload, mode toggle, source viewer
 */

/* ===== STATE ===== */
const state = {
  mode: 'intern',           // 'intern' | 'expert'
  messages: [],
  uploadedDocs: [],
  sourcesOpen: false,
  currentSources: [],
  isThinking: false,
  sidebarOpen: true,
};

/* ===== DOM REFS ===== */
const $ = id => document.getElementById(id);
const els = {
  sidebar: $('sidebar'),
  sidebarToggle: $('sidebarToggle'),
  menuBtn: $('menuBtn'),
  internBtn: $('internBtn'),
  expertBtn: $('expertBtn'),
  modeDesc: $('modeDesc'),
  modeLabel: $('modeLabel'),
  uploadZone: $('uploadZone'),
  fileInput: $('fileInput'),
  docList: $('docList'),
  topicChips: document.querySelectorAll('.topic-chip'),
  welcomeCards: document.querySelectorAll('.welcome-card'),
  welcomeScreen: $('welcomeScreen'),
  messagesContainer: $('messagesContainer'),
  typingIndicator: $('typingIndicator'),
  chatInput: $('chatInput'),
  sendBtn: $('sendBtn'),
  attachBtn: $('attachBtn'),
  sourcesToggleBtn: $('sourcesToggleBtn'),
  sourcesPanel: $('sourcesPanel'),
  closeSourcesBtn: $('closeSourcesBtn'),
  sourcesContent: $('sourcesContent'),
  tabSources: $('tabSources'),
  tabGlossary: $('tabGlossary'),
  glossaryContent: $('glossaryContent'),
  contextBadges: $('contextBadges'),
  newChatBtn: $('newChatBtn'),
};

/* ===== INIT ===== */
document.addEventListener('DOMContentLoaded', () => {
  bindEvents();
});

function bindEvents() {
  // Mode toggle
  els.internBtn.addEventListener('click', () => setMode('intern'));
  els.expertBtn.addEventListener('click', () => setMode('expert'));

  // Sidebar toggle
  els.sidebarToggle.addEventListener('click', () => toggleSidebar());
  els.menuBtn.addEventListener('click', () => toggleSidebar());

  // Chat input
  els.chatInput.addEventListener('input', onInputChange);
  els.chatInput.addEventListener('keydown', onInputKeydown);

  // Send
  els.sendBtn.addEventListener('click', sendMessage);

  // Attach in input
  els.attachBtn.addEventListener('click', () => els.fileInput.click());

  // Upload zone
  els.uploadZone.addEventListener('click', () => els.fileInput.click());
  els.uploadZone.addEventListener('dragover', e => { e.preventDefault(); els.uploadZone.classList.add('drag-over'); });
  els.uploadZone.addEventListener('dragleave', () => els.uploadZone.classList.remove('drag-over'));
  els.uploadZone.addEventListener('drop', e => {
    e.preventDefault();
    els.uploadZone.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
  });
  els.fileInput.addEventListener('change', e => handleFiles(e.target.files));

  // Topic chips
  els.topicChips.forEach(chip => {
    chip.addEventListener('click', () => handleQuery(chip.dataset.query));
  });

  // Welcome cards
  els.welcomeCards.forEach(card => {
    card.addEventListener('click', () => handleQuery(card.dataset.query));
  });

  // Sources panel tabs
  els.sourcesToggleBtn.addEventListener('click', toggleSources);
  els.closeSourcesBtn.addEventListener('click', () => setSources(false));
  els.tabSources.addEventListener('click', () => switchPanelTab('sources'));
  els.tabGlossary.addEventListener('click', () => switchPanelTab('glossary'));

  // Render glossary into panel
  renderGlossaryPanel();

  // New chat
  els.newChatBtn.addEventListener('click', resetChat);
}

/* ===== MODE ===== */
function setMode(mode) {
  state.mode = mode;
  els.internBtn.classList.toggle('active', mode === 'intern');
  els.expertBtn.classList.toggle('active', mode === 'expert');
  els.modeLabel.textContent = mode === 'intern' ? 'Intern Mode' : 'Expert Mode';
  els.modeDesc.textContent = mode === 'intern'
    ? 'Mentor-like explanations with examples and context'
    : 'Concise, technical depth with frameworks and indicators';
}

/* ===== SIDEBAR ===== */
function toggleSidebar() {
  state.sidebarOpen = !state.sidebarOpen;
  els.sidebar.classList.toggle('collapsed', !state.sidebarOpen);
}

/* ===== SOURCES PANEL ===== */
function toggleSources() {
  setSources(!state.sourcesOpen);
}
function setSources(open) {
  state.sourcesOpen = open;
  els.sourcesPanel.classList.toggle('open', open);
  els.sourcesToggleBtn.classList.toggle('active', open);
}

/* ===== REFERENCE PANEL TABS ===== */
function switchPanelTab(tab) {
  const isSources = tab === 'sources';
  els.tabSources.classList.toggle('active', isSources);
  els.tabGlossary.classList.toggle('active', !isSources);
  els.sourcesContent.style.display = isSources ? 'block' : 'none';
  els.glossaryContent.style.display = isSources ? 'none' : 'block';
}

function renderGlossaryPanel() {
  if (!window.FULL_GLOSSARY) return;

  const entries = Object.entries(window.FULL_GLOSSARY).sort((a, b) => a[0].localeCompare(b[0]));

  const html = entries.map(([term, def]) => `
    <div class="glossary-item">
      <div class="glossary-term">${escapeHtml(term)}</div>
      <div class="glossary-def">${escapeHtml(def)}</div>
    </div>
  `).join('');

  els.glossaryContent.innerHTML = html;
}

/* ===== INPUT HANDLING ===== */
function onInputChange() {
  const val = els.chatInput.value.trim();
  els.sendBtn.disabled = !val || state.isThinking;

  // Auto-resize textarea
  els.chatInput.style.height = 'auto';
  els.chatInput.style.height = Math.min(els.chatInput.scrollHeight, 160) + 'px';
}

function onInputKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!els.sendBtn.disabled) sendMessage();
  }
}

/* ===== SEND MESSAGE ===== */
async function getAIResponse(message) {
  try {
    const response = await fetch("https://cashcap-ai.onrender.com/ask", {  // ✅ RIKTIG ENDPOINT
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: message }),
    });

    if (!response.ok) {
      try {
        const errorData = await response.json();
        return `⚠️ Error from server: ${errorData.answer || errorData.detail || response.statusText}`;
      } catch (err) {
        return `⚠️ Error from server (${response.status}): ${response.statusText}`;
      }
    }

    const data = await response.json();
    return data.answer;

  } catch (error) {
    console.error("API error:", error);
    return "⚠️ Error connecting to CashCap AI backend.";
  }
}

async function sendMessage() {
  const query = els.chatInput.value.trim();
  if (!query || state.isThinking) return;
  handleQuery(query);
}

function detectGlossary(message) {
  if (!window.FULL_GLOSSARY) return;

  const words = message.toUpperCase().split(/\s+/);
  for (const word of words) {
    if (window.FULL_GLOSSARY[word]) {
      addMessage('ai', `### 📚 Glossary Update\n\n<span style="color:var(--accent-cyan); font-weight:600; font-size:1.05em;">${word}</span> — ${window.FULL_GLOSSARY[word]}`);
      break;
    }
  }
}

async function handleQuery(query) {
  if (state.isThinking) return;

  // Clear input
  els.chatInput.value = '';
  els.chatInput.style.height = 'auto';
  els.sendBtn.disabled = true;

  // Show chat
  showChat();

  // Add user message
  addMessage('user', query);

  // Fast glossary detection feedback in UI
  detectGlossary(query);

  // Think
  state.isThinking = true;
  showTyping(true);

  // Fetch real answer from FastAPI backend
  const answer = await getAIResponse(query);

  // Retrieve relevant knowledge for source display
  const sources = searchKnowledge(query, 5);
  state.currentSources = sources;

  showTyping(false);
  state.isThinking = false;

  // Add AI message
  addMessage('ai', answer, sources);

  // Update sources panel
  updateSourcesPanel(sources);
}

/* ===== CHAT UI ===== */
function showChat() {
  els.welcomeScreen.style.display = 'none';
  els.messagesContainer.classList.add('visible');
}

function addMessage(role, content, sources = []) {
  const msg = { role, content, sources, time: new Date() };
  state.messages.push(msg);

  const el = createMessageEl(msg);
  els.messagesContainer.appendChild(el);
  scrollToBottom();
}

function createMessageEl({ role, content, sources, time }) {
  const div = document.createElement('div');
  div.className = `message ${role}`;

  const avatar = document.createElement('div');

  if (role === 'ai') {
    avatar.className = 'avatar ai-avatar';
    avatar.innerHTML = `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L2 7l10 5 10-5-10-5z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
    </svg>`;
  } else {
    avatar.className = 'avatar user-avatar';
    avatar.textContent = 'U';
  }

  const msgContent = document.createElement('div');
  msgContent.className = 'message-content';

  if (role === 'ai') {
    const bubble = document.createElement('div');
    bubble.className = 'bubble ai-bubble';
    bubble.innerHTML = renderMarkdown(content);

    if (sources.length > 0) {
      const sourceSection = document.createElement('div');
      sourceSection.className = 'response-section';
      sourceSection.innerHTML = `
        <div class="section-badge badge-sources">📚 Sources</div>
        <div class="source-tags">
          ${sources.slice(0, 4).map(s => `<span class="source-tag">📄 ${s.org}</span>`).join('')}
        </div>`;
      bubble.appendChild(sourceSection);
    }

    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.innerHTML = `
      <span class="meta-time">${formatTime(time)}</span>
      <button class="copy-btn" onclick="copyText(this, event)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
        Copy
      </button>`;

    msgContent.appendChild(bubble);
    msgContent.appendChild(meta);
  } else {
    const bubble = document.createElement('div');
    bubble.className = 'bubble user-bubble';
    bubble.textContent = content;
    msgContent.appendChild(bubble);
  }

  div.appendChild(avatar);
  div.appendChild(msgContent);
  return div;
}

function scrollToBottom() {
  setTimeout(() => {
    els.messagesContainer.scrollTop = els.messagesContainer.scrollHeight;
  }, 50);
}

function showTyping(show) {
  els.typingIndicator.style.display = show ? 'flex' : 'none';
  if (show) els.messagesContainer.scrollTop = els.messagesContainer.scrollHeight;
}

/* ===== SOURCES PANEL ===== */
function updateSourcesPanel(sources) {
  if (sources.length === 0) {
    els.sourcesContent.innerHTML = `
      <div class="sources-empty">
        <div class="sources-empty-icon">🔍</div>
        <p>No direct document sources found.<br/>Answer based on humanitarian best practice knowledge.</p>
      </div>`;
    return;
  }

  // Update context badges
  els.contextBadges.innerHTML = sources.slice(0, 2).map(s =>
    `<div class="context-badge">📄 ${s.org}</div>`
  ).join('');

  els.sourcesContent.innerHTML = sources.map(s => `
    <div class="source-card">
      <div class="source-card-header">
        <div class="source-card-icon">📄</div>
        <div>
          <div class="source-card-title">${escapeHtml(s.title)}</div>
          <div class="source-card-org">${escapeHtml(s.org)}</div>
        </div>
      </div>
      <div class="source-card-excerpt">${escapeHtml(s.excerpt)}</div>
      <div class="source-relevance">
        <div class="relevance-bar">
          <div class="relevance-fill" style="width:${Math.round(s.relevance * 100)}%"></div>
        </div>
        <span class="relevance-score">${Math.round(s.relevance * 100)}% match</span>
      </div>
    </div>
  `).join('');
}

/* ===== DOCUMENT UPLOAD ===== */
function handleFiles(files) {
  Array.from(files).forEach(file => {
    const ext = file.name.split('.').pop().toLowerCase();
    const icon = ext === 'pdf' ? '📕' : ext === 'docx' || ext === 'doc' ? '📘' : '📄';
    const id = 'doc_' + Date.now() + Math.random();
    const docData = { id, name: file.name, size: file.size, icon, status: 'processing' };
    state.uploadedDocs.push(docData);
    renderDocItem(docData);

    // Simulate processing
    setTimeout(() => {
      docData.status = 'ready';
      updateDocStatus(id);
      addUploadedDocToKnowledge(file, docData);
    }, 1500 + Math.random() * 1000);
  });

  // Reset file input
  els.fileInput.value = '';
}

function renderDocItem(doc) {
  const div = document.createElement('div');
  div.className = 'doc-item';
  div.id = `docitem_${doc.id}`;
  div.innerHTML = `
    <div class="doc-icon">${doc.icon}</div>
    <div class="doc-info">
      <div class="doc-name">${escapeHtml(doc.name)}</div>
      <div class="doc-size doc-processing" id="docstatus_${doc.id}">
        <span>⏳</span> Processing...
      </div>
    </div>
    <button class="doc-remove" onclick="removeDoc('${doc.id}')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>`;
  els.docList.appendChild(div);
}

function updateDocStatus(id) {
  const el = document.getElementById(`docstatus_${id}`);
  if (el) {
    el.className = 'doc-size';
    el.style.color = 'var(--accent-emerald)';
    el.innerHTML = '✓ Indexed';
  }
}

function addUploadedDocToKnowledge(file, docData) {
  // Simulate reading and indexing
  const reader = new FileReader();
  reader.onload = (e) => {
    const text = e.target?.result || '';
    if (text && typeof text === 'string' && text.length > 50) {
      const chunk = text.substring(0, 2000);
      KNOWLEDGE_BASE.push({
        id: docData.id,
        title: docData.name,
        org: 'Uploaded Document',
        section: 'User Documents',
        tags: docData.name.toLowerCase().split(/[\s._-]+/),
        content: chunk,
        excerpt: chunk.substring(0, 140) + '…',
      });
    }
  };
  try {
    if (file.type === 'text/plain') reader.readAsText(file);
  } catch (_) { }
}

window.removeDoc = function (id) {
  state.uploadedDocs = state.uploadedDocs.filter(d => d.id !== id);
  const el = document.getElementById(`docitem_${id}`);
  if (el) el.remove();
  // Remove from KB
  const idx = KNOWLEDGE_BASE.findIndex(d => d.id === id);
  if (idx > -1) KNOWLEDGE_BASE.splice(idx, 1);
};

/* ===== COPY BUTTON ===== */
window.copyText = function (btn, e) {
  const bubble = btn.closest('.message-content').querySelector('.ai-bubble');
  if (!bubble) return;
  const text = bubble.innerText;
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = '✓ Copied';
    setTimeout(() => {
      btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> Copy`;
    }, 2000);
  });
};

/* ===== RESET ===== */
function resetChat() {
  state.messages = [];
  state.currentSources = [];
  els.messagesContainer.innerHTML = '';
  els.messagesContainer.classList.remove('visible');
  els.welcomeScreen.style.display = '';
  els.contextBadges.innerHTML = '';
  els.sourcesContent.innerHTML = `
    <div class="sources-empty">
      <div class="sources-empty-icon">📚</div>
      <p>Sources will appear here after your first query</p>
    </div>`;
}

/* ===== AI RESPONSE GENERATION (Backend handles this now) ===== */

/* ===== MARKDOWN RENDERER ===== */
function renderMarkdown(text) {
  // Process section badges
  text = text
    .replace(/### 🔍 Answer/g, '<div class="section-badge badge-answer">🔍 Answer</div>')
    .replace(/### ⚙️ Practical Insight/g, '<div class="section-badge badge-insight">⚙️ Practical Insight</div>')
    .replace(/### 📌 Key Takeaway/g, '<div class="section-badge badge-takeaway">📌 Key Takeaway</div>')
    .replace(/### 📚 Glossary Update/g, '<div class="section-badge badge-sources">📚 Glossary Update</div>')
    .replace(/### 📚 Sources/g, '<div class="section-badge badge-sources">📚 Sources</div>');

  if (window.marked) {
    return marked.parse(text);
  }
  return text;
}

function processInline(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>');
}

/* ===== UTILS ===== */
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
