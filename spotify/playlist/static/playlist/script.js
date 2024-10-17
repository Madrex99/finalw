document.addEventListener('DOMContentLoaded', function() {
    
    const wrapper = document.querySelector('.wrapper')
    const registerLink = document.querySelector('.register-link')
    const loginLink = document.querySelector('.login-link')
    // Check if the URL has the signup action
    const urlParams = new URLSearchParams(window.location.search);
    const action = urlParams.get('action');
    
    if (action === 'signup') {
        wrapper.classList.add('active')
    }


    registerLink.onclick = () => {
        wrapper.classList.add('active')
        history.pushState(null, null, '/register')
    }

    loginLink.onclick = () => {
        wrapper.classList.remove('active')
        history.pushState(null, null, '/login')
    } 

    window.addEventListener('popstate', () => {
        if (window.location.pathname === '/register') {
            wrapper.classList.add('active')
            console.log('yes');
        } else if (window.location.pathname === '/login') {
            wrapper.classList.remove('active')
            console.log('no');
        }
    })
});
