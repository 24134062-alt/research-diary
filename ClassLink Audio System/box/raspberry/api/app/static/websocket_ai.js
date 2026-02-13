// WebSocket AI Integration for ClassLink Dashboard
// Connects to AI Service on port 8765

let aiWebSocket = null;
let wsReconnectInterval = null;
let isWsConnected = false;
let pendingMessages = [];

// Initialize WebSocket connection
function initAIWebSocket() {
    // Get Pi IP (same as current page)
    const piIP = window.location.hostname;
    const wsUrl = `ws://${piIP}:8765`;

    console.log('[AI WebSocket] Connecting to:', wsUrl);

    try {
        aiWebSocket = new WebSocket(wsUrl);

        aiWebSocket.onopen = () => {
            console.log('[AI WebSocket] ✅ Connected!');
            isWsConnected = true;
            updateAIStatus('online');

            // Send pending messages
            while (pendingMessages.length > 0) {
                const msg = pendingMessages.shift();
                aiWebSocket.send(JSON.stringify(msg));
            }
        };

        aiWebSocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleAIResponse(data);
            } catch (e) {
                console.error('[AI WebSocket] Parse error:', e);
            }
        };

        aiWebSocket.onerror = (error) => {
            console.error('[AI WebSocket] ❌ Error:', error);
            isWsConnected = false;
            updateAIStatus('error');
        };

        aiWebSocket.onclose = () => {
            console.log('[AI WebSocket] 🔴 Disconnected');
            isWsConnected = false;
            updateAIStatus('offline');

            // Auto reconnect after 3 seconds
            if (!wsReconnectInterval) {
                wsReconnectInterval = setTimeout(() => {
                    console.log('[AI WebSocket] 🔄 Reconnecting...');
                    wsReconnectInterval = null;
                    initAIWebSocket();
                }, 3000);
            }
        };

    } catch (e) {
        console.error('[AI WebSocket] Failed to create connection:', e);
        updateAIStatus('error');
    }
}

// Send message via WebSocket
function sendAIMessage(text) {
    if (!text || !text.trim()) return;

    const message = {
        type: 'question',
        text: text.trim(),
        timestamp: new Date().toISOString()
    };

    // Add to chat UI immediately (user message)
    addChatMessage({
        sender: 'teacher',
        text: text.trim(),
        timestamp: new Date().toLocaleTimeString()
    });

    if (isWsConnected && aiWebSocket.readyState === WebSocket.OPEN) {
        aiWebSocket.send(JSON.stringify(message));
        console.log('[AI WebSocket] Sent:', message);
    } else {
        console.warn('[AI WebSocket] Not connected, queuing message');
        pendingMessages.push(message);
        showToast('⚠️ Đang kết nối AI...', 'warning');

        // Try to reconnect
        if (!wsReconnectInterval) {
            initAIWebSocket();
        }
    }
}

// Handle AI response
function handleAIResponse(data) {
    console.log('[AI WebSocket] Received:', data);

    if (data.type === 'answer') {
        // Add AI response to chat
        addChatMessage({
            sender: 'ai',
            text: data.text || data.answer || 'Không có phản hồi',
            timestamp: new Date().toLocaleTimeString()
        });
    } else if (data.type === 'error') {
        showToast('❌ AI Error: ' + (data.message || 'Unknown error'), 'error');
    }
}

// Add message to chat UI
function addChatMessage(msg) {
    const chatContainer = document.getElementById('teacher-chat-history');
    if (!chatContainer) return;

    // Remove empty state if present
    const emptyState = chatContainer.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const isSelf = msg.sender === 'teacher';
    const isSystem = msg.sender === 'system';

    const msgDiv = document.createElement('div');
    msgDiv.className = `message-bubble ${isSelf ? 'sent' : 'received'}`;
    msgDiv.innerHTML = `
        ${msg.text}
        <div class="msg-meta">${msg.sender === 'ai' ? 'Trợ lý AI' : 'Giáo viên'} • ${msg.timestamp}</div>
    `;

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Update AI status indicator
function updateAIStatus(status) {
    const statusIndicator = document.getElementById('ai-status-indicator');
    const statusText = document.getElementById('ai-status-text');

    if (statusIndicator) {
        const colors = {
            'online': '#22c55e',
            'offline': '#71717a',
            'error': '#ef4444'
        };
        statusIndicator.style.background = colors[status] || '#71717a';
    }

    if (statusText) {
        const texts = {
            'online': 'Online',
            'offline': 'Offline',
            'error': 'Lỗi kết nối'
        };
        statusText.textContent = texts[status] || 'Unknown';
    }
}

// Override original sendMessage function
window.sendMessage = function () {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    sendAIMessage(text);
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('[AI WebSocket] Initializing...');
    initAIWebSocket();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (aiWebSocket) {
        aiWebSocket.close();
    }
    if (wsReconnectInterval) {
        clearTimeout(wsReconnectInterval);
    }
});
