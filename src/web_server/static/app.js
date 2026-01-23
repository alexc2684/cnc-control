document.addEventListener('DOMContentLoaded', () => {
    const connectBtn = document.getElementById('connectBtn');
    const statusDiv = document.getElementById('status');

    connectBtn.addEventListener('click', async () => {
        // Disable button
        connectBtn.disabled = true;
        connectBtn.textContent = 'Running Test...';
        statusDiv.textContent = 'Communicating with machine...';
        statusDiv.className = 'status-box loading';

        try {
            const response = await fetch('/api/connect', {
                method: 'POST'
            });

            const data = await response.json();

            if (response.ok) {
                statusDiv.textContent = data.message;
                statusDiv.className = 'status-box success';
            } else {
                throw new Error(data.message || 'Unknown error');
            }
        } catch (error) {
            statusDiv.textContent = 'Error: ' + error.message;
            statusDiv.className = 'status-box error';
        } finally {
            // Re-enable button
            connectBtn.disabled = false;
            connectBtn.textContent = 'Connect & Run Test';
        }
    });

    const moveBtn = document.getElementById('moveBtn');
    const moveStatusDiv = document.getElementById('move-status');

    moveBtn.addEventListener('click', async () => {
        const x = parseFloat(document.getElementById('x-input').value);
        const y = parseFloat(document.getElementById('y-input').value);
        const z = parseFloat(document.getElementById('z-input').value);

        moveBtn.disabled = true;
        moveBtn.textContent = 'Moving...';
        moveStatusDiv.textContent = 'Sending move command...';
        moveStatusDiv.className = 'status-box loading';

        try {
            const response = await fetch('/api/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ x, y, z })
            });

            const data = await response.json();

            if (response.ok) {
                moveStatusDiv.textContent = data.message;
                moveStatusDiv.className = 'status-box success';
            } else {
                throw new Error(data.message || data.detail || 'Unknown error');
            }
        } catch (error) {
            moveStatusDiv.textContent = 'Error: ' + error.message;
            moveStatusDiv.className = 'status-box error';
        } finally {
            moveBtn.disabled = false;
            moveBtn.textContent = 'Move to Coordinates';
        }
    });
});
