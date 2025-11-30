document.addEventListener('DOMContentLoaded', function () {
    // Sticky Navigation Elements
    const sections = document.querySelectorAll('section.main-section, .sub-section');
    const stickyNav = document.getElementById('sticky-nav');
    const firstSection = sections[0];
    const dropdownMenu = document.getElementById('dropdown-menu');
    const stickyNavHeight = stickyNav.offsetHeight;
    const hierarchyText = document.getElementById('hierarchy-text');
    const menuArrow = document.querySelector('.menu-arrow');
    let lastSeenSection = null;

    // Function to update the sticky nav with the current section
    function updateStickyNav(section) {
        let hierarchy = '';
        let mainSectionText = '';

        if (section.classList.contains('main-section')) {
            hierarchy = section.querySelector('h1').textContent;
            mainSectionText = hierarchy;
        } else if (section.classList.contains('sub-section')) {
            const mainSection = section.closest('.main-section');
            if (mainSection) {
                const mainSectionTitle = mainSection.querySelector('h1').textContent;
                const subSectionTitle = section.querySelector('h2')
                    ? section.querySelector('h2').textContent
                    : ''; // Fallback if no sub-section title
                hierarchy = `${mainSectionTitle} > ${subSectionTitle}`;
                mainSectionText = mainSectionTitle;
            }
        }

        hierarchyText.textContent = hierarchy;
        stickyNav.style.display = 'flex';

        // Highlight the main section in the dropdown menu
        highlightCurrentHierarchy(mainSectionText);
    }

    // Function to highlight the current main section in the dropdown menu
    function highlightCurrentHierarchy(sectionText) {
        const links = dropdownMenu.querySelectorAll('a');
        links.forEach(link => {
            link.classList.remove('active-hierarchy');
            if (link.textContent.trim() === sectionText.trim()) {
                link.classList.add('active-hierarchy');
            }
        });
    }

    // Function to check the scroll position and update the sticky nav
    function checkScrollPosition() {
        let currentSection = null;

        // Hide sticky nav if above the first section
        if (firstSection.getBoundingClientRect().top > stickyNavHeight) {
            stickyNav.style.display = 'none';
            return;
        }

        // Loop through sections to find the one currently in view
        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            // Check if the section or sub-section is in view (partial or full)
            if (rect.top <= stickyNavHeight && rect.bottom > stickyNavHeight) {
                currentSection = section;
            }
        });

        // Update the sticky nav and dropdown highlight if a section is in view
        if (currentSection) {
            lastSeenSection = currentSection;
            updateStickyNav(currentSection);
        } else if (lastSeenSection) {
            // Keep displaying the last seen section when between sections
            updateStickyNav(lastSeenSection);
        }
    }

    // Run checkScrollPosition on scroll
    window.addEventListener('scroll', checkScrollPosition);

    // Initial check on page load
    checkScrollPosition();

    // Dropdown Menu Toggle
    dropdownMenu.style.display = 'none'; // Initially hide the dropdown

    menuArrow.addEventListener('click', function () {
        const isDropdownVisible = dropdownMenu.style.display === 'block';
        dropdownMenu.style.display = isDropdownVisible ? 'none' : 'block';
        menuArrow.classList.toggle('active', !isDropdownVisible); // Toggle arrow rotation
    });

    // Populate the dropdown with links to h1 sections only
    const mainSections = document.querySelectorAll('h1');
    mainSections.forEach(section => {
        const link = document.createElement('a');
        link.textContent = section.textContent || section.dataset.typed || 'Untitled';
        link.href = `#${section.parentElement.id}`;
        
        // Add event listener to close dropdown on link click
        link.addEventListener('click', function () {
            dropdownMenu.style.display = 'none';
            menuArrow.classList.remove('active'); // Reset the arrow
        });

        dropdownMenu.appendChild(link);
    });

    // Hide the dropdown menu when clicking outside of it
    document.addEventListener('click', function (e) {
        if (!dropdownMenu.contains(e.target) && !menuArrow.contains(e.target)) {
            dropdownMenu.style.display = 'none';
            menuArrow.classList.remove('active'); // Reset the arrow
        }
    });
});
