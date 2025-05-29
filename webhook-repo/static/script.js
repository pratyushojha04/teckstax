function fetchEvents() {
    fetch('/events')
        .then(response => response.json())
        .then(events => {
            const eventsDiv = document.getElementById('events');
            eventsDiv.innerHTML = ''; // Clear existing content
            events.forEach(event => {
                let message;
                if (event.action === 'PUSH') {
                    message = `${event.author} pushed to ${event.to_branch} on ${new Date(event.timestamp).toLocaleString()}`;
                } else if (event.action === 'PULL_REQUEST') {
                    message = `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${new Date(event.timestamp).toLocaleString()}`;
                } else if (event.action === 'MERGE') {
                    message = `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${new Date(event.timestamp).toLocaleString()}`;
                }
                const eventDiv = document.createElement('div');
                eventDiv.className = 'event';
                eventDiv.innerHTML = `<p>${message}</p>`;
                eventsDiv.appendChild(eventDiv);
            });
        })
        .catch(error => console.error('Error fetching events:', error));
}

// Poll every 15 seconds
setInterval(fetchEvents, 15000);

// Initial fetch
fetchEvents();