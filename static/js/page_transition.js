document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("page-enter");

    // Finish enter animation
    requestAnimationFrame(() => {
        document.body.classList.add("page-loaded");
    });
});

window.navigateWithTransition = function (url) {
    document.body.classList.add("page-exit");

    setTimeout(() => {
        window.requestAnimationFrame(() => {
    window.scrollTo(0, window.scrollY); // freeze scroll
    window.location.href = url;
});
    }, 180); // ultra-fast
};