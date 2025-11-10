/**
 * Skills Carousel Functionality
 * Creates an interactive carousel for showcasing tech stack and skills
 * 
 * HOW IT WORKS:
 * 1. Detects screen size to determine number of visible cards
 * 2. Allows navigation through skills using prev/next buttons
 * 3. Automatically adjusts for responsive layouts
 * 
 * CUSTOMIZATION:
 * - Add more skill cards directly in the HTML
 * - Adjust animation speed in the CSS transition
 */

document.addEventListener('DOMContentLoaded', () => {
    const track = document.getElementById('skillsTrack');
    const prevBtn = document.querySelector('.carousel-btn.prev');
    const nextBtn = document.querySelector('.carousel-btn.next');
    
    if (!track) return; // Exit if carousel not on page
    
    const cards = track.querySelectorAll('.skill-card');
    let currentIndex = 0;
    let cardsPerView = getCardsPerView();
    
    // Show carousel buttons only if needed
    updateCarouselButtons();
    
    /**
     * Calculate number of cards to show based on screen width
     */
    function getCardsPerView() {
        const width = window.innerWidth;
        if (width < 480) return 1;
        if (width < 768) return 2;
        if (width < 1024) return 3;
        return 4;
    }
    
    /**
     * Update carousel position
     */
    function updateCarousel() {
        const maxIndex = Math.max(0, cards.length - cardsPerView);
        currentIndex = Math.min(currentIndex, maxIndex);
        
        // Calculate the offset based on card width and gap
        const cardWidth = cards[0].offsetWidth;
        const gap = 24; // var(--spacing-lg) is typically 2rem = 32px, but we'll get computed value
        const computedGap = parseInt(window.getComputedStyle(track).gap) || gap;
        const offset = currentIndex * (cardWidth + computedGap);
        
        // Apply transform to slide the carousel
        track.style.transform = `translateX(-${offset}px)`;
        
        updateCarouselButtons();
    }
    
    /**
     * Show/hide carousel buttons based on whether scrolling is needed
     */
    function updateCarouselButtons() {
        if (cards.length <= cardsPerView) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'flex';
            nextBtn.style.display = 'flex';
        }
    }
    
    /**
     * Navigate to previous set of cards
     */
    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });
    
    /**
     * Navigate to next set of cards
     */
    nextBtn.addEventListener('click', () => {
        const maxIndex = Math.max(0, cards.length - cardsPerView);
        if (currentIndex < maxIndex) {
            currentIndex++;
            updateCarousel();
        }
    });
    
    /**
     * Update carousel on window resize
     */
    window.addEventListener('resize', () => {
        cardsPerView = getCardsPerView();
        updateCarousel();
    });
});
