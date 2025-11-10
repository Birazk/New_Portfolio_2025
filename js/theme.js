/**
 * Theme Toggle Functionality
 * Handles dark/light mode switching with localStorage persistence
 * 
 * HOW IT WORKS:
 * 1. Checks localStorage for saved theme preference
 * 2. Applies theme on page load
 * 3. Toggles theme when button is clicked
 * 4. Saves preference to localStorage for persistence across pages
 * 5. CSS handles icon visibility automatically based on data-theme attribute
 */

// Get theme toggle button
const themeToggle = document.getElementById('themeToggle');

// Check for saved theme preference or default to 'light'
const currentTheme = localStorage.getItem('theme') || 'light';

// Apply saved theme on page load
document.documentElement.setAttribute('data-theme', currentTheme);
updateThemeLabel(currentTheme);

// Toggle theme when button is clicked
themeToggle.addEventListener('click', () => {
    // Get current theme
    const theme = document.documentElement.getAttribute('data-theme');
    
    // Switch theme
    const newTheme = theme === 'light' ? 'dark' : 'light';
    
    // Apply new theme
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Save to localStorage
    localStorage.setItem('theme', newTheme);
    
    // Update aria label
    updateThemeLabel(newTheme);
});

/**
 * Update theme button aria-label for accessibility
 * @param {string} theme - Current theme ('light' or 'dark')
 */
function updateThemeLabel(theme) {
    if (themeToggle) {
        if (theme === 'dark') {
            themeToggle.setAttribute('aria-label', 'Switch to light mode');
        } else {
            themeToggle.setAttribute('aria-label', 'Switch to dark mode');
        }
    }
}
