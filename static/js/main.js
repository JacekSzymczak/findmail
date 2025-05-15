// Global error handling
function showError(message) {
    const banner = document.getElementById('error-banner');
    const messageSpan = document.getElementById('error-message');

    messageSpan.textContent = message;
    banner.classList.remove('d-none');

    // Auto-hide after 5 seconds
    setTimeout(() => {
        banner.classList.add('d-none');
    }, 5000);
}

// Close error banner
document.addEventListener('DOMContentLoaded', function () {
    const banner = document.getElementById('error-banner');
    const closeBtn = banner.querySelector('.btn-close');

    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            banner.classList.add('d-none');
        });
    }
}); 