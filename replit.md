# Biraj Kharel - Portfolio Website

## Overview
A professional, responsive portfolio website for Biraj Kharel - Mechanical Engineer specializing in electric vehicles, sustainable energy systems, and data analytics.

## Project Structure
```
/
├── index.html          # Home page with hero section and about
├── projects.html       # Project showcase with modal details
├── timeline.html       # Interactive career timeline
├── gallery.html        # Photo gallery with lightbox
├── blog.html          # Blog articles and posts
├── css/
│   └── styles.css     # Main stylesheet with theme variables
├── js/
│   ├── theme.js       # Dark/light mode toggle
│   ├── carousel.js    # Skills carousel functionality
│   ├── modal.js       # Project modal functionality
│   └── gallery.js     # Gallery lightbox functionality
├── images/            # Project photos, gallery images
└── assets/            # Icons, logos, tech stack icons
```

## Features
- **Dark/Light Mode**: Toggle with smooth transitions, persisted across pages
- **Responsive Design**: Mobile-first approach with breakpoints for tablet and desktop
- **Color Scheme**: Muted blues, grays, and warm accents for professional appearance
- **Interactive Elements**:
  - Tech stack carousel with animated skill cards
  - Project modals with detailed information
  - Timeline visualization with expandable milestones
  - Gallery with lightbox and category filtering

## Technologies Used
- HTML5
- CSS3 (Grid, Flexbox, Custom Properties)
- Vanilla JavaScript
- LocalStorage API for theme persistence

## Adding New Content

### Adding a New Project
Edit `projects.html` and add a new project card in the projects grid:
```html
<div class="project-card" data-project="your-project-id">
    <img src="images/your-project.jpg" alt="Project Name">
    <h3>Project Title</h3>
    <p>Brief description</p>
</div>
```

Then add the corresponding modal with details.

### Adding Timeline Entry
Edit `timeline.html` and add a new timeline item in chronological order.

### Adding Gallery Images
Place images in the `images/` folder and add them to `gallery.html` with appropriate category tags.

## User Preferences
- Minimalist and professional design
- Well-documented code for easy future modifications
- Modular structure with separate files for each page
- Smooth, muted color palette (no bright colors)

## Recent Changes
- [2025-11-10] Initial project setup and structure created
