// Global state store for processed history items
const historyStore = {};
let historyIdCounter = 0;

async function processVideo() {
  const urlInput = document.getElementById("urlInput");
  const langSelect = document.getElementById("langSelect");
  const processBtn = document.getElementById("processBtn");
  const loadingContainer = document.getElementById("loadingContainer");
  const resultsContainer = document.getElementById("resultsContainer");

  const source = urlInput ? urlInput.value.trim() : "";
  const language = langSelect ? langSelect.value : "english";

  if (!source) {
    alert("Please enter a valid video URL or file path.");
    return;
  }

  // UI state: Show loading spinner, disable process button, hide old results
  if (processBtn) processBtn.disabled = true;
  if (loadingContainer) loadingContainer.classList.remove("hidden");
  if (resultsContainer) resultsContainer.classList.add("hidden");

  try {
    const response = await fetch("/api/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source, language }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Failed to process video");
    }

    const result = await response.json();

    // Render results on the UI dashboard
    document.getElementById("videoTitle").innerText = result.title;
    document.getElementById("summaryText").innerText = result.summary || "No summary available.";

    // Reset Chat Messages for new video session
    const chatMessages = document.getElementById("chatMessages");
    if (chatMessages) {
      chatMessages.innerHTML = `
        <div class="message system-msg">
          <strong>AI Assistant:</strong> Ready! Ask me any question about "${result.title}".
        </div>
      `;
    }

    // Show results container
    if (resultsContainer) resultsContainer.classList.remove("hidden");

    // Store item in sidebar history
    if (result.title) {
      addHistoryItem(result);
    }
  } catch (error) {
    alert("Error: " + error.message);
  } finally {
    if (processBtn) processBtn.disabled = false;
    if (loadingContainer) loadingContainer.classList.add("hidden");
  }
}

// Interactive Chat Handler
async function sendChatMessage() {
  const chatInput = document.getElementById("chatInput");
  const chatMessages = document.getElementById("chatMessages");
  const sendBtn = document.getElementById("sendChatBtn");

  const question = chatInput ? chatInput.value.trim() : "";
  if (!question) return;

  // Render User Message
  appendChatMessage("user-msg", `<strong>You:</strong> ${escapeHtml(question)}`);
  chatInput.value = "";

  // Disable Send Button while AI is thinking
  if (sendBtn) sendBtn.disabled = true;

  // Placeholder AI thinking message
  const thinkingId = "thinking_" + Date.now();
  appendChatMessage("ai-msg", `<em>AI is thinking...</em>`, thinkingId);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Failed to get response");
    }

    const data = await response.json();

    // Replace thinking message with real AI response
    const thinkingElem = document.getElementById(thinkingId);
    if (thinkingElem) {
      thinkingElem.innerHTML = `<strong>AI:</strong> ${escapeHtml(data.answer)}`;
    }
  } catch (error) {
    const thinkingElem = document.getElementById(thinkingId);
    if (thinkingElem) {
      thinkingElem.innerHTML = `<strong style="color: #ef4444;">Error:</strong> ${escapeHtml(error.message)}`;
    }
  } finally {
    if (sendBtn) sendBtn.disabled = false;
  }
}

function handleKeyPress(event) {
  if (event.key === "Enter") {
    sendChatMessage();
  }
}

function appendChatMessage(typeClass, htmlContent, elementId = null) {
  const chatMessages = document.getElementById("chatMessages");
  if (!chatMessages) return;

  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${typeClass}`;
  if (elementId) msgDiv.id = elementId;
  msgDiv.innerHTML = htmlContent;

  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to latest message
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, function (m) {
    return {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    }[m];
  });
}

// Sidebar History Management
function addHistoryItem(result) {
  const historyList = document.getElementById("historyList");
  if (!historyList) return;

  const id = "history_" + historyIdCounter++;
  historyStore[id] = result;

  const item = document.createElement("div");
  item.className = "history-item active";
  item.id = id;

  item.innerHTML = `
    <div class="history-content" onclick="openHistoryItem('${id}')">
      <i class="fa-brands fa-youtube" style="color: #ef4444;"></i>
      <div class="history-info">
        <span class="history-title">${result.title}</span>
        <span class="history-date">Just now</span>
      </div>
    </div>
    
    <div class="history-menu-container">
      <button class="history-menu-btn" onclick="toggleDropdown(event, '${id}')">
        <i class="fa-solid fa-ellipsis-vertical"></i>
      </button>
      
      <div class="history-dropdown" id="dropdown_${id}">
        <div class="dropdown-item" onclick="openHistoryItem('${id}')">
          <i class="fa-solid fa-folder-open"></i> Open
        </div>
        <div class="dropdown-item delete" onclick="deleteHistoryItem('${id}')">
          <i class="fa-solid fa-trash"></i> Delete
        </div>
      </div>
    </div>
  `;

  document.querySelectorAll(".history-item").forEach((el) => el.classList.remove("active"));
  historyList.prepend(item);
}

function openHistoryItem(id) {
  const data = historyStore[id];
  if (!data) return;

  document.getElementById("videoTitle").innerText = data.title;
  document.getElementById("summaryText").innerText = data.summary || "No summary available.";

  document.getElementById("resultsContainer").classList.remove("hidden");

  document.querySelectorAll(".history-item").forEach((el) => el.classList.remove("active"));
  const activeElem = document.getElementById(id);
  if (activeElem) activeElem.classList.add("active");

  closeAllDropdowns();
}

function deleteHistoryItem(id) {
  const item = document.getElementById(id);
  if (item) item.remove();

  delete historyStore[id];
  closeAllDropdowns();
}

function toggleDropdown(event, id) {
  event.stopPropagation();
  const dropdown = document.getElementById("dropdown_" + id);
  const isCurrentlyOpen = dropdown ? dropdown.classList.contains("show") : false;

  closeAllDropdowns();

  if (dropdown && !isCurrentlyOpen) {
    dropdown.classList.add("show");
  }
}

function closeAllDropdowns() {
  document.querySelectorAll(".history-dropdown").forEach((el) => el.classList.remove("show"));
}

document.addEventListener("click", closeAllDropdowns);