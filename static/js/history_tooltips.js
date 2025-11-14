document.addEventListener("DOMContentLoaded", () => {
    const tooltip = document.createElement("div");
    tooltip.className = "explain-tooltip";
    document.body.appendChild(tooltip);

    document.querySelectorAll(".explain").forEach(el => {
        el.addEventListener("mouseenter", () => {
            tooltip.innerHTML = el.dataset.explain;   // <=== HTML allowed
            tooltip.style.display = "block";
        });

        el.addEventListener("mousemove", (e) => {
            tooltip.style.left = (e.pageX + 12) + "px";
            tooltip.style.top = (e.pageY + 12) + "px";
        });

        el.addEventListener("mouseleave", () => {
            tooltip.style.display = "none";
        });
    });
});
