document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.querySelector("nav, #navbar, .main-nav");  
    const sticky = document.querySelector(".sticky-article-nav");

    if (!navbar || !sticky) return;

    const height = navbar.offsetHeight;

    sticky.style.top = height + "px";
});
