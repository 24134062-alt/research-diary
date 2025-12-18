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
function showView(viewId) {
    // Hide all views
    const views = document.querySelectorAll('.view-section');
    views.forEach(view => view.classList.remove('active'));

    // Show selected view
    const selectedView = document.getElementById(viewId);
    if (selectedView) {
        selectedView.classList.add('active');
    }

    // Update nav active state
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    const activeNavItem = document.querySelector(`[onclick="showView('${viewId}')"]`);
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }

    // Update page title
    const titles = {
        'view-dashboard': 'Trang Chủ Quan Trị',
        'view-devices': 'Quản Lý Thiết Bị',
        'view-wifi': 'Cấu Hình WiFi',
        'view-settings': 'Cài Đặt'
    };
    const subtitles = {
        'view-dashboard': 'Quản lý thiết bị và chế độ giảng dạy',
        'view-devices': 'Theo dõi và điều khiển các thiết bị kết nối',
        'view-wifi': 'Kết nối và quản lý mạng không dây',
        'view-settings': 'Cấu hình hệ thống và công cụ phát triển'
    };
    document.getElementById('page-title').textContent = titles[viewId] || 'Dashboard';
    document.getElementById('page-subtitle').textContent = subtitles[viewId] || '';

    // Fetch system info when opening settings
    if (viewId === 'view-settings') {
        fetchSystemInfo();
    }
}

// --- Chat & Assistant Logic (Messenger Style) ---
let chatSessions = {};
let currentSessionId = 'broadcast';
let isChatOpen = false;
let pollingInterval = null;

function openChatModal() {
    document.getElementById('chat-modal').classList.add('active');
    isChatOpen = true;
    // Clear notification badge
    const badge = document.getElementById('chat-badge');
    if (badge) badge.style.display = 'none';
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

        // Count new messages for badge
        let totalMessages = 0;
        Object.values(sessions).forEach(msgs => {
            totalMessages += msgs.filter(m => m.sender === 'student' || m.sender === 'student_log').length;
        });
        updateChatBadge(totalMessages);

        chatSessions = sessions;
        renderSessions();
        renderChat(currentSessionId);
    } catch (error) {
        // console.error("Error fetching chat:", error);
    }
}

// Update notification badge
let lastMessageCount = 0;
function updateChatBadge(count) {
    const badge = document.getElementById('chat-badge');
    if (!badge) return;

    // Show badge only when there are new messages and modal is closed
    if (count > lastMessageCount && !isChatOpen) {
        const newCount = count - lastMessageCount;
        badge.textContent = newCount > 99 ? '99+' : newCount;
        badge.style.display = 'block';
    }
    lastMessageCount = count;
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

// --- Mic Remote Transcription ---
function clearMicTranscription() {
    const area = document.getElementById('mic-transcription-area');
    if (area) {
        area.innerHTML = '<p style="color: #71717a; text-align: center;">Chưa có dữ liệu thu âm<\/p>';
    }
    showToast('Đã xóa lịch sử thu âm', 'success');
}

function addMicTranscription(text, timestamp) {
    const area = document.getElementById('mic-transcription-area');
    if (!area) return;

    // Clear empty state if present
    if (area.querySelector('p[style*="text-align: center"]')) {
        area.innerHTML = '';
    }

    const entry = document.createElement('div');
    entry.className = 'transcription-entry';
    entry.style.cssText = 'margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #1f1f23;';
    entry.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="color: #71717a; font-size: 0.75rem;">${timestamp || new Date().toLocaleTimeString()}<\/span>
        <\/div>
        <p style="margin: 0; color: #e4e4e7;">"${text}"<\/p>
        <div style="margin-top: 6px;">
            <span style="background: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem;">
                <i class="fas fa-volume-up"><\/i> Broadcast TTS
            <\/span>
        <\/div>
    `;
    area.appendChild(entry);
    area.scrollTop = area.scrollHeight;
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

// --- WiFi Status & Failover ---
let currentWifiStatus = null;
let lastSignalLevel = null;
let hasShownWeakWarning = false;
let hasShownCriticalModal = false;

async function fetchWifiStatus() {
    try {
        const res = await fetch(`${API_URL}/api/wifi-manager/status`);
        const status = await res.json();
        currentWifiStatus = status;
        updateWifiWidget(status);
        checkSignalThresholds(status);
    } catch (e) {
        console.error('WiFi status fetch failed', e);
    }
}

function updateWifiWidget(status) {
    const widget = document.getElementById('wifi-status-widget');
    if (!widget) return;

    if (status.ap_mode) {
        widget.innerHTML = `
            <i class="fas fa-wifi" style="color: #fbbf24"></i>
            <span>Hotspot: ${status.ssid || 'ClassLink-Setup'}</span>
        `;
    } else if (status.connected) {
        const color = status.level === 'strong' ? '#34d399' :
            status.level === 'medium' ? '#fbbf24' :
                status.level === 'weak' ? '#fb923c' : '#ef4444';
        widget.innerHTML = `
            <i class="fas fa-wifi" style="color: ${color}"></i>
            <span>${status.ssid || 'Connected'} (${status.signal}%)</span>
        `;
    } else {
        widget.innerHTML = `
            <i class="fas fa-wifi-slash" style="color: #71717a"></i>
            <span>Not connected</span>
        `;
    }
}

function checkSignalThresholds(status) {
    if (status.ap_mode || !status.connected) {
        hasShownWeakWarning = false;
        hasShownCriticalModal = false;
        return;
    }

    const signal = status.signal;

    // Critical: < 10%
    if (signal < 10 && !hasShownCriticalModal) {
        hasShownCriticalModal = true;
        showCriticalSignalModal(status);
    }
    // Weak: < 30%
    else if (signal < 30 && !hasShownWeakWarning) {
        hasShownWeakWarning = true;
        showWeakSignalToast(signal);
    }
    // Restored: >= 30%
    else if (signal >= 30) {
        hasShownWeakWarning = false;
        hasShownCriticalModal = false;
    }
}

function showWeakSignalToast(signal) {
    showToast(`⚠️ WiFi signal weak (${signal}%)<br>Connection may become unstable`, 'warning');
}

function showCriticalSignalModal(status) {
    const modal = document.getElementById('critical-signal-modal');
    if (!modal) return;

    document.getElementById('critical-ssid').textContent = status.ssid;
    document.getElementById('critical-signal').textContent = `${status.signal}%`;
    modal.classList.add('active');
}

function closeCriticalModal() {
    document.getElementById('critical-signal-modal').classList.remove('active');
}

async function switchToHotspot() {
    closeCriticalModal();
    showToast('Switching to hotspot mode...', 'info');

    try {
        const res = await fetch(`${API_URL}/api/wifi-manager/switch-to-ap`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ confirm: true })
        });
        const result = await res.json();

        if (result.status === 'success') {
            showToast(`✅ Hotspot enabled: ${result.ssid}`, 'success');
            fetchWifiStatus(); // Refresh
        } else {
            showToast(`❌ Hotspot failed: ${result.detail || result.message}`, 'error');
        }
    } catch (e) {
        showToast('❌ Hotspot switch failed', 'error');
    }
}

async function switchToClient() {
    showToast('Switching back to WiFi...', 'info');

    try {
        const res = await fetch(`${API_URL}/api/wifi-manager/switch-to-client`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ confirm: true })
        });
        const result = await res.json();

        if (result.status === 'success') {
            showToast('✅ Switched back to client mode', 'success');
            fetchWifiStatus();
        } else {
            showToast(`❌ Switch failed: ${result.detail || result.message}`, 'error');
        }
    } catch (e) {
        showToast('❌ Mode switch failed', 'error');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = message;

    container.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// --- Code Management ---
async function fetchSystemInfo() {
    try {
        const res = await fetch(`${API_URL}/api/system/system-info`);
        const info = await res.json();

        document.getElementById('git-branch').textContent = info.branch;
        document.getElementById('git-commit').textContent = info.last_commit;
    } catch (e) {
        console.error('Failed to fetch system info', e);
    }
}

async function downloadCode() {
    const password = prompt('Nhập mật khẩu admin để tải code:');
    if (!password) return;

    showToast('Đang tạo file ZIP...', 'info');

    try {
        const res = await fetch(`${API_URL}/api/system/download-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });

        if (res.status === 401) {
            showToast('❌ Mật khẩu không đúng!', 'error');
            return;
        }

        if (!res.ok) {
            showToast('❌ Lỗi tải code', 'error');
            return;
        }

        // Download file
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'classlink-code.zip';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showToast('✅ Code đã tải về thành công!', 'success');
    } catch (e) {
        showToast('❌ Lỗi: ' + e.message, 'error');
    }
}

async function updateCode() {
    const password = prompt('Nhập mật khẩu admin để cập nhật code từ GitHub:');
    if (!password) return;

    showToast('Đang pull code từ GitHub...', 'info');

    try {
        const res = await fetch(`${API_URL}/api/system/update-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });

        if (res.status === 401) {
            showToast('❌ Mật khẩu không đúng!', 'error');
            return;
        }

        const result = await res.json();

        if (result.status === 'success') {
            showToast('✅ ' + result.message, 'success');
            // Refresh system info
            setTimeout(fetchSystemInfo, 1000);
        } else {
            showToast('❌ ' + result.message, 'error');
        }
    } catch (e) {
        showToast('❌ Lỗi: ' + e.message, 'error');
    }
}

// Poll every 2 seconds
setInterval(() => {
    fetchDevices();
    fetchWifiStatus(); // Check WiFi status

    // Only poll chat if active view is chat
    const chatView = document.getElementById('view-chat');
    if (chatView && chatView.classList.contains('active')) {
        fetchChatHistory();
    }
}, 2000);

fetchDevices();
