document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-download]").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();  

            const url = this.href;

            const old = document.getElementById("hidden-download-frame");
            if (old) old.remove();

            const iframe = document.createElement("iframe");
            iframe.style.display = "none";
            iframe.id = "hidden-download-frame";
            iframe.src = url;

            document.body.appendChild(iframe);
        });
    });
});