async function scanWiFi() {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const scanBtn = document.getElementById('scan-btn');
    const wifiBody = document.getElementById('wifi-body');
    const networkCount = document.getElementById('network-count');

    statusDot.classList.add('busy');
    statusText.textContent = 'Scanning...';
    scanBtn.disabled = true;

    try {
        const response = await fetch('/api/scan');
        const networks = await response.json();
        
        updateTable(networks);
        networkCount.textContent = `${networks.length} found`;
    } catch (error) {
        console.error('Scan failed:', error);
        wifiBody.innerHTML = '<tr><td colspan="5" class="empty-state">Error during scan</td></tr>';
    } finally {
        statusDot.classList.remove('busy');
        statusText.textContent = 'Ready';
        scanBtn.disabled = false;
    }
}

function updateTable(networks) {
    const wifiBody = document.getElementById('wifi-body');
    
    if (networks.length === 0) {
        wifiBody.innerHTML = '<tr><td colspan="5" class="empty-state">No networks found</td></tr>';
        return;
    }

    // Sort by RSSI descending
    networks.sort((a, b) => b.rssi - a.rssi);

    wifiBody.innerHTML = networks.map(net => {
        const percentage = Math.min(100, Math.max(0, 2 * (net.rssi + 100)));
        let color = '--danger';
        if (percentage >= 80) color = '--success';
        else if (percentage >= 50) color = '--warning';

        return `
            <tr>
                <td style="font-weight: 500;">${net.ssid}</td>
                <td>
                    <div class="signal-bar">
                        <span style="min-width: 40px;">${percentage}%</span>
                        <div class="bar-bg">
                            <div class="bar-fill" style="width: ${percentage}%; background-color: var(${color});"></div>
                        </div>
                    </div>
                </td>
                <td>${net.band}</td>
                <td>${net.channel}</td>
                <td style="color: var(--text-secondary); font-size: 0.85rem;">${net.security}</td>
            </tr>
        `;
    }).join('');
}

document.getElementById('scan-btn').addEventListener('click', scanWiFi);

// Initial scan
scanWiFi();

// Auto refresh every 30 seconds
setInterval(scanWiFi, 30000);
