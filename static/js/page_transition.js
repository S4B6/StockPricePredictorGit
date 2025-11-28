// -------------------------------------------------------
// ABSOLUTE RESET — runs even before DOMContentLoaded
// -------------------------------------------------------
document.body.classList.remove("page-exit");


// -------------------------------------------------------
// Fix for browser back/forward cache (bfcache)
// -------------------------------------------------------
window.addEventListener("pageshow", (event) => {
    document.body.classList.remove("page-exit");
    document.body.classList.add("page-loaded");
});



document.addEventListener("DOMContentLoaded", () => {

    // 🔥 FIX for back navigation / cached pages
    document.body.classList.remove("page-exit");

    document.body.classList.add("page-loaded");

    document.querySelectorAll("a[href]").forEach(link => {
        const url = link.getAttribute("href");

        if (!url || url.startsWith("#") || url.startsWith("javascript:")) return;

        // ⛔ 1) IGNORE CSV DOWNLOAD BUTTONS
        if (link.hasAttribute("data-download") || link.classList.contains("chart-download-btn")) {
            return; 
        }

        // ⛔ 2) IGNORE links forced to open in new tab
        if (link.getAttribute("target") === "_blank") return;

        // ⛔ 3) Internal pages only
        try {
            const dest = new URL(url, window.location.origin);
            if (dest.origin !== window.location.origin) return;
        } catch {}

        // ✔ fade-out animation
        link.addEventListener("click", e => {
            e.preventDefault();
            document.body.classList.add("page-exit");

            setTimeout(() => {
                window.location.href = url;
            }, 180);
        });
    });
});
