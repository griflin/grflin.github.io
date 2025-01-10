document.addEventListener('DOMContentLoaded', function() {
    const initForm = document.getElementById('initForm');
    const scanBtn = document.getElementById('scanBtn');
    const networksList = document.getElementById('networksList');
    const statusLog = document.getElementById('statusLog');

    function log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const entry = `[${timestamp}] ${message}\n`;
        statusLog.innerHTML += `<span class="status-${type}">${entry}</span>`;
        statusLog.scrollTop = statusLog.scrollHeight;
    }

    initForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const data = {
            interface: document.getElementById('interface').value,
            ssid: document.getElementById('ssid').value,
            wordlist: document.getElementById('wordlist').value
        };

        try {
            const response = await fetch('/api/init', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                log('Tool initialized successfully', 'success');
                scanBtn.disabled = false;
            } else {
                log(`Initialization failed: ${result.message}`, 'error');
            }
        } catch (error) {
            log(`Error: ${error.message}`, 'error');
        }
    });

    scanBtn.addEventListener('click', async function() {
        try {
            log('Starting network scan...');
            networksList.innerHTML = '';
            
            const response = await fetch('/api/scan');
            const result = await response.json();
            
            if (result.status === 'success') {
                Object.entries(result.networks).forEach(([bssid, data]) => {
                    const row = document.createElement('tr');
                    row.className = 'network-row';
                    row.innerHTML = `
                        <td>${data.ssid}</td>
                        <td>${bssid}</td>
                        <td>${data.channel}</td>
                        <td>${data.signal} dBm</td>
                        <td>${data.encryption}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" 
                                    onclick="startAttack('${bssid}')">
                                Attack
                            </button>
                        </td>
                    `;
                    networksList.appendChild(row);
                });
                log(`Found ${Object.keys(result.networks).length} networks`, 'success');
            } else {
                log(`Scan failed: ${result.message}`, 'error');
            }
        } catch (error) {
            log(`Error: ${error.message}`, 'error');
        }
    });
});

async function startAttack(bssid) {
    try {
        log(`Starting attack on ${bssid}...`);
        
        const response = await fetch('/api/attack', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ bssid })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            log(`Attack completed on ${bssid}`, 'success');
        } else {
            log(`Attack failed: ${result.message}`, 'error');
        }
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
    }
} 