/**
 * Gallery Functionality (Corrected Version)
 * - Category filtering
 * - Lightbox view for images
 * - Keyboard navigation
 */

document.addEventListener('DOMContentLoaded', () => {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');
    const lightbox = document.getElementById('lightbox');
    const lightboxImageContainer = document.querySelector('.lightbox-image'); // Renamed for clarity
    const lightboxTitle = document.querySelector('.lightbox-caption h3');
    const lightboxDesc = document.querySelector('.lightbox-caption p');
    const closeBtn = document.querySelector('.lightbox-close');
    const prevBtn = document.querySelector('.lightbox-prev');
    const nextBtn = document.querySelector('.lightbox-next');
    
    let currentIndex = 0;
    let visibleItems = Array.from(galleryItems);
    
    // --- Filter functionality (This part is correct and unchanged) ---
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const filter = button.getAttribute('data-filter');
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            visibleItems = [];
            galleryItems.forEach(item => {
                const category = item.getAttribute('data-category');
                const isVisible = filter === 'all' || category === filter;
                item.style.display = isVisible ? 'block' : 'none'; // Use display instead of a class for simplicity
                if (isVisible) {
                    visibleItems.push(item);
                }
            });
        });
    });
    
    // --- Open lightbox when clicking a gallery item ---
    galleryItems.forEach(item => {
        item.addEventListener('click', () => {
            // Find the index of the clicked item within the *currently visible* items
            currentIndex = visibleItems.indexOf(item);
            if (currentIndex !== -1) {
                openLightbox();
            }
        });
    });
    
    // --- Close lightbox events ---
    closeBtn.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });
    
    // --- Navigation button events ---
    prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        showPrevImage();
    });
    
    nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        showNextImage();
    });
    
    // --- Keyboard navigation ---
    document.addEventListener('keydown', (e) => {
        if (!lightbox.classList.contains('active')) return;
        
        if (e.key === 'Escape') closeLightbox();
        else if (e.key === 'ArrowLeft') showPrevImage();
        else if (e.key === 'ArrowRight') showNextImage();
    });
    
    /**
     * ==========================================================
     * THE CORRECTED FUNCTION TO OPEN THE LIGHTBOX
     * ==========================================================
     */
    function openLightbox() {
        const item = visibleItems[currentIndex];
        
        // CHANGE 1: Find the actual <img> tag inside the clicked item
        const imageElement = item.querySelector('.gallery-image img');
        
        // CHANGE 2: Get the text content from the overlay
        const title = item.querySelector('.gallery-overlay h3').textContent;
        const desc = item.querySelector('.gallery-overlay p').textContent;
        
        // CHANGE 3: Create a new image element for the lightbox to display the full picture
        const newImage = document.createElement('img');
        newImage.src = imageElement.src; // Use the same source as the thumbnail
        newImage.alt = imageElement.alt; // Copy the alt text
        
        // Populate the lightbox
        lightboxImageContainer.innerHTML = ''; // Clear previous image
        lightboxImageContainer.appendChild(newImage); // Add the new full-size image
        lightboxTitle.textContent = title;
        lightboxDesc.textContent = desc;
        
        // Show the lightbox
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
    
    /**
     * Close lightbox
     */
    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = 'auto'; // Re-enable scrolling
    }
    
    /**
     * Show previous image
     */
    function showPrevImage() {
        currentIndex = (currentIndex - 1 + visibleItems.length) % visibleItems.length;
        openLightbox();
    }
    
    /**
     * Show next image
     */
    function showNextImage() {
        currentIndex = (currentIndex + 1) % visibleItems.length;
        openLightbox();
    }
});