/**
 * Timeline Expand/Collapse Functionality
 * Allows users to expand timeline items to see more details
 * 
 * HOW TO ADD NEW TIMELINE ITEMS:
 * 1. Add timeline-item div in timeline.html
 * 2. Include expand-btn button
 * 3. Add timeline-details div with hidden content
 * 4. The script will automatically handle expand/collapse
 */

document.addEventListener('DOMContentLoaded', () => {
    const expandButtons = document.querySelectorAll('.expand-btn');
    
    expandButtons.forEach(button => {
        button.addEventListener('click', () => {
            const content = button.closest('.timeline-content');
            const details = content.querySelector('.timeline-details');
            
            // Toggle active class
            details.classList.toggle('active');
            
            // Update button text
            if (details.classList.contains('active')) {
                button.textContent = 'Show Less';
            } else {
                button.textContent = 'Read More';
            }
        });
    });
    
    // Optional: Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all timeline items
    document.querySelectorAll('.timeline-item').forEach(item => {
        observer.observe(item);
    });
});
