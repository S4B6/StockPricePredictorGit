
//////////////////////////////////////// MAP

// Define the color range for performance, consistent with the legend
const colorRange = [
    "#700000",              // Very high negative performance (dark red)
    "rgb(255, 140, 140)",   // Mild negative performance (light red)
    "#9aff9a",              // Mild positive performance (light green)
    "#006400"               // Very high positive performance (dark green)
];

// Define the performance thresholds manually to separate negative and positive values explicitly
const performanceThresholds = [-1, 0, 1];  // Example thresholds for fixed color attribution

// Fetch country performance data from Django
fetch("/markets/countries-performance-data/")
    .then(response => response.json())
    .then(data => {
        const performanceData = {};

        data.forEach(item => {
            performanceData[item.country_code] = {
                performance: item.d_performance,
                security_name: item.security_name,
                price: item.index_most_recent_price,
                fetch_date: item.fetch_date
            };
        });

        // Log the entire performanceData object to verify the structure
        console.log("Performance Data:", performanceData);

        // Create a threshold scale based on fixed performance ranges
        const colorScale = d3.scaleThreshold()
            .domain(performanceThresholds)  // Fixed thresholds for color mapping
            .range(colorRange);              // Map to the color range

        // Load the GeoJSON data for the world map
        d3.json("/static/geojson/countries.geo.json").then(function(geoData) {
            const width = 750, height = 500;
            const svg = d3.select("#map-container").append("svg")
                          .attr("width", width)
                          .attr("height", height);

            const projection = d3.geoMercator()
                                 .scale(130)
                                 .translate([width / 2, height / 1.5]);

            const path = d3.geoPath().projection(projection);

            svg.selectAll("path")
                .data(geoData.features)
                .enter().append("path")
                .attr("d", path)
                .attr("fill", d => {
                    const countryCode = d.properties.iso_a3_eh || d.properties.iso_a3_eh;  // Use iso_a3 as fallback
                    const data = performanceData[countryCode];

                    return data && data.performance !== null ? colorScale(data.performance) : 'rgba(180,180,180)';  
                })
                .attr("stroke", "#333")
                .attr("stroke-width", 0.5)
                .on("mouseover", function(event, d) {
                    const countryCode = d.properties.iso_a3_eh || d.properties.iso_a3_eh;
                    const data = performanceData[countryCode];
                    const countryName = d.properties.name;
                
                    if (data && data.performance !== undefined) {
                        const performance = data.performance > 0 ? `+${data.performance.toFixed(2)}` : data.performance.toFixed(2);
                        const price = data.price ? data.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "N/A"; // Format price with thousands separator and 2 decimal places
                        const securityName = data.security_name || "Unknown";
                        const fetchDate = new Date(data.fetch_date);
                        const fetchDateFormatted = fetchDate.toLocaleDateString("en-GB", {
                            weekday: "short",
                            day: "numeric",
                            month: "short",
                            hour: "2-digit",
                            minute: "2-digit"
                        }).replace(",", ""); // Remove the comma after the weekday
                
                        // Choose the appropriate arrow and color
                        const arrow = data.performance > 0 ? "↗" : " ↘";
                        const arrowColor = data.performance > 0 ? "rgba(0, 255, 0);" : "red";
                
                        d3.select("#tooltip")
                            .style("visibility", "visible")
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 10) + "px")
                            .html(`
                                 <span style="color: ${arrowColor}">${arrow}</span> <strong>${countryCode}</strong><br>
                                <span style="color: ${arrowColor}">${securityName}; ${price}; ${performance}%</span><br>
                                <span style="color: rgb(160, 160, 160); font-size: 12px;">As of ${fetchDateFormatted} (CET)</span>
                            `);
                    }
                })
                .on("mousemove", function(event) {
                    d3.select("#tooltip")
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");
                })
                .on("mouseout", function() {
                    d3.select("#tooltip").style("visibility", "hidden");
                });
                
        });
    })
    .catch(error => console.error("Error fetching performance data:", error));

//////////////////////////////////////// LEGEND

    function createNALegend() {
        const legendContainer = d3.select("#legend-container")
            .append("svg")
            .attr("width", 200)  // Increase width to fit more boxes
            .attr("height", 140); // Increase height to fit labels
    
        // Colors and labels for each range
        const colorData = [
            { color: "#006400", label: "> +1%" },
            { color: "#9aff9a", label: "0 to +1%" },
            { color: "rgb(255, 140, 140)", label: "-1 to 0%" },
            { color: "#700000", label: "< -1%" },
            { color: "#cccccc", label: "n/a" }
        ];
    
        // Create a legend entry for each color
        colorData.forEach((item, index) => {
            legendContainer.append("rect")
                .attr("x", 10)
                .attr("y", 10 + index * 25)  // Adjust y position for each box
                .attr("width", 20)
                .attr("height", 20)
                .attr("fill", item.color)
                .attr("stroke", "#333")
                .attr("stroke-width", 0.5);
    
            legendContainer.append("text")
                .attr("x", 40)
                .attr("y", 25 + index * 25)  // Align text with each box
                .attr("font-size", "14px")
                .attr("fill", "white")
                .text(item.label);
        });
    }
    
    // Call this function to display the updated legend
    createNALegend();

    
//////////////////////////////////// Perf chart

// Sample data
const data1 = [
    { name: "Index A", value: 1.8 },
    { name: "Index B", value: 1.2 },
    { name: "Index C", value: -0.3 },
    { name: "Index D", value: -0.7 },
    { name: "Index E", value: -1.1 },
    { name: "Index F", value: -1.8 }
];

const data2 = [
    { name: "Custom A", value: 1.6 },
    { name: "Custom B", value: 1.3 },
    { name: "Custom C", value: 1.1 },
    { name: "Custom D", value: -0.5 },
    { name: "Custom E", value: -1.3 },
    { name: "Custom F", value: -1.9 }
];

// Function to get color based on value
function getColorForValue(value) {
    if (value < performanceThresholds[0]) {
        return colorRange[0]; // Very high negative performance
    } else if (value >= performanceThresholds[0] && value < performanceThresholds[1]) {
        return colorRange[1]; // Mild negative performance
    } else if (value >= performanceThresholds[1] && value < performanceThresholds[2]) {
        return colorRange[2]; // Mild positive performance
    } else {
        return colorRange[3]; // Very high positive performance
    }
}

function createChart(containerId, data, footerText, footerAlign) {
    const container = document.getElementById(containerId);

    // Create the chart content
    data.forEach(item => {
        const barContainer = document.createElement("div");
        barContainer.className = "bar-container";

        // Add label (index name) above the bar
        const label = document.createElement("span");
        label.className = "bar-label";
        label.innerText = item.name;

        // Add bar
        const bar = document.createElement("div");
        bar.className = "bar";
        bar.style.backgroundColor = getColorForValue(item.value); // Set color based on value
        bar.style.width = `${Math.min(Math.abs(item.value) * 40, 80)}%`;

        // Add percentage label below the bar
        const percentageLabel = document.createElement("span");
        percentageLabel.className = "percentage-label";
        percentageLabel.innerText = `${item.value.toFixed(1)}%`; // Display the percentage with one decimal

        // Set the color of the percentage label based on the value
        percentageLabel.style.color = item.value >= 0 ? "rgba(0, 255, 0)" : "red";

        barContainer.appendChild(percentageLabel); // Append the percentage label below the bar

        // Tooltip data
        const fetchDate = new Date(item.fetch_date || Date.now());
        const fetchDateFormatted = fetchDate.toLocaleDateString("en-GB", {
            weekday: "short",
            day: "numeric",
            month: "short",
            hour: "2-digit",
            minute: "2-digit"
        }).replace(",", "");

        // Add hover events for bar-tooltip
        bar.addEventListener("mouseover", function(event) {
            const tooltip = document.getElementById("bar-tooltip");
            tooltip.style.visibility = "visible";
            tooltip.style.left = (event.pageX + 10) + "px";
            tooltip.style.top = (event.pageY - 10) + "px";
            tooltip.innerHTML = `<span style="color: rgb(160, 160, 160); font-size: 12px;">As of ${fetchDateFormatted} (CET)</span>`;
        });

        bar.addEventListener("mousemove", function(event) {
            const tooltip = document.getElementById("bar-tooltip");
            tooltip.style.left = (event.pageX + 10) + "px";
            tooltip.style.top = (event.pageY - 10) + "px";
        });

        bar.addEventListener("mouseout", function() {
            const tooltip = document.getElementById("bar-tooltip");
            tooltip.style.visibility = "hidden";
        });

        // Append elements to barContainer in the correct order
        barContainer.appendChild(label); // Index name above
        barContainer.appendChild(bar);

        container.appendChild(barContainer);
        barContainer.appendChild(percentageLabel); // Percentage label below the bar

    });
}

// Render both charts without titles, as the title is now shared
createChart("performance-chart1", data1);
createChart("performance-chart2", data2);