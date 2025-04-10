document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('popup-container');
    const button = document.getElementById('popup-btn');

    button.addEventListener('click', showRandomPopup);

    async function showRandomPopup() {
        try {
            const response = await fetch('/next-message'); // or full URL for local testing
            const data = await response.json();
            createPopup(data.message);
        } catch (error) {
            console.error('Failed to fetch message:', error);
        }
    }

    function createPopup(message) {
        const popup = document.createElement('div');
        popup.className = 'popup';
        popup.innerHTML = `
      <span class="close-btn">&times;</span>
      <p>${message}</p>
    `;

        container.appendChild(popup);

        // Trigger reflow then apply .show to enable transition in
        requestAnimationFrame(() => {
            popup.classList.add('show');
        });

        const timeoutId = setTimeout(() => {
            fadeOutAndRemove(popup);
        }, 15000);

        popup.querySelector('.close-btn').onclick = () => {
            clearTimeout(timeoutId);
            fadeOutAndRemove(popup);
        };
    }

    function fadeOutAndRemove(element) {
        element.classList.remove('show');
        element.classList.add('hide');
        setTimeout(() => {
            element.remove();
        }, 1100); // match transition time
    }

});
