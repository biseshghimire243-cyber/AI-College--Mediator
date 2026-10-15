
const API_BASE_URL = "";

const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const messagesContainer = document.getElementById("messages");
const welcomeScreen = document.getElementById("welcomeScreen");
const sendBtn = document.getElementById("sendBtn");
const charCount = document.getElementById("charCount");
const connectionStatus = document.getElementById("connectionStatus");
const statusDot = document.getElementById("statusDot");
const newChatBtn = document.getElementById("newChatBtn");
const historyBtn = document.getElementById("historyBtn");
const homeBtn = document.getElementById("homeBtn");
const sidebar = document.getElementById("sidebar");
const menuBtn = document.getElementById("menuBtn");
const toast = document.getElementById("toast");

let isSending = false;
let toastTimeout;

function showToast(message) {
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add("show");

    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

async function checkBackend() {
    try {
        const response = await fetch("/api/health");

        if (!response.ok) {
            throw new Error("Health check failed");
        }

        const data = await response.json();

        if (statusDot) statusDot.className = "status-dot online";

        if (connectionStatus) {
            connectionStatus.textContent =
                data.status === "healthy"
                    ? "Backend connected"
                    : "Backend online";
        }
    } catch {
        if (statusDot) statusDot.className = "status-dot offline";
        if (connectionStatus) connectionStatus.textContent = "Backend offline";
    }
}

function getTime() {
    return new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function createMessageElement(role, text, isTyping = false) {
    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = role === "assistant" ? "✦" : "S";

    const content = document.createElement("div");
    content.className = "message-content";

    const name = document.createElement("span");
    name.className = "message-name";
    name.textContent = role === "assistant" ? "CampusAI Assistant" : "You";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (isTyping) {
        const indicator = document.createElement("div");
        indicator.className = "typing-indicator";
        indicator.setAttribute("aria-label", "Assistant is thinking");

        for (let i = 0; i < 3; i++) {
            indicator.appendChild(document.createElement("span"));
        }

        bubble.appendChild(indicator);
    } else {
        bubble.textContent = text;
    }

    const meta = document.createElement("div");
    meta.className = "message-meta";
    meta.textContent = getTime();

    content.append(name, bubble, meta);
    row.append(avatar, content);
    messagesContainer.appendChild(row);

    return row;
}

function scrollToLatest() {
    messagesContainer.lastElementChild?.scrollIntoView({
        behavior: "smooth",
        block: "end"
    });
}

function updateComposer() {
    if (!messageInput) return;

    if (charCount) {
        charCount.textContent = `${messageInput.value.length} / 2000`;
    }

    messageInput.style.height = "auto";
    messageInput.style.height =
        `${Math.min(messageInput.scrollHeight, 140)}px`;
}

async function sendMessage(question) {
    const cleanQuestion = question.trim();

    if (!cleanQuestion || isSending) return;

    if (
        !chatForm ||
        !messageInput ||
        !messagesContainer ||
        !welcomeScreen ||
        !sendBtn
    ) {
        console.error("Chat HTML elements are missing. Check index.html IDs.");
        return;
    }

    isSending = true;
    sendBtn.disabled = true;

    welcomeScreen.hidden = true;
    createMessageElement("user", cleanQuestion);

    const typingRow = createMessageElement("assistant", "", true);
    scrollToLatest();

    messageInput.value = "";
    updateComposer();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: cleanQuestion })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.answer || data.error || data.message ||
                `Server error: ${response.status}`
            );
        }

        const answer = data.answer || data.response || data.message;

        if (typeof answer !== "string" || !answer.trim()) {
            throw new Error("The server did not return a valid answer.");
        }

        typingRow.querySelector(".message-bubble").textContent = answer;
        typingRow.querySelector(".message-meta").textContent = getTime();
    } catch (error) {
        typingRow.querySelector(".message-bubble").textContent =
            "Unable to get a response. Check that Flask is running and /api/chat is available.";

        console.error("Chat error:", error);
    } finally {
        isSending = false;
        sendBtn.disabled = false;
        messageInput.focus();
        scrollToLatest();
    }
}

if (chatForm) {
    chatForm.addEventListener("submit", (event) => {
        event.preventDefault();
        sendMessage(messageInput.value);
    });
}

if (messageInput) {
    messageInput.addEventListener("input", updateComposer);

    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            chatForm?.requestSubmit();
        }
    });
}

document.querySelectorAll("[data-question]").forEach((button) => {
    button.addEventListener("click", () => {
        sendMessage(button.dataset.question);

        if (sidebar) sidebar.classList.remove("open");
    });
});

if (newChatBtn) {
    newChatBtn.addEventListener("click", () => {
        if (isSending) {
            showToast("Please wait for the current response.");
            return;
        }

        messagesContainer.replaceChildren();
        welcomeScreen.hidden = false;
        messageInput.value = "";
        updateComposer();

        if (sidebar) sidebar.classList.remove("open");

        messageInput.focus();
    });
}

if (homeBtn) {
    homeBtn.addEventListener("click", () => {
        if (isSending) return;

        messagesContainer.replaceChildren();
        welcomeScreen.hidden = false;

        if (sidebar) sidebar.classList.remove("open");
    });
}

if (historyBtn) {
    historyBtn.addEventListener("click", () => {
        showToast("Chat history will be available after database integration.");

        if (sidebar) sidebar.classList.remove("open");
    });
}

if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });
}

document.addEventListener("click", (event) => {
    if (
        window.innerWidth <= 650 &&
        sidebar &&
        menuBtn &&
        sidebar.classList.contains("open") &&
        !sidebar.contains(event.target) &&
        !menuBtn.contains(event.target)
    ) {
        sidebar.classList.remove("open");
    }
});

updateComposer();
checkBackend();
setInterval(checkBackend, 30000);
