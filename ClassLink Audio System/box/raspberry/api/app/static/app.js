const API_URL = "";

async function fetchDevices() {
    try {
        const res = await fetch(`${API_URL}/api/devices`);
        const data = await res.json();
        renderDevices(data);
    } catch (e) {
        console.error("Failed to fetch devices", e);
    }
}

function renderDevices(devices) {
    const container = document.getElementById('devices-container');
    container.innerHTML = '';

    if (Object.keys(devices).length === 0) {
        container.innerHTML = '<div class="card">No devices connected</div>';
        return;
    }

    Object.values(devices).forEach(device => {
        const div = document.createElement('div');
        div.className = 'card';
        div.innerHTML = `
            <h3>${device.device_id}</h3>
            <div class="info-row">
                <span>Type</span>
                <span>${device.type}</span>
            </div>
            <div class="info-row">
                <span>Status</span>
                <span style="color: ${device.status === 'online' ? '#34d399' : '#94a3b8'}">${device.status}</span>
            </div>
             <div class="info-row">
                <span>Mode</span>
                <span class="mode-badge" onclick="toggleMode('${device.device_id}', '${device.mode}')" style="cursor:pointer">${device.mode}</span>
            </div>
            ${device.battery ? `
            <div class="info-row">
                <span>Battery</span>
                <span>${device.battery}%</span>
            </div>` : ''}
            
            <div class="actions">
                <button class="btn-sm" onclick="setMode('${device.device_id}', 'class')">Class</button>
                <button class="btn-sm" onclick="setMode('${device.device_id}', 'private')">Private</button>
            </div>
        `;
        container.appendChild(div);
    });
}

async function startRecord() {
    await fetch(`${API_URL}/control/record/start`, { method: 'POST' });
}

async function stopRecord() {
    await fetch(`${API_URL}/control/record/stop`, { method: 'POST' });
}

async function setMode(deviceId, mode) {
    await fetch(`${API_URL}/control/mode/${deviceId}/${mode}`, { method: 'POST' });
    fetchDevices(); // Refresh
}

async function setSubject(subject) {
    // Update UI immediately
    document.querySelectorAll('.subject-card').forEach(btn => btn.classList.remove('active'));

    // Map subject to ID: math -> sub-math, literature -> sub-lit
    const id = subject === 'math' ? 'sub-math' : 'sub-lit';
    const el = document.getElementById(id);
    if (el) el.classList.add('active');

    // Send to backend
    await fetch(`${API_URL}/control/subject/${subject}`, { method: 'POST' });
}

// Navigation
function switchView(viewName) {
    // Hide all views
    document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
    // Show selected view
    document.getElementById(`view-${viewName}`).classList.add('active');

    // Update Sidebar Active State
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    // Find button that calls this view
    const navBtns = document.querySelectorAll('.nav-item');
    if (viewName === 'dashboard') navBtns[0].classList.add('active');
    if (viewName === 'wifi') navBtns[1].classList.add('active');
    // if (viewName === 'chat') navBtns[2].classList.add('active');
    if (viewName === 'settings') navBtns[2].classList.add('active');
}

// --- Chat & Assistant Logic (Messenger Style) ---
let chatSessions = {};
let currentSessionId = 'broadcast';
let isChatOpen = false;
let pollingInterval = null;

function openChatModal() {
    document.getElementById('chat-modal').classList.add('active');
    isChatOpen = true;
    fetchChatHistory();
    if (!pollingInterval) {
        pollingInterval = setInterval(fetchChatHistory, 2000);
    }
}

function closeChatModal() {
    document.getElementById('chat-modal').classList.remove('active');
    isChatOpen = false;
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

async function fetchChatHistory() {
    if (!isChatOpen) return;
    try {
        const response = await fetch(`${API_URL}/api/chat/history`);
        const sessions = await response.json();
        chatSessions = sessions;
        renderSessions();
        renderChat(currentSessionId);
    } catch (error) {
        // console.error("Error fetching chat:", error);
    }
}

function renderSessions() {
    const listContainer = document.getElementById('session-list');
    if (!listContainer) return;

    listContainer.innerHTML = '';

    // Sort: broadcast first, then alphanumeric
    const sessionIds = Object.keys(chatSessions).sort((a, b) => {
        if (a === 'broadcast') return -1;
        if (b === 'broadcast') return 1;
        return a.localeCompare(b);
    });

    sessionIds.forEach(sessId => {
        const isActive = sessId === currentSessionId;
        const messages = chatSessions[sessId];
        const lastMsg = messages.length > 0 ? messages[messages.length - 1].text : 'Chưa có tin nhắn';

        let displayName = sessId === 'broadcast' ? 'Kênh Chung' : `Học sinh ${sessId}`;

        const item = document.createElement('div');
        item.className = `session-item ${isActive ? 'active' : ''}`;
        item.onclick = () => selectSession(sessId);
        item.innerHTML = `
            <div class="avatar"><i class="fas ${sessId === 'broadcast' ? 'fa-bullhorn' : 'fa-user'}"></i></div>
            <div class="session-info">
                <h4>${displayName}</h4>
                <p>${lastMsg.substring(0, 25)}${lastMsg.length > 25 ? '...' : ''}</p>
            </div>
        `;
        listContainer.appendChild(item);
    });
}

function selectSession(sessionId) {
    currentSessionId = sessionId;
    renderSessions();
    renderChat(sessionId);
}

function renderChat(sessionId) {
    const chatContainer = document.getElementById('chat-history');
    if (!chatContainer) return;

    // Safety check if session exists, else default to empty
    const messages = chatSessions[sessionId] || [];

    if (messages.length === 0) {
        chatContainer.innerHTML = '<div class="empty-state"><p>Chưa có hội thoại nào</p></div>';
        return;
    }

    // Optimization: if last message ID is same, skip full render? 
    // Ideally yes, but for simplicity/correctness with session switching, we re-render.
    // We can just verify if container has same number of children + same last ID to skip.

    chatContainer.innerHTML = messages.map(msg => {
        const isSelf = msg.sender === 'teacher';
        const isSystem = msg.sender === 'system' || msg.sender === 'student_log';

        if (isSystem || msg.sender === 'student_log') {
            return `
                <div class="message-bubble log">
                   ${msg.text.replace(/\n/g, '<br>')}
                   <div class="msg-meta">${msg.timestamp}</div>
                   ${msg.sender === 'student_log' ? `<button class="btn-xs" style="margin-top:5px" onclick="fillChat('Sửa câu trả lời: ', '')">Sửa lỗi</button>` : ''}
                </div>
            `;
        }
        return `
            <div class="message-bubble ${isSelf ? 'sent' : 'received'}">
                ${msg.text}
                <div class="msg-meta">${msg.sender === 'ai' ? 'Trợ lý AI' : 'Giáo viên'} • ${msg.timestamp}</div>
            </div>
        `;
    }).join('');

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';

    try {
        await fetch(`${API_URL}/api/chat/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                session_id: currentSessionId
            })
        });
        fetchChatHistory();
    } catch (e) {
        console.error("Sending failed:", e);
    }
}

function handleEnter(e) {
    if (e.key === 'Enter') sendMessage();
}

function fillChat(prefix, content) {
    const input = document.getElementById('chat-input');
    input.value = prefix + content;
    input.focus();
}

function scrollToBottom() {
    const container = document.getElementById('chat-history');
    if (container) container.scrollTop = container.scrollHeight;
}

// --- WiFi Management ---
async function scanWiFi() {
    const button = document.querySelector('[onclick="scanWiFi()"]');
    const container = document.getElementById('wifi-list');

    // Show loading state
    if (button) button.disabled = true;
    if (button) button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang quét...';

    try {
        const res = await fetch(`${API_URL}/api/wifi/scan`);
        const networks = await res.json();
        renderWiFiNetworks(networks);
    } catch (e) {
        console.error("WiFi scan failed", e);
        if (container) {
            container.innerHTML = '<div class="empty-state"><p>❌ Lỗi quét WiFi. Vui lòng thử lại.</p></div>';
        }
    } finally {
        // Restore button
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-broadcast-tower"></i> Quét Mạng';
        }
    }
}

function renderWiFiNetworks(networks) {
    const container = document.getElementById('wifi-list');
    if (!container) return;

    if (!networks || networks.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Không tìm thấy mạng WiFi nào</p></div>';
        return;
    }

    // Helper function to get WiFi icon based on signal strength
    function getSignalIcon(signal) {
        if (signal >= 75) return '<i class="fas fa-wifi" style="color: #34d399"></i>'; // Strong - Green
        if (signal >= 50) return '<i class="fas fa-wifi" style="color: #fbbf24"></i>'; // Medium - Yellow
        if (signal >= 25) return '<i class="fas fa-wifi" style="color: #fb923c"></i>'; // Weak - Orange
        return '<i class="fas fa-wifi" style="color: #ef4444"></i>'; // Very weak - Red
    }

    // Helper function to get signal bars (visual representation)
    function getSignalBars(signal) {
        const bars = Math.ceil(signal / 25); // 0-25=1, 26-50=2, 51-75=3, 76-100=4
        let html = '<div class="signal-bars" style="display: inline-flex; gap: 2px; align-items: flex-end;">';
        for (let i = 1; i <= 4; i++) {
            const height = i * 25;
            const color = i <= bars ? (signal >= 75 ? '#34d399' : signal >= 50 ? '#fbbf24' : signal >= 25 ? '#fb923c' : '#ef4444') : '#334155';
            html += `<div style="width: 3px; height: ${height}%; background: ${color}; border-radius: 1px;"></div>`;
        }
        html += '</div>';
        return html;
    }

    container.innerHTML = networks.map(network => `
        <div class="wifi-item" onclick="connectToWiFi('${network.ssid}', ${network.secure})">
            <div class="wifi-info">
                <h4>${getSignalIcon(network.signal)} ${network.ssid}</h4>
                <small>
                    ${getSignalBars(network.signal)}
                    <span style="margin-left: 8px;">Signal: ${network.signal}%</span>
                    ${network.secure ? '🔒 Secured' : '🔓 Open'}
                </small>
            </div>
            <button class="btn-sm">Kết nối</button>
        </div>
    `).join('');
}

function connectToWiFi(ssid, isSecure) {
    const password = isSecure ? prompt(`Nhập mật khẩu cho "${ssid}":`) : null;

    if (isSecure && !password) {
        alert('Cần mật khẩu để kết nối!');
        return;
    }

    fetch(`${API_URL}/api/wifi/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ssid, password })
    })
        .then(res => res.json())
        .then(data => {
            alert(`✅ ${data.message}`);
        })
        .catch(e => {
            console.error("Connection failed", e);
            alert('❌ Kết nối thất bại. Vui lòng thử lại.');
        });
}

// Poll every 2 seconds
setInterval(() => {
    fetchDevices();

    // Only poll chat if active view is chat
    const chatView = document.getElementById('view-chat');
    if (chatView && chatView.classList.contains('active')) {
        fetchChatHistory();
    }
}, 2000);

fetchDevices();
