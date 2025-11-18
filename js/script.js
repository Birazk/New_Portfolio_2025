// script.js
// Handles the modal pop-up and triggers the auto-slide for the certification grid.

document.addEventListener('DOMContentLoaded', () => {
  // --- MODAL AND AUTO-SLIDE SETUP ---
  const certGrid = document.getElementById('cert-grid');
  const modal = document.getElementById('image-modal');
  const modalImage = document.getElementById('modal-image');
  const modalTitle = document.getElementById('modal-title');
  const modalDesc = document.getElementById('modal-desc');
  const closeModalBtn = document.getElementById('close-modal');
  const carouselContainer = document.getElementById('carousel-container');

  // settings
  const AUTO_SLIDE_MS = 4000; // 0 to disable auto slide

  const allCards = Array.from(certGrid.querySelectorAll('.cert-card'));
  let autoInterval = null;

  // --- MODAL LOGIC (No changes needed here) ---

  // Function to open the modal
function openModalFromCard(card) {
  const src = card.getAttribute('data-image') || '';
  if (!src) return;

  modalImage.src = src; // We ONLY need to set the image source

  modal.setAttribute('aria-hidden', 'false');
  modal.style.display = 'flex';
  closeModalBtn.focus();
}

  // Function to close the modal
  function closeModalFn() {
    modal.setAttribute('aria-hidden', 'true');
    modal.style.display = 'none';
    modalImage.src = '';
  }

  // Attach click and keyboard behavior to each card for the modal
  allCards.forEach(card => {
    card.addEventListener('click', () => openModalFromCard(card));
    card.setAttribute('tabindex', '0');
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openModalFromCard(card);
      }
    });
  });

  // Modal close handlers
  closeModalBtn.addEventListener('click', closeModalFn);
  window.addEventListener('click', (e) => {
    if (e.target === modal) closeModalFn();
  });
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.style.display === 'flex') closeModalFn();
  });




  // Pause auto-slide on hover
  if (carouselContainer) {
    carouselContainer.addEventListener('mouseenter', stopAutoSlide);
    carouselContainer.addEventListener('mouseleave', startAutoSlide);
  }

  // --- INITIALIZATION ---
  startAutoSlide();
});