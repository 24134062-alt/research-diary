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

// --- Broadcast TTS Functions ---
function setBroadcast(text) {
    const input = document.getElementById('broadcast-input');
    if (input) {
        input.value = text;
        input.focus();
    }
}

async function sendBroadcast() {
    const input = document.getElementById('broadcast-input');
    const text = input.value.trim();
    if (!text) {
        showToast('❌ Vui lòng nhập nội dung thông báo!', 'warning');
        return;
    }

    try {
        showToast('📢 Đang gửi broadcast...', 'info');

        const response = await fetch(`${API_URL}/api/broadcast`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        const result = await response.json();

        if (result.status === 'sent') {
            showToast('✅ Đã gửi TTS tới tất cả kính!', 'success');
            input.value = '';
        } else if (result.status === 'no_glasses') {
            showToast('⚠️ Chưa có kính nào kết nối!', 'warning');
        } else {
            showToast(`❌ ${result.message || 'Lỗi gửi broadcast'}`, 'error');
        }
    } catch (e) {
        console.error('Broadcast failed:', e);
        showToast('❌ Lỗi kết nối. Thử lại sau.', 'error');
    }
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
let currentConnectedSSID = null;

async function scanWiFi() {
    const button = document.querySelector('[onclick="scanWiFi()"]');
    const container = document.getElementById('wifi-list');

    // Show loading state
    if (button) button.disabled = true;
    if (button) button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang quét...';

    try {
        // Get connected WiFi first
        const connRes = await fetch(`${API_URL}/api/wifi/connected`);
        const connData = await connRes.json();
        currentConnectedSSID = connData.connected ? connData.ssid : null;

        // Then scan networks
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

    container.innerHTML = networks.map(network => {
        const isConnected = currentConnectedSSID && network.ssid === currentConnectedSSID;

        if (isConnected) {
            // Connected WiFi - show disconnect button
            return `
            <div class="wifi-item">
                <div class="wifi-info">
                    <h4>${getSignalIcon(network.signal)} ${network.ssid} <span style="color: #22c55e; font-size: 0.8em;">(Đang dùng)</span></h4>
                    <small>
                        ${getSignalBars(network.signal)}
                        <span style="margin-left: 8px;">Signal: ${network.signal}%</span>
                        ${network.secure ? '🔒 Secured' : '🔓 Open'}
                    </small>
                </div>
                <button class="btn-sm" style="background: #ef4444;" onclick="showDisconnectModal()">
                    <i class="fas fa-times"></i> Ngắt
                </button>
            </div>
            `;
        }

        // Other WiFi - show connect button
        return `
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
    `}).join('');
}

function connectToWiFi(ssid, isSecure) {
    const password = isSecure ? prompt(`Nhập mật khẩu cho "${ssid}":`) : null;

    if (isSecure && !password) {
        alert('Cần mật khẩu để kết nối!');
        return;
    }

    showToast('🔄 Đang kết nối...', 'info');

    fetch(`${API_URL}/api/wifi/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ssid, password })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success' && data.new_url) {
                // Show modal with new URL
                showNewIPModal(ssid, data.new_url);
            } else if (data.status === 'success') {
                showToast(`✅ ${data.message}`, 'success');
            } else {
                showToast(`❌ ${data.message}`, 'error');
            }
        })
        .catch(e => {
            console.error("Connection failed", e);
            showToast('❌ Kết nối thất bại. Vui lòng thử lại.', 'error');
        });
}

// Show modal with new IP after WiFi connection
function showNewIPModal(ssid, newUrl) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('new-ip-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'new-ip-modal';
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content" style="text-align: center;">
                <h3 style="color: #22c55e;">✅ Kết nối thành công!</h3>
                <p style="color: var(--text-secondary);">Đã kết nối WiFi: <span id="new-ssid" style="color: white;"></span></p>
                <div style="margin: 20px 0;">
                    <p style="margin-bottom: 10px;">Truy cập web mới tại:</p>
                    <div style="background: #09090b; padding: 15px; border-radius: 8px; border: 1px solid var(--primary);">
                        <code id="new-url" style="font-size: 1.1rem; color: var(--primary);"></code>
                    </div>
                </div>
                <div class="modal-actions" style="justify-content: center; gap: 12px;">
                    <button class="btn-primary" onclick="openNewUrl()">
                        <i class="fas fa-external-link-alt"></i> Truy cập Web
                    </button>
                    <button class="btn-secondary" onclick="copyNewUrl()">
                        <i class="fas fa-copy"></i> Sao chép
                    </button>
                    <button class="btn-ghost" onclick="closeNewIPModal()">Đóng</button>
                </div>
                <p style="margin-top: 15px; font-size: 0.85rem; color: var(--text-secondary);">
                    ⚠️ Kết nối WiFi <span id="new-ssid-2" style="color: white;"></span> trên thiết bị của bạn trước khi truy cập.
                </p>
            </div>
        `;
        document.body.appendChild(modal);
    } else {
        modal.classList.add('active');
    }

    // Update content
    document.getElementById('new-ssid').textContent = ssid;
    document.getElementById('new-ssid-2').textContent = ssid;
    document.getElementById('new-url').textContent = newUrl;
    modal.dataset.url = newUrl;
}

function openNewUrl() {
    const modal = document.getElementById('new-ip-modal');
    const url = modal ? modal.dataset.url : '';
    if (url) {
        window.open(url, '_blank');
        showToast('🌐 Đang mở trang web mới...', 'info');
    }
}

function copyNewUrl() {
    const modal = document.getElementById('new-ip-modal');
    const url = modal ? modal.dataset.url : '';

    navigator.clipboard.writeText(url).then(() => {
        showToast('📋 Đã sao chép URL!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('📋 Đã sao chép URL!', 'success');
    });
}

function closeNewIPModal() {
    const modal = document.getElementById('new-ip-modal');
    if (modal) modal.classList.remove('active');
}

// --- Disconnect WiFi with AP Mode Switch ---
function showDisconnectModal() {
    // Create modal if it doesn't exist
    let modal = document.getElementById('disconnect-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'disconnect-modal';
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content" style="text-align: center;">
                <h3 style="color: #f59e0b;">⚠️ Ngắt kết nối WiFi?</h3>
                <p style="color: var(--text-secondary);">
                    Raspberry Pi sẽ chuyển sang chế độ Access Point.<br>
                    Bạn cần kết nối lại WiFi để truy cập web.
                </p>
                <div style="background: #27272a; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0 0 8px 0; color: white;"><strong>Thông tin kết nối mới:</strong></p>
                    <p style="margin: 4px 0; color: var(--text-secondary);">📶 WiFi: <span style="color: #22c55e;">ClassLink-Setup</span></p>
                    <p style="margin: 4px 0; color: var(--text-secondary);">🔑 Password: <span style="color: #22c55e;">classlink2024</span></p>
                    <p style="margin: 4px 0; color: var(--text-secondary);">🌐 URL: <span style="color: #22c55e;">http://192.168.4.1:8000</span></p>
                </div>
                <div class="modal-actions" style="justify-content: center; gap: 12px;">
                    <button class="btn-primary" style="background: #f59e0b;" onclick="confirmDisconnect()">
                        <i class="fas fa-wifi"></i> Ngắt kết nối
                    </button>
                    <button class="btn-ghost" onclick="closeDisconnectModal()">Hủy</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    } else {
        modal.classList.add('active');
    }
}

function closeDisconnectModal() {
    const modal = document.getElementById('disconnect-modal');
    if (modal) modal.classList.remove('active');
}

async function confirmDisconnect() {
    closeDisconnectModal();
    showToast('🔄 Đang ngắt kết nối và bật AP mode...', 'info');

    try {
        const res = await fetch(`${API_URL}/api/wifi/disconnect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();

        if (data.status === 'success') {
            showToast(`✅ ${data.message}`, 'success');
            // Show info about new connection
            setTimeout(() => {
                alert(`📶 Đã chuyển sang AP mode!\n\nKết nối WiFi: ${data.ap_ssid}\nPassword: ${data.ap_password || 'classlink2024'}\nURL: ${data.ap_url}`);
            }, 1000);
        } else {
            showToast(`❌ ${data.message}`, 'error');
        }
    } catch (e) {
        console.error("Disconnect failed", e);
        showToast('❌ Lỗi ngắt kết nối.', 'error');
    }
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

// ===== PC AI SERVICE FUNCTIONS =====

// Download PC installer
function downloadPCInstaller() {
    showToast('📥 Đang tải installer...', 'info');

    // Create download link for installer package
    const link = document.createElement('a');
    link.href = '/api/system/pc-installer';
    link.download = 'ClassLink-PC-Installer.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Show instruction modal after a short delay
    setTimeout(() => {
        showPCInstallerModal();
    }, 1000);
}

// Show PC Installer instruction modal
function showPCInstallerModal() {
    const modal = document.getElementById('pc-installer-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

// Close PC Installer modal
function closePCInstallerModal() {
    const modal = document.getElementById('pc-installer-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Check PC service status
async function checkPCStatus() {
    const statusEl = document.getElementById('pc-status');
    const loadingEl = document.getElementById('pc-loading');
    const loadingStatus = document.getElementById('pc-loading-status');

    // Show loading
    loadingEl.style.display = 'block';
    loadingStatus.textContent = 'Đang kết nối tới PC Service...';

    try {
        // Try to ping PC service via MQTT broker
        const res = await fetch(`${API_URL}/api/system/pc-status`, {
            method: 'GET',
            timeout: 5000
        });

        if (res.ok) {
            const data = await res.json();

            if (data.connected) {
                // Update status to connected
                statusEl.innerHTML = `
                    <span style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%;"></span>
                    <span style="color: #86efac;">Đã kết nối</span>
                `;
                statusEl.style.background = 'rgba(34, 197, 94, 0.2)';
                loadingStatus.textContent = 'PC Service đang chạy!';
                showToast('✅ PC AI Service đã kết nối!', 'success');
            } else {
                // Not connected
                statusEl.innerHTML = `
                    <span style="width: 8px; height: 8px; background: #f59e0b; border-radius: 50%;"></span>
                    <span style="color: #fcd34d;">Chờ kết nối</span>
                `;
                statusEl.style.background = 'rgba(245, 158, 11, 0.2)';
                loadingStatus.textContent = 'PC Service chưa kết nối. Hãy chạy installer!';
                showToast('⚠️ PC chưa kết nối. Chạy install.bat trên PC!', 'info');
            }
        } else {
            throw new Error('Server error');
        }
    } catch (e) {
        // Error or not installed
        statusEl.innerHTML = `
            <span style="width: 8px; height: 8px; background: #ef4444; border-radius: 50%;"></span>
            <span style="color: #fca5a5;">Chưa cài đặt</span>
        `;
        statusEl.style.background = 'rgba(239, 68, 68, 0.2)';
        loadingStatus.textContent = 'Không thể kết nối. Hãy tải và cài installer!';
    }

    // Hide loading after 2 seconds
    setTimeout(() => {
        loadingEl.style.display = 'none';
    }, 2000);
}

// CSS for spinner animation
const spinnerStyle = document.createElement('style');
spinnerStyle.textContent = `
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(spinnerStyle);

// ===== DEBUG TERMINAL FUNCTIONS =====

// Store admin password for session
let adminPassword = null;

// Set command in input field
function setCommand(cmd) {
    document.getElementById('cmd-input').value = cmd;
    document.getElementById('cmd-input').focus();
}

// Run debug command
async function runDebugCommand() {
    const cmdInput = document.getElementById('cmd-input');
    const outputEl = document.getElementById('cmd-output');
    const command = cmdInput.value.trim();

    if (!command) {
        showToast('Vui lòng nhập lệnh!', 'error');
        return;
    }

    // Ask for password if not stored
    if (!adminPassword) {
        adminPassword = prompt('Nhập mật khẩu admin để chạy lệnh:');
        if (!adminPassword) return;
    }

    // Show loading
    outputEl.innerHTML = `<span style="color: #f59e0b;">$ ${command}</span>\n<span style="color: #71717a;">Đang thực thi...</span>`;

    try {
        const res = await fetch(`${API_URL}/api/system/run-command`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                password: adminPassword,
                command: command,
                timeout: 30
            })
        });

        if (res.status === 401) {
            adminPassword = null;
            outputEl.innerHTML = `<span style="color: #ef4444;">❌ Mật khẩu không đúng!</span>`;
            return;
        }

        if (res.status === 400) {
            const error = await res.json();
            outputEl.innerHTML = `<span style="color: #ef4444;">🛡️ ${error.detail}</span>`;
            return;
        }

        const result = await res.json();

        // Format output
        let output = `<span style="color: #f59e0b;">$ ${command}</span>\n`;
        output += `<span style="color: #71717a;">[cwd: ${result.cwd || 'N/A'}]</span>\n\n`;

        if (result.status === 'success') {
            if (result.stdout) {
                output += `<span style="color: #22c55e;">${escapeHtml(result.stdout)}</span>`;
            } else {
                output += `<span style="color: #71717a;">(Không có output)</span>`;
            }
        } else if (result.status === 'error') {
            output += `<span style="color: #ef4444;">${escapeHtml(result.stderr || result.message || 'Error')}</span>`;
        } else if (result.status === 'timeout') {
            output += `<span style="color: #f59e0b;">⏱️ ${result.message}</span>`;
        }

        output += `\n\n<span style="color: #71717a;">Exit code: ${result.returncode !== undefined ? result.returncode : 'N/A'}</span>`;

        outputEl.innerHTML = output;
        outputEl.scrollTop = outputEl.scrollHeight;

    } catch (e) {
        outputEl.innerHTML = `<span style="color: #ef4444;">❌ Lỗi: ${e.message}</span>`;
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
