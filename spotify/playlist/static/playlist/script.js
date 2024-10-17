document.addEventListener('DOMContentLoaded', function() {
    
    const wrapper = document.querySelector('.wrapper')
    const registerLink = document.querySelector('.register-link')
    const loginLink = document.querySelector('.login-link')
    // Check if the URL has the signup action
    const urlParams = new URLSearchParams(window.location.search);
    const action = urlParams.get('action');
    
    if (action === 'signup') {
        wrapper.classList.add('active')
    } else if (action === 'signin') {
        wrapper.classList.remove('active')
    }


    registerLink.onclick = (event) => {
        event.preventDefault();
        wrapper.classList.add('active')
        // Update URL without reloading the page
        history.pushState(null, '', '?action=signup')
    }

    loginLink.onclick = (event) => {
        event.preventDefault();
        wrapper.classList.remove('active')
        // Update URL without reloading the page
        history.pushState(null, '', '?action=signin')
    } 

    // Handle browser back/forward buttons
    window.addEventListener('popstate', () => {
        const newAction = new URLSearchParams(window.location.search).get('action');
        if (newAction === 'signup') {
            wrapper.classList.add('active')
        } else if (newAction === 'signin') {
            wrapper.classList.remove('active')
        }
    })
});

/*
document.addEventListener('DOMContentLoaded', function() {
    
    const wrapper = document.querySelector('.wrapper')
    const registerLink = document.querySelector('.register-link')
    const loginLink = document.querySelector('.login-link')
    // Check if the URL has the signup action 

    registerLink.addEventListener('click', function(event) {
        event.preventDefault();
        wrapper.classList.add('active')
    })
    loginLink.addEventListener('click', function(event) {
        event.preventDefault();
        wrapper.classList.remove('active')
    })
});
*/
