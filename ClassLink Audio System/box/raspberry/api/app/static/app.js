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
