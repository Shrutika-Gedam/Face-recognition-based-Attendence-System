document.addEventListener('DOMContentLoaded', function() {
    const registerBtn = document.getElementById('registerBtn');
    const attendanceBtn = document.getElementById('attendanceBtn');
    const nameInput = document.getElementById('nameInput');
    const statusText = document.getElementById('status');
    let pollingInterval;

    // Function to update the status message
    function updateStatus(message) {
        statusText.textContent = `Status: ${message}`;
    }

    // Register button click handler
    registerBtn.addEventListener('click', function() {
        const name = nameInput.value.trim();
        if (!name) {
            alert('Please enter a name for registration.');
            return;
        }

        updateStatus('Registering...');
        fetch(`/register?name=${name}`)
            .then(response => response.json())
            .then(data => {
                updateStatus(data.message);
                if (data.success) {
                    nameInput.value = ''; // Clear input on success
                }
            })
            .catch(error => {
                updateStatus('Registration failed. Server error.');
                console.error('Error:', error);
            });
    });

    // Attendance button click handler
    attendanceBtn.addEventListener('click', function() {
        updateStatus('Looking for a face...');
        attendanceBtn.disabled = true;

        fetch(`/start_attendance`)
            .then(response => response.json())
            .then(data => {
                updateStatus(data.message);
                
                // Start polling the server for status updates
                pollingInterval = setInterval(function() {
                    fetch('/get_status')
                        .then(response => response.json())
                        .then(statusData => {
                            if (statusData.success) {
                                updateStatus(statusData.message);
                                attendanceBtn.disabled = false;
                                clearInterval(pollingInterval);
                            }
                        })
                        .catch(error => {
                            console.error('Error polling status:', error);
                            clearInterval(pollingInterval);
                            attendanceBtn.disabled = false;
                        });
                }, 1000); // Poll every second
            })
            .catch(error => {
                updateStatus('Failed to start attendance mode.');
                console.error('Error:', error);
                attendanceBtn.disabled = false;
            });
    });
});