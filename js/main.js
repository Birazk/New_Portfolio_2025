// =================================================================
// MAIN.JS - CONTAINS ALL GLOBAL AND PAGE-SPECIFIC SCRIPTS
// =================================================================

document.addEventListener('DOMContentLoaded', () => {

    // -------------------------------------------------------------
    // SCRIPT 1: ACTIVE NAVIGATION LINK HIGHLIGHTING
    // -------------------------------------------------------------
    const navLinks = document.querySelectorAll('.nav-menu a');
    const currentPageUrl = window.location.href;

    navLinks.forEach(link => {
        // If the link's href is part of the current page's URL, make it active
        if (currentPageUrl.includes(link.href)) {
            link.classList.add('active');
        }
    });

    // -------------------------------------------------------------
    // SCRIPT 2: BACK-TO-TOP BUTTON VISIBILITY
    // -------------------------------------------------------------
    const backToTopButton = document.querySelector('.back-to-top');

    if (backToTopButton) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) { // Show button after scrolling 300px
                backToTopButton.classList.add('visible');
            } else {
                backToTopButton.classList.remove('visible');
            }
        });
    }

    // -------------------------------------------------------------
    // SCRIPT 3: CERTIFICATIONS CAROUSEL (PAGINATION, MODAL, AUTO-SLIDE)
    // This entire block will only run if the certification grid exists on the page.
    // -------------------------------------------------------------
    const certGrid = document.getElementById('cert-grid');

    if (certGrid) {
        
        // --- 1. SETUP: GATHER ALL ELEMENTS ---
        const certCards = Array.from(certGrid.getElementsByClassName('cert-card'));
        const carouselContainer = document.getElementById('carousel-container');

        // Pagination Elements
        const paginationContainer = document.getElementById('pagination');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const pageInfo = document.getElementById('page-info');
        const paginationWrap = document.querySelector('.pagination-wrap');

        // Modal Elements
        const modal = document.getElementById('image-modal');
        const modalImage = document.getElementById('modal-image');
        const closeModalBtn = document.getElementById('close-modal');
        
        // --- 2. SETTINGS ---
        const ITEMS_PER_PAGE = 3;      // How many cards to show per page
        const AUTO_SLIDE_MS = 2000;    // Auto-slide delay. Set to 0 to disable.

        // --- 3. STATE VARIABLES ---
        let currentPage = 1;
        const totalPages = Math.ceil(certCards.length / ITEMS_PER_PAGE);
        let autoInterval = null;

        // --- 4. CORE FUNCTIONS ---

        // A. PAGINATION LOGIC
        function showPage(page) {
            currentPage = page;
            const startIndex = (page - 1) * ITEMS_PER_PAGE;
            const endIndex = startIndex + ITEMS_PER_PAGE;

            certGrid.style.opacity = 0;
            setTimeout(() => {
                certCards.forEach((card, index) => {
                    card.style.display = (index >= startIndex && index < endIndex) ? 'flex' : 'none';
                });
                updateControls();
                certGrid.style.opacity = 1;
            }, 150);
        }

        function updateControls() {
            if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
            if (prevBtn) prevBtn.disabled = currentPage === 1;
            if (nextBtn) nextBtn.disabled = currentPage === totalPages;
            updatePaginationDots();
        }

        function createPaginationDots() {
            if (!paginationContainer) return;
            paginationContainer.innerHTML = '';
            for (let i = 1; i <= totalPages; i++) {
                const button = document.createElement('button');
                button.setAttribute('data-page', i);
                button.setAttribute('aria-label', `Go to page ${i}`);
                button.addEventListener('click', () => {
                    showPage(i);
                    resetAutoSlide(); // Reset timer on manual click
                });
                paginationContainer.appendChild(button);
            }
        }

        function updatePaginationDots() {
            if (!paginationContainer) return;
            const dots = paginationContainer.getElementsByTagName('button');
            for (let dot of dots) {
                dot.classList.toggle('active', parseInt(dot.getAttribute('data-page')) === currentPage);
            }
        }

        // B. AUTO-SLIDE LOGIC
        function startAutoSlide() {
            if (AUTO_SLIDE_MS <= 0) return;
            stopAutoSlide(); // Prevent multiple intervals
            autoInterval = setInterval(() => {
                const nextPage = (currentPage >= totalPages) ? 1 : currentPage + 1;
                showPage(nextPage);
            }, AUTO_SLIDE_MS);
        }

        function stopAutoSlide() {
            clearInterval(autoInterval);
        }

        function resetAutoSlide() {
            stopAutoSlide();
            startAutoSlide();
        }

        // C. MODAL LOGIC
        function openModalFromCard(card) {
            const src = card.getAttribute('data-image');
            if (!src) return;

            modalImage.src = src;
            modal.classList.add('active');
            modal.setAttribute('aria-hidden', 'false');
        }

        function closeModal() {
            modal.classList.remove('active');
            modal.setAttribute('aria-hidden', 'true');
        }

        // --- 5. EVENT LISTENERS ---

        // Manual Pagination Clicks
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentPage > 1) showPage(currentPage - 1);
                resetAutoSlide(); // Reset timer
            });
        }
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (currentPage < totalPages) showPage(currentPage + 1);
                resetAutoSlide(); // Reset timer
            });
        }

        // Pause Auto-slide on Hover
        if (carouselContainer) {
            carouselContainer.addEventListener('mouseenter', stopAutoSlide);
            carouselContainer.addEventListener('mouseleave', startAutoSlide);
        }

        // Modal Listeners
        certCards.forEach(card => {
            card.addEventListener('click', () => openModalFromCard(card));
        });
        if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
        if (modal) modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) closeModal();
        });

        // --- 6. INITIALIZATION ---
        if (totalPages > 1) {
            if (paginationWrap) paginationWrap.style.display = 'flex';
            createPaginationDots();
            showPage(1);
            startAutoSlide(); // Start the automatic sliding
        } else {
            if (paginationWrap) paginationWrap.style.display = 'none';
            showPage(1); // Still need to show the only page
        }
    } // End of the "if (certGrid)" block

}); // End of the single DOMContentLoaded listener