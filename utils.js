const API_URL = "http://localhost:5000/api";
const token = localStorage.getItem("token");

async function apiRequest(endpoint, method = "GET", body) {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(API_URL + endpoint, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined
    });
    return res.json();
}

// ------------------------ DARK MODE ------------------------
function loadDarkMode() {
    const enabled = localStorage.getItem("dark-mode") === "true";
    if (enabled) {
        document.body.classList.add("dark-mode");
        const toggleBtn = document.getElementById("darkToggle");
        if (toggleBtn) toggleBtn.innerText = "☀️ Light Mode";
    }
}

function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
    const enabled = document.body.classList.contains("dark-mode");
    localStorage.setItem("dark-mode", enabled);
    const toggleBtn = document.getElementById("darkToggle");
    if (toggleBtn) toggleBtn.innerText = enabled ? "☀️ Light Mode" : "🌙 Dark Mode";
}

// --------------------- JOB ACTIONS --------------------------
async function acceptFreelancer(jobId, freelancerId) {
    await apiRequest(`/jobs/${jobId}/accept/${freelancerId}`, "POST");
    alert("Freelancer Accepted!");
    loadJobs();
}

async function markJobCompleted(jobId) {
    await apiRequest(`/jobs/${jobId}/complete`, "POST");
    alert("Job marked as completed!");
    loadJobs();
}

async function approveCompletion(jobId) {
    await apiRequest(`/jobs/${jobId}/approve`, "POST");
    alert("Job approved!");
    loadJobs();
}

async function releasePayment(jobId) {
    await apiRequest(`/jobs/${jobId}/release-payment`, "POST");
    alert("Payment released!");
    loadJobs();
}

// ------------------- NOTIFICATIONS -------------------------
async function loadNotifications() {
    if (!token) return;
    const notifs = await apiRequest("/notifications");
    const count = notifs.filter(n => !n.read).length;
    const notifCount = document.getElementById("notifCount");
    if (notifCount) notifCount.innerText = count;

    const list = document.getElementById("notifList");
    if (!list) return;

    list.innerHTML = notifs.length === 0
        ? "<li class='dropdown-item'>No notifications</li>"
        : notifs.map(n => `
            <li class="dropdown-item ${n.read ? '' : 'fw-bold'}"
                onclick="markNotificationAsRead('${n._id}')">
                ${n.message}<br>
                <small class="text-muted">${new Date(n.createdAt).toLocaleString()}</small>
            </li>
        `).join("");
}

async function markNotificationAsRead(id) {
    await apiRequest(`/notifications/read/${id}`, "POST");
    loadNotifications();
}

// Auto-refresh notifications
setInterval(loadNotifications, 5000);

// ------------------- BITCOIN/WALLET ----------------------
async function getBitcoinBalance() {
    if (!token) return { btc: 0, fiat: 0 };
    try {
        const balance = await apiRequest("/wallet/balance");
        return balance;
    } catch (error) {
        console.error("Failed to fetch bitcoin balance:", error);
        return { btc: 0, fiat: 0 };
    }
}

async function withdrawBitcoin(amount, address) {
    if (!token) {
        alert("Please log in first");
        return;
    }
    try {
        const result = await apiRequest("/wallet/withdraw", "POST", { amount, address });
        alert("Withdrawal initiated! Transaction ID: " + result.txId);
    } catch (error) {
        alert("Withdrawal failed: " + error.message);
    }
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.value || element.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const originalText = element.previousElementSibling?.innerText || "Copy";
        alert("Copied to clipboard!");
    }).catch(err => {
        console.error("Failed to copy:", err);
    });
}

// ------------------- HELPER -------------------------------
function getUserId() {
    return localStorage.getItem("userId");
}
