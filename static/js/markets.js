// Function to initialize a Plotly chart
function initChart(elementId, chartData, chartTitle) {
    Plotly.newPlot(elementId, [{
        x: chartData.date,
        y: chartData.close,
        type: 'scatter',
        mode: 'lines',
        name: chartTitle
    }], {
        title: chartTitle,
        xaxis: { title: 'Date' },
        yaxis: { title: 'Close Price (USD)' },
        responsive: true
    });
}

// Run when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function() {
    const northAmericaChartElement = document.getElementById("north-america-chart");
    const easternEuropeChartElement = document.getElementById("eastern-europe-chart");

    // Retrieve and parse JSON data from data-chart-data attribute
    const northAmericaData = JSON.parse(northAmericaChartElement.dataset.chartData);
    const easternEuropeData = JSON.parse(easternEuropeChartElement.dataset.chartData);

    // Initialize the charts
    initChart("north-america-chart", northAmericaData, 'North America: S&P 500 Closing Prices');
    initChart("eastern-europe-chart", easternEuropeData, 'Eastern Europe: Nikkei 225 Closing Prices (Placeholder)');
});
