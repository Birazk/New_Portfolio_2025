/**
 * Theme handling
 * The site uses the light theme. If a page has a #themeToggle button,
 * it lets the visitor switch to dark mode, and the choice is remembered.
 * Pages without the button simply stay in light mode (no errors).
 */
(function () {
    const themeToggle = document.getElementById('themeToggle');
    const savedTheme = themeToggle ? (localStorage.getItem('theme') || 'light') : 'light';

    document.documentElement.setAttribute('data-theme', savedTheme);

    if (!themeToggle) return;

    function updateThemeLabel(theme) {
        themeToggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }

    updateThemeLabel(savedTheme);

    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeLabel(next);
    });
})();
