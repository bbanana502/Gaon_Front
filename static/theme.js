// theme.js
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    
    // Load saved theme
    const savedTheme = localStorage.getItem('gaonTheme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }

    // Toggle click handler
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            
            // Save preference
            if (document.body.classList.contains('dark-mode')) {
                localStorage.setItem('gaonTheme', 'dark');
            } else {
                localStorage.setItem('gaonTheme', 'light');
            }
        });
    }
});
