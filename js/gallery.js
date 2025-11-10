/**
 * Gallery Functionality
 * - Category filtering
 * - Lightbox view for images
 * - Keyboard navigation
 * 
 * HOW TO ADD NEW IMAGES:
 * 1. Add gallery-item div in gallery.html
 * 2. Set data-category attribute (projects, simulations, renders, workshop)
 * 3. Add title and description in gallery-overlay
 * 4. This script will automatically handle filtering and lightbox
 */

document.addEventListener('DOMContentLoaded', () => {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');
    const lightbox = document.getElementById('lightbox');
    const lightboxImage = document.querySelector('.lightbox-image');
    const lightboxTitle = document.querySelector('.lightbox-caption h3');
    const lightboxDesc = document.querySelector('.lightbox-caption p');
    const closeBtn = document.querySelector('.lightbox-close');
    const prevBtn = document.querySelector('.lightbox-prev');
    const nextBtn = document.querySelector('.lightbox-next');
    
    let currentIndex = 0;
    let visibleItems = Array.from(galleryItems);
    
    // Filter functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const filter = button.getAttribute('data-filter');
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Filter items
            visibleItems = [];
            galleryItems.forEach(item => {
                const category = item.getAttribute('data-category');
                
                if (filter === 'all' || category === filter) {
                    item.classList.remove('hidden');
                    visibleItems.push(item);
                } else {
                    item.classList.add('hidden');
                }
            });
        });
    });
    
    // Open lightbox when clicking gallery item
    galleryItems.forEach((item, index) => {
        item.addEventListener('click', () => {
            currentIndex = visibleItems.indexOf(item);
            if (currentIndex !== -1) {
                openLightbox();
            }
        });
    });
    
    // Close lightbox
    closeBtn.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });
    
    // Navigation buttons
    prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        showPrevImage();
    });
    
    nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        showNextImage();
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (!lightbox.classList.contains('active')) return;
        
        if (e.key === 'Escape') {
            closeLightbox();
        } else if (e.key === 'ArrowLeft') {
            showPrevImage();
        } else if (e.key === 'ArrowRight') {
            showNextImage();
        }
    });
    
    /**
     * Open lightbox and display current image
     */
    function openLightbox() {
        const item = visibleItems[currentIndex];
        const imagePlaceholder = item.querySelector('.image-placeholder').cloneNode(true);
        const title = item.querySelector('.gallery-overlay h3').textContent;
        const desc = item.querySelector('.gallery-overlay p').textContent;
        
        lightboxImage.innerHTML = '';
        lightboxImage.appendChild(imagePlaceholder);
        lightboxTitle.textContent = title;
        lightboxDesc.textContent = desc;
        
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * Close lightbox
     */
    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = 'auto';
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
