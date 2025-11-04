/////////////////////////////////////// Dropdown Perf
function selectPeriod(period) {
    // Logic to handle the selected period
    console.log(`Selected period: ${period}`);
    // Here you can add your logic to update the map or perform other tasks
}

// Toggle dropdown visibility and adjust width for "10Y"
document.getElementById("performance-period").addEventListener("click", function () {
    const dropdown = document.getElementById("period-selection");
    dropdown.classList.toggle("show-dropdown"); // Toggle dropdown visibility
    this.classList.toggle("active"); // Highlight the dropdown trigger when active

    // Recalculate dropdown position dynamically
    positionDropdown();
});

// Adjust dropdown position dynamically
function positionDropdown() {
    const dropdown = document.getElementById("period-selection");
    const trigger = document.getElementById("performance-period");

    const rect = trigger.getBoundingClientRect(); // Get trigger position
    dropdown.style.top = `${rect.bottom + window.scrollY}px`; // Place below trigger
    dropdown.style.left = `${rect.left + window.scrollX}px`; // Align with trigger

    // Adjust dropdown width for "10Y"
    const selectedPeriod = trigger.textContent.trim();
    dropdown.style.minWidth = selectedPeriod === "10Y" ? "72px" : "57px"; // Adjust width
}

// Attach event listeners for dropdown links (1D, 1W, etc.)
document.querySelectorAll("#period-selection a").forEach(link => {
    link.addEventListener("click", function (event) {
        event.preventDefault(); // Prevent default link behavior
        const period = this.textContent.trim(); // Get the selected period

        // Update the dropdown trigger text
        const trigger = document.getElementById("performance-period");
        trigger.textContent = period; // Set the selected period as the trigger text

        selectPeriod(period); // Update selected period and map

        // Close the dropdown after selection
        const dropdown = document.getElementById("period-selection");
        dropdown.classList.remove("show-dropdown");
        trigger.classList.remove("active");
    });
});
// Close dropdown when clicking outside
window.addEventListener("click", function (event) {
    const dropdown = document.getElementById("period-selection");
    const trigger = document.getElementById("performance-period");

    if (!event.target.closest("#performance-period") && !event.target.closest("#period-selection")) {
        dropdown.classList.remove("show-dropdown"); // Hide dropdown
        trigger.classList.remove("active"); // Remove highlight
    }
});

// Adjust dropdown position on window resize or zoom
window.addEventListener("resize", function () {
    const dropdown = document.getElementById("period-selection");
    if (dropdown.classList.contains("show-dropdown")) {
        positionDropdown(); // Recalculate dropdown position
    }
});




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

// Selected period state
let selectedPeriod = "1D"; // Default period

// Function to update the map based on the selected period
function updateMap(period) {
    console.log(`Updating map for period: ${period}`); // Debug log

    // Fetch country performance data from Django
    fetch("/markets/countries-performance-data/")
        .then(response => response.json())
        .then(data => {
            const performanceData = {};

            // Process data for the selected period
            data.forEach(item => {
                performanceData[item.country_code] = {
                    performance: period === "1D" ? item.d_performance :
                                 period === "1W" ? item.w_performance :
                                 period === "1M" ? item.m_performance :
                                 period === "1Y" ? item.y_performance :
                                 period === "10Y" ? item.decade_performance : null,
                    security_name: item.security_name,
                    price: item.index_most_recent_price,
                    fetch_date: item.fetch_date
                };
            });

            // Debug log for processed data
            console.log("Processed Performance Data:", performanceData);

            // Create a threshold scale based on fixed performance ranges
            const colorScale = d3.scaleThreshold()
                .domain(performanceThresholds)  // Fixed thresholds for color mapping
                .range(colorRange);

            // Load the GeoJSON data for the world map
            d3.json("/static/geojson/countries.geo.json").then(function (geoData) {
                let svg = d3.select("#map-container svg");
                if (svg.empty()) {
                    svg = d3.select("#map-container")
                            .append("svg")
                            .attr("width", 750)
                            .attr("height", 500);
                }

                const projection = d3.geoMercator()
                                     .scale(130)
                                     .translate([750 / 2, 500 / 1.5]);
                const path = d3.geoPath().projection(projection);

                // Bind data to paths and update map
                const paths = svg.selectAll("path").data(geoData.features);

                paths.enter()
                     .append("path")
                     .merge(paths) // Handle both entering and updating paths
                     .attr("d", path)
                     .attr("fill", d => {
                         const countryCode = d.properties.iso_a3_eh || d.properties.iso_a3_eh || 'n/a';
                         const data = performanceData[countryCode];
                         return data && data.performance !== null
                             ? colorScale(data.performance)
                             : 'rgba(180,180,180)'; // Default grey for no data
                     })
                     .attr("stroke", "#333")
                     .attr("stroke-width", 0.5)
                     .on("mouseover", function (event, d) {
                         const countryCode = d.properties.iso_a3_eh || d.properties.iso_a3_eh || 'n/a';
                         const data = performanceData[countryCode];
                         const countryName = d.properties.name;

                         if (data && data.performance !== undefined) {
                             const performance = data.performance > 0 ? `+${data.performance.toFixed(2)}` : data.performance.toFixed(2);
                             const price = data.price ? data.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "N/A";
                             const securityName = data.security_name || "Unknown";
                             const fetchDate = new Date(data.fetch_date);
                             const fetchDateFormatted = fetchDate.toLocaleDateString("en-GB", {
                                 weekday: "short",
                                 day: "numeric",
                                 month: "short",
                                 hour: "2-digit",
                                 minute: "2-digit"
                             }).replace(",", "");

                             const arrow = data.performance > 0 ? "↗" : "↘";
                             const arrowColor = data.performance > 0 ? "rgba(0, 255, 0);" : "red";

                             d3.select("#tooltip")
                                 .style("visibility", "visible")
                                 .style("left", (event.pageX + 10) + "px")
                                 .style("top", (event.pageY - 10) + "px")
                                 .html(`
                                    <span style="color: ${arrowColor}">${arrow}</span> <strong>${countryName}</strong><br>
                                    <span style="color: ${arrowColor}">${securityName}; ${price}; ${performance}%</span><br>
                                    <span style="color: rgb(160, 160, 160); font-size: 12px;">As of ${fetchDateFormatted} (CET)</span>
                                 `);
                         }
                     })
                     .on("mousemove", function (event) {
                         d3.select("#tooltip")
                             .style("left", (event.pageX + 10) + "px")
                             .style("top", (event.pageY - 10) + "px");
                     })
                     .on("mouseout", function () {
                         d3.select("#tooltip").style("visibility", "hidden");
                     });

                paths.exit().remove(); // Remove unused paths
                updateMarketStatusLights(svg, projection);
            });
        })
        .catch(error => console.error("Error fetching performance data:", error));
}



// Initial map generation for default period
updateMap(selectedPeriod);

// Update the map when a new period is selected
function selectPeriod(period) {
    if (selectedPeriod !== period) {
        selectedPeriod = period; // Update selected period
        updateMap(period); // Update map with new period data
    }
}

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

// Function to create and render a chart
function createChart(containerId, data, isRegion = false) {
    const container = document.getElementById(containerId);
    container.innerHTML = ""; // Clear any existing content

    data.forEach(item => {
        const barContainer = document.createElement("div");
        barContainer.className = "bar-container";

        // Create a container for the arrow and label to ensure they are inline
        const arrowLabelContainer = document.createElement("div");
        arrowLabelContainer.style.display = "flex"; // Ensures arrow and label are side-by-side
        arrowLabelContainer.style.alignItems = "center"; // Aligns arrow and label on the same vertical level

        // Arrow element
        const arrow = document.createElement("span");
        arrow.innerText = item.value > 0 ? "▲" : "▼";
        arrow.style.color = item.value > 0 ? "rgba(0, 255, 0)" : "red";
        arrow.style.fontSize = "12px";
        arrow.style.marginRight = "6px"; // Adds extra space between arrow and label

        // Label element (index name)
        const label = document.createElement("span");
        label.innerText = item.name;
        label.style.fontSize = "12px";

        // Append arrow and label to the container
        arrowLabelContainer.appendChild(arrow);
        arrowLabelContainer.appendChild(label);

        // Bar element representing performance
        const bar = document.createElement("div");
        bar.className = "bar";
        bar.style.backgroundColor = getColorForValue(item.value);
        bar.style.width = `${Math.min(Math.abs(item.value) * 40, 80)}%`;

        const percentageLabel = document.createElement("span");
        percentageLabel.className = "percentage-label";
        percentageLabel.innerText = `${item.value > 0 ? "+" : ""}${item.value.toFixed(1)}%`;
        percentageLabel.style.color = item.value >= 0 ? "rgba(0, 255, 0)" : "red";

        // Tooltip data using the fetch_date from the item data
        const fetchDate = new Date(item.fetch_date);
        const fetchDateFormatted = fetchDate.toLocaleDateString("en-GB", {
            weekday: "short",
            day: "numeric",
            month: "short",
            hour: "2-digit",
            minute: "2-digit"
        }).replace(",", "");

        //Determine country code or list of countries for regions
        const countryInfo = isRegion
            ? typeof item.country_list === "string" && item.country_list.trim().length > 0
                ? item.country_list.split(",").join(", ")  // Split the string and join with ", "
                : "N/A" // Fallback for regions with no country list
            : item.country_code || "N/A"; // Fallback for countries with no country code

        // Add hover events for bar-tooltip
        bar.addEventListener("mouseover", function(event) {
            const tooltip = document.getElementById("bar-tooltip");
            tooltip.style.visibility = "visible";
            tooltip.style.left = (event.pageX + 10) + "px";
            tooltip.style.top = (event.pageY - 10) + "px";
            tooltip.innerHTML = `<strong style="color: white; font-weight: bold;">${countryInfo}</strong><br>
                                 <span style="color: rgb(160, 160, 160); font-size: 12px;">As of ${fetchDateFormatted} (CET)</span>`;
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

        // Append elements in the correct order
        barContainer.appendChild(arrowLabelContainer); // Arrow and label in one line
        barContainer.appendChild(bar);                  // Bar for performance
        barContainer.appendChild(percentageLabel);      // Percentage label below the bar
        container.appendChild(barContainer);
    });
}

// Function to process data to get top and bottom 3 performers
function processPerformanceData(data, isRegion = false) {
    // Filter for region data if needed
    if (isRegion) {
        data = data.filter(item => item.asset_class === "Equity Basket");
    }

    // Sort by d_performance to get top and bottom performers
    data.sort((a, b) => b.d_performance - a.d_performance);
    const top3 = data.slice(0, 3);
    const bottom3 = data.slice(-3);

    // Transform data to desired format
    return [...top3, ...bottom3].map(item => ({
        name: isRegion ? item.custom_region_name || "Unnamed Region" : item.security_name,
        value: item.d_performance,
        fetch_date: item.fetch_date,  // Include fetch_date for tooltip
        country_code: item.country_code,  // Include country code for countries
        country_list: item.country_list || [] // Include country list for regions
    }));
}

// Render charts for both countries and regions
async function renderCharts() {
    try {
        // Fetch data from the updated APIs
        const [countryData, regionData] = await Promise.all([
            fetch("/markets/countries-performance-data").then(res => res.json()),
            fetch("/markets/regions-performance-data").then(res => res.json())
        ]);

        // Process the data for the charts
        const processedCountryData = processPerformanceData(countryData);
        const processedRegionData = processPerformanceData(regionData, true);

        // Render the charts with the processed data
        createChart("performance-chart1", processedCountryData, false);  // For countries
        createChart("performance-chart2", processedRegionData, true);    // For regions
    } catch (error) {
        console.error("Error rendering charts:", error);
    }
}

// Call renderCharts to load data and render the charts
renderCharts();

async function updateMarketStatusLights(svg, projection) {
    try {
        const response = await fetch("/markets/market-status-data/");
        const statusData = await response.json();

        const marketStatus = {};
        statusData.forEach(item => {
            marketStatus[item.country] = item;
        });

        const countryCoords = {
            "US": [-98, 38],
            "Canada": [-106, 56],
            "Mexico": [-102, 23],
            "Brazil": [-51, -10],
            "France": [2, 46],
            "Germany": [10, 51],
            "United Kingdom": [-1, 54],
            "Saudi Arabia": [45, 24],
            "India": [78, 22],
            "China": [104, 35],
            "Japan": [138, 37],
            "South Korea": [127.5, 36],
            "Hong Kong": [114, 22],
            "Australia": [134, -25]
        };

        svg.selectAll(".market-light").remove();

        Object.entries(countryCoords).forEach(([country, coords]) => {
            const data = marketStatus[country];
            if (!data) return;

            const [x, y] = projection(coords);
            const color = data.is_open ? "#00FF00" : "#FF0000";

            svg.append("circle")
                .attr("class", "market-light")
                .attr("cx", x)
                .attr("cy", y)
                .attr("r", 5)
                .attr("fill", color)
                .attr("opacity", 0.9);
        });
    } catch (error) {
        console.error("Error loading market status:", error);
    }
}





