document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".history-chart").forEach(container => {
        const chartId = container.dataset.chartId;

        fetch(`/history/chart/${chartId}/`)
            .then(res => res.text())
            .then(html => {
                // Insert HTML
                container.innerHTML = html;

                // Execute embedded Plotly scripts
                container.querySelectorAll("script").forEach(oldScript => {
                    const newScript = document.createElement("script");
                    newScript.textContent = oldScript.textContent;
                    document.body.appendChild(newScript);
                });
            })
            .catch(err => {
                container.innerHTML = "<div class='chart-error'>Failed to load chart</div>";
                console.error(err);
            });
    });
});
