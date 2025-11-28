document.addEventListener("DOMContentLoaded", () => {
    const toc = document.getElementById("mini-toc");
    if (!toc) return;

    // Generate TOC
    const sections = document.querySelectorAll(".history-body h2");
    sections.forEach((section, index) => {
        if (!section.id) {
            section.id = "section-" + index;
        }

        const link = document.createElement("a");
        link.href = "#" + section.id;
        link.textContent = section.textContent.trim();
        toc.appendChild(link);
    });

    const tocLinks = toc.querySelectorAll("a");

    // Highlight logic
    function highlightSection() {
        let activeIndex = 0;
        const scrollPos = window.scrollY + 150; // offset so header doesn't hide

        sections.forEach((section, i) => {
            if (section.offsetTop <= scrollPos) {
                activeIndex = i;
            }
        });

        tocLinks.forEach((link) => link.classList.remove("active"));
        tocLinks[activeIndex].classList.add("active");
    }

    window.addEventListener("scroll", highlightSection);
    highlightSection();
});
