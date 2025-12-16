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

// Poll every 2 seconds
setInterval(fetchDevices, 2000);
fetchDevices();
