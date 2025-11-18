/**
 * Timeline Page Script
 * 
 * 1. Handles expand/collapse for timeline item details.
 * 2. Adds a fade-in animation for timeline items as they are scrolled into view.
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- PART 1: EXPAND/COLLAPSE BUTTON FUNCTIONALITY ---
    
    const expandButtons = document.querySelectorAll('.expand-btn');

    expandButtons.forEach(button => {
        button.addEventListener('click', function() {
            const details = this.nextElementSibling;

            if (details && details.classList.contains('timeline-details')) {
                details.classList.toggle('active');

                if (details.classList.contains('active')) {
                    this.textContent = 'Read Less';
                } else {
                    this.textContent = 'Read More';
                }
            }
        });
    });
    
    
    // --- PART 2: SCROLL-IN ANIMATION FOR TIMELINE ITEMS ---
    
    // Check if IntersectionObserver is supported by the browser
    if ('IntersectionObserver' in window) {
        const observerOptions = {
            threshold: 0.1, // Trigger when 10% of the item is visible
            rootMargin: '0px 0px -50px 0px' // Start animation a bit before it's fully in view
        };

        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                // When the item comes into view, add the 'in-view' class
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                    // Stop observing the item once it has animated in
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe all timeline items
        const items = document.querySelectorAll('.timeline-item');
        items.forEach(item => {
            observer.observe(item);
        });
    }
});

// Add this to a global JS file or an inline script tag at the bottom of your body
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-menu a');
    const currentPage = window.location.pathname.split('/').pop(); // Gets 'timeline.html', etc.

    navLinks.forEach(link => {
        const linkPage = link.getAttribute('href').split('/').pop();

        // If the link's href matches the current page, add the 'active' class
        if (linkPage === currentPage) {
            link.classList.add('active');
        }
    });
});