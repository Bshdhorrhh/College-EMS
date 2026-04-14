document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss flashes
    const flashes = document.querySelectorAll('.flash');
    setTimeout(() => {
        flashes.forEach(f => {
            f.style.transition = 'opacity 0.5s';
            f.style.opacity = '0';
            setTimeout(() => f.remove(), 500);
        });
    }, 4000);

    // Live search
    const searchInput = document.getElementById('searchEvents');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('.event-card').forEach(card => {
                const title = card.querySelector('h3').innerText.toLowerCase();
                const desc = card.querySelector('.desc').innerText.toLowerCase();
                if (title.includes(query) || desc.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});
