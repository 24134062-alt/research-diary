// Simplified test version of app.js for local demo

// View switching
function showView(viewId) {
    document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    document.getElementById(viewId).classList.add('active');
    event.target.closest('.nav-item').classList.add('active');

    // Update header
    const titles = {
        'view-dashboard': ['Trang Chủ Quản Trị', 'Quản lý thiết bị và chế độ giảng dạy'],
        'view-wifi': ['Cấu Hình WiFi', 'Quản lý kết nối mạng'],
        'view-settings': ['Cài Đặt', 'Thông tin hệ thống']
    };

    if (titles[viewId]) {
        document.getElementById('page-title').textContent = titles[viewId][0];
        document.getElementById('page-subtitle').textContent = titles[viewId][1];
    }
}

// Subject selection
function setSubject(subject) {
    document.querySelectorAll('.subject-card').forEach(c => c.classList.remove('active'));

    if (subject === 'math') {
        document.getElementById('sub-math').classList.add('active');
        showToast('Đã chuyển sang chế độ Tự Nhiên', 'success');
    } else {
        document.getElementById('sub-lit').classList.add('active');
        showToast('Đã chuyển sang chế độ Xã Hội', 'success');
    }
}

// Chat modal
function openChatModal() {
    document.getElementById('chat-modal').classList.add('active');
    // Clear notification badge
    const badge = document.getElementById('chat-badge');
    if (badge) badge.style.display = 'none';
}

function closeChatModal() {
    document.getElementById('chat-modal').classList.remove('active');
}

// WiFi functions
function scanWiFi() {
    showToast('Đang quét mạng WiFi...', 'info');
}

function selectWiFi(ssid) {
    showToast('Đã chọn mạng: ' + ssid, 'success');
}

// Device refresh
function refreshDevices() {
    showToast('Đang làm mới danh sách thiết bị...', 'info');
}

// Toast notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast ' + type;
    toast.style.cssText = `
        background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

// Initialize
console.log('ClassLink Web Test - Ready');

// Add pulse animation
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
`;
document.head.appendChild(style);

// Clear transcription
function clearTranscription() {
    document.getElementById('transcription-area').innerHTML = '<p style="color: #71717a; text-align: center; padding: 20px;">Không có dữ liệu thu âm</p>';
    showToast('Đã xóa lịch sử thu âm', 'success');
}
