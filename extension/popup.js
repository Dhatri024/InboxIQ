const analyzeBtn = document.getElementById("analyzeBtn");
const extractBtn = document.getElementById("extractBtn");
const emailInput = document.getElementById("emailInput");
const resultDiv = document.getElementById("result");
const toneSelect = document.getElementById("toneSelect");

// -----------------------------
// EXTRACT EMAIL FROM GMAIL
// -----------------------------
extractBtn.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({
    active: true,
    currentWindow: true,
  });

  chrome.scripting.executeScript(
    {
      target: { tabId: tab.id },
      func: extractEmailContent,
    },
    (results) => {
      if (results && results[0]) {
        emailInput.value = results[0].result;
      }
    }
  );
});

// -----------------------------
// FUNCTION INJECTED INTO GMAIL
// -----------------------------
function extractEmailContent() {
  const emailBody = document.querySelector(".a3s");
  return emailBody ? emailBody.innerText : "No email detected.";
}

// -----------------------------
// ANALYZE EMAIL
// -----------------------------
analyzeBtn.addEventListener("click", async () => {
  const text = emailInput.value;
  if (!text) return;

  const tone = toneSelect?.value || "formal";

  // Loading UI
  resultDiv.innerHTML = `
  <div class="loading-state">
    <div class="spinner"></div>
    <p>Analyzing email with AI...</p>
  </div>
  `;

  try {
    // ✅ FIXED FETCH (UTF-8 SAFE HEADERS ADDED HERE)
    const response = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
      },
      body: JSON.stringify({
        text,
        tone
      }),
    });

    const data = await response.json();

    // -----------------------------
    // SAFE DEFAULTS
    // -----------------------------
    const actionItems = Array.isArray(data.action_items) ? data.action_items : [];
    const keywords = Array.isArray(data.keywords) ? data.keywords : [];
    const entities = Array.isArray(data.entities) ? data.entities : [];

    // -----------------------------
    // RENDER UI
    // -----------------------------
    resultDiv.innerHTML = `
      <div class="card">
        <div class="headerRow">
          <h3>Summary</h3>
          <button class="copyBtn" id="copySummary">Copy</button>
        </div>
        <p id="summaryText">${data.summary || "N/A"}</p>
      </div>

      <div class="card">
        <h3>Sentiment</h3>
        <p>${data.sentiment || "N/A"}</p>
      </div>

      <div class="card">
        <h3>Priority</h3>
        <p>
          <span class="badge ${(data.urgency || "low").toLowerCase()}">
            ${data.urgency || "Low"}
          </span>
        </p>
      </div>

      <div class="card">
        <h3>Category</h3>
        <p>${data.category || "N/A"}</p>
      </div>

      <div class="card">
        <h3>Action Items</h3>
        <ul>
          ${
            actionItems.length
              ? actionItems.map(item => `<li>${item}</li>`).join("")
              : "<li>No action items</li>"
          }
        </ul>
      </div>

      <div class="card">
        <h3>Keywords</h3>
        <div>
          ${
            keywords.length
              ? keywords.map(k => `<span class="badge low">${k}</span>`).join(" ")
              : "No keywords"
          }
        </div>
      </div>

      <div class="card">
        <h3>Entities</h3>
        <ul>
          ${
            entities.length
              ? entities.map(e => `
                  <li><strong>${e.label || "Entity"}</strong> → ${e.text || ""}</li>
                `).join("")
              : "<li>No entities found</li>"
          }
        </ul>
      </div>

      <div class="card">
        <div class="headerRow">
          <h3>Smart Reply</h3>
          <button class="copyBtn" id="copyReply">Copy</button>
        </div>
        <p id="replyText">${data.smart_reply || "N/A"}</p>
      </div>
    `;

    // -----------------------------
    // COPY SUMMARY
    // -----------------------------
    document.getElementById("copySummary")?.addEventListener("click", () => {
      const summaryText = document.getElementById("summaryText")?.innerText || "";
      navigator.clipboard.writeText(summaryText);
      alert("Summary copied!");
    });

    // -----------------------------
    // COPY SMART REPLY
    // -----------------------------
    document.getElementById("copyReply")?.addEventListener("click", () => {
      const replyText = document.getElementById("replyText")?.innerText || "";
      navigator.clipboard.writeText(replyText);
      alert("Reply copied!");
    });

  } catch (error) {
    console.error(error);
    resultDiv.innerHTML = `
      <div class="error-state">
        ❌ Unable to connect to backend
        <p>Please check if FastAPI server is running.</p>
      </div>
    `;
  }
});