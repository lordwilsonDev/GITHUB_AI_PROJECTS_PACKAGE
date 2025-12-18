document.addEventListener('DOMContentLoaded', () => {
    const statusBody = document.getElementById('status-body');

    const renderTable = (data) => {
        // Clear existing rows
        statusBody.innerHTML = '';

        if (!data || data.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="3" style="text-align: center;">Awaiting data...</td>`;
            statusBody.appendChild(row);
            return;
        }

        // Sort data alphabetically by name
        data.sort((a, b) => a.name.localeCompare(b.name));

        // Populate with new rows
        data.forEach(project => {
            const row = document.createElement('tr');
            const statusClass = `status-${project.status.toLowerCase()}`;
            
            row.innerHTML = `
                <td>${project.name}</td>
                <td class="${statusClass}">${project.status.toUpperCase()}</td>
                <td>${project.details}</td>
            `;
            statusBody.appendChild(row);
        });
    };

    const fetchStatus = async () => {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            renderTable(data);
        } catch (error) {
            console.error("Failed to fetch status:", error);
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="3" style="text-align: center; color: #f44336;">Failed to connect to dashboard server.</td>`;
            statusBody.innerHTML = '';
            statusBody.appendChild(row);
        }
    };

    // Fetch status on initial load
    fetchStatus();

    // Fetch status every 15 seconds
    setInterval(fetchStatus, 15000);
});
