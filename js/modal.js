// ===================================
//  PROJECT MODAL SCRIPT (FINAL VERSION)
// ===================================

// We wrap everything in a DOMContentLoaded listener to make sure the HTML is fully
// loaded before this script tries to find elements on the page.
document.addEventListener('DOMContentLoaded', () => {

    // --- 1. GET HTML ELEMENTS ---
    // Get references to the modal elements we added to the HTML file.
    const modal = document.getElementById('projectModal');
    const modalBody = document.getElementById('modalBody');
    const closeBtn = modal.querySelector('.modal-close');
    const overlay = modal.querySelector('.modal-overlay');

    // Safety check in case the HTML is missing.
    if (!modal || !modalBody || !closeBtn || !overlay) {
        console.error("Modal elements not found! Make sure the modal HTML is in projects.html.");
        return;
    }
    
    // --- 2. PROJECT DATA ---
    // This data object is perfect as you wrote it. No changes needed.
    const projectsData = {
        'electric-bus': { title: 'Electric Bus Conversion', subtitle: 'System-Level Design & Implementation', abstract: 'Led the comprehensive conversion of a conventional diesel bus to a fully electric drivetrain system. This project involved system-level architecture design, component selection, integration planning, and performance validation.', overview: 'Working at ESTRL, I managed the end-to-end conversion process including battery pack design, motor selection, power electronics integration, and thermal management systems. The project required close collaboration with industry partners and adherence to safety standards.', result: 'Successfully converted and deployed an electric bus capable of 150km range on a single charge, reducing operational costs by 60% and eliminating local emissions. The bus is now in pilot operation serving rural routes.', tools: [{ icon: '📐', name: 'MATLAB' }, { icon: '⚙️', name: 'ANSYS' }, { icon: '🔧', name: 'Fusion 360' }, { icon: '📊', name: 'Excel' }], metrics: [{ value: '150km', label: 'Range per Charge' }, { value: '60%', label: 'Cost Reduction' }, { value: '0', label: 'Emissions' }], demoLink: '#' },
        'modular-vehicle': { title: 'Modular Vehicle for Rural Areas', subtitle: 'Adaptable Platform Design', abstract: 'Designed a modular vehicle platform specifically engineered for rural terrain and diverse use cases. The vehicle features interchangeable cargo/passenger modules and robust suspension for challenging road conditions.', overview: 'This project focused on creating an affordable, versatile transportation solution for rural communities. Key design criteria included ease of maintenance, component modularity, and adaptability to different load requirements.', result: 'Developed a working prototype with 3 interchangeable module configurations. The vehicle can transform between passenger transport (8 seats), cargo hauler (500kg capacity), and agricultural equipment carrier.', tools: [{ icon: '🔧', name: 'Fusion 360' }, { icon: '🎨', name: 'Blender' }, { icon: '📏', name: 'AutoCAD' }, { icon: '🐍', name: 'Python' }], metrics: [{ value: '3', label: 'Module Types' }, { value: '500kg', label: 'Max Payload' }, { value: '35%', label: 'Cost Savings' }], demoLink: '#' },
        'battery-thermal': { title: 'Battery Thermal Modeling', subtitle: 'CFD Analysis & Optimization', abstract: 'Developed comprehensive thermal models for lithium-ion battery packs used in electric vehicles. Used ANSYS for CFD analysis to optimize cooling strategies and prevent thermal runaway.', overview: 'Battery thermal management is critical for EV performance and safety. This project involved creating detailed 3D thermal models, simulating various cooling strategies (air, liquid, phase-change materials), and validating results against experimental data.', result: 'Achieved 25% improvement in thermal uniformity across the battery pack and reduced maximum operating temperature by 8°C. These improvements extended battery life by an estimated 15%.', tools: [{ icon: '⚙️', name: 'ANSYS' }, { icon: '📐', name: 'MATLAB' }, { icon: '🐍', name: 'Python' }, { icon: '📊', name: 'Excel' }], metrics: [{ value: '25%', label: 'Better Uniformity' }, { value: '8°C', label: 'Temp Reduction' }, { value: '15%', label: 'Life Extension' }], demoLink: '#' },
        'hybrid-optimization': { title: 'Hybrid Drivetrain Optimization', subtitle: 'Data-Driven Performance Enhancement', abstract: 'Implemented optimization algorithms for hybrid vehicle energy management using MATLAB/Simulink. Focused on maximizing fuel efficiency while maintaining performance targets.', overview: 'Collaborated with industry partners to develop control strategies that intelligently manage power split between engine and electric motor based on driving conditions, battery state, and efficiency maps.', result: 'Achieved 22% improvement in fuel economy in urban driving cycles and 18% in highway conditions. The optimization algorithm adapts to real-time traffic and terrain data.', tools: [{ icon: '📐', name: 'MATLAB' }, { icon: '🤖', name: 'Simulink' }, { icon: '🐍', name: 'Python' }, { icon: '📈', name: 'Power BI' }], metrics: [{ value: '22%', label: 'Urban Efficiency' }, { value: '18%', label: 'Highway Efficiency' }, { value: '95%', label: 'Control Accuracy' }], demoLink: '#' },
        'diagnostics-dashboard': { title: 'Vehicle Diagnostics Dashboard', subtitle: 'Real-Time Performance Monitoring', abstract: 'Built an interactive dashboard for real-time monitoring of electric vehicle performance metrics including battery health, energy consumption, motor efficiency, and predictive maintenance alerts.', overview: 'Using Power BI and Python, created a comprehensive visualization system that processes vehicle telemetry data and presents actionable insights to fleet operators and engineers.', result: 'Dashboard now monitors 15+ vehicles in real-time, enabling proactive maintenance that reduced downtime by 40% and improved overall fleet efficiency by 28%.', tools: [{ icon: '📈', name: 'Power BI' }, { icon: '🐍', name: 'Python' }, { icon: '📊', name: 'Excel' }, { icon: '🌿', name: 'Git' }], metrics: [{ value: '15+', label: 'Vehicles Monitored' }, { value: '40%', label: 'Reduced Downtime' }, { value: '28%', label: 'Fleet Efficiency' }], demoLink: '#' },
        'ice-ev-conversion': { title: 'ICE to EV Conversion', subtitle: 'Hands-On Electric Drivetrain Installation', abstract: 'Complete conversion of an internal combustion engine vehicle to electric drive during internship at ESTRL. Involved motor installation, battery integration, power electronics setup, and system testing.', overview: 'This hands-on project provided deep practical experience in EV systems. Removed ICE components, installed electric motor and reduction gearbox, integrated battery pack with BMS, and configured motor controller.', result: 'Successfully converted a passenger vehicle achieving 100km range, top speed of 80km/h, and 0-50km/h acceleration in 8 seconds. Vehicle is used as research platform for EV testing.', tools: [{ icon: '🔧', name: 'Hand Tools' }, { icon: '⚡', name: 'Electronics' }, { icon: '📐', name: 'MATLAB' }, { icon: '🔧', name: 'Fusion 360' }], metrics: [{ value: '100km', label: 'Range' }, { value: '80km/h', label: 'Top Speed' }, { value: '8s', label: '0-50 km/h' }], demoLink: '#' }
    };
    
    // --- 3. EVENT LISTENERS ---

    // Find ALL project cards and add a click listener to each one.
    document.querySelectorAll('.project-card-link').forEach(cardLink => {
        cardLink.addEventListener('click', (event) => {
            // Since our card is a link (<a>), we must PREVENT it from
            // trying to navigate to a new page.
            event.preventDefault(); 
            
            const projectId = cardLink.dataset.project;
            openModal(projectId);
        });
    });

    // Add listeners for closing the modal
    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', closeModal);
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });

    // --- 4. FUNCTIONS ---

    function openModal(projectId) {
        const project = projectsData[projectId];
        if (!project) {
            console.error(`Project data for "${projectId}" not found.`);
            return;
        }

        // Fill the modal body with the project's data
        modalBody.innerHTML = `
            <div class="modal-header">
                <h2 class="modal-title">${project.title}</h2>
                <p class="modal-subtitle">${project.subtitle}</p>
            </div>
            <div class="modal-section"><h3>📋 Abstract</h3><p>${project.abstract}</p></div>
            <div class="modal-section"><h3>🎯 Overview</h3><p>${project.overview}</p></div>
            <div class="modal-section">
                <h3>🛠 Tools Used</h3>
                <div class="tools-grid">
                    ${project.tools.map(tool => `
                        <div class="tool-item">
                            <div class="tool-icon">${tool.icon}</div>
                            <div class="tool-name">${tool.name}</div>
                        </div>`).join('')}
                </div>
            </div>
            <div class="modal-section">
                <h3>📊 Key Metrics & Outcomes</h3>
                <div class="metrics-grid">
                    ${project.metrics.map(metric => `
                        <div class="metric-card">
                            <div class="metric-value">${metric.value}</div>
                            <div class="metric-label">${metric.label}</div>
                        </div>`).join('')}
                </div>
            </div>
            <div class="modal-section">
                <h3>✅ Result</h3><p>${project.result}</p>
                ${project.demoLink && project.demoLink !== '#' ? `<a href="${project.demoLink}" class="btn-primary" target="_blank" rel="noopener noreferrer">View Demo</a>` : ''}
            </div>
        `;
        
        // Make the modal visible and prevent the page from scrolling
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Re-enable scrolling
    }
});