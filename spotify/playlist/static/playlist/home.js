src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"
src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"


document.addEventListener('DOMContentLoaded', (event) => {
    setTimeout(() => {
        document.querySelector('.main-content h1').classList.add('fade-in');
        document.querySelector('.main-content .btn-custom').classList.add('fade-in');
    }, 100);
});
