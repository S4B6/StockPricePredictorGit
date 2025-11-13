document.addEventListener("DOMContentLoaded", () => {
  const level1 = document.getElementById("level1");
  const subSection = document.getElementById("sub-section");
  const subWrapper = document.getElementById("sub-wrapper");
  const backBtn = document.getElementById("back-btn");
  const hero = document.querySelector(".history-hero");

  if (!level1 || !subSection || !subWrapper || !backBtn) {
    console.warn("History nav: some DOM elements are missing.");
    return;
  }

  const normalize = c => (c === "fx" ? "currencies" : c);

  const themeClass = {
    macro: "sub-theme-macro",
    equity: "sub-theme-equity",
    rates: "sub-theme-rates",
    currencies: "sub-theme-currencies",
    commodities: "sub-theme-commodities",
    "real-assets": "sub-theme-real-assets"
  };

// Example (to copuy-paste)



  const navTree = {

  /* ============================================================
     1. MACRO — THEMATIC ONLY (no regions)
  ============================================================ */
  macro: {
    _label: "Macro",
    children: [
      "Growth",
      "Inflation",
      "Labor Market",
      "Fiscal Policy",
      "Monetary Policy",
      "Credit Conditions",
      "Trade & Supply Chains",
      "Productivity",
      "Demographics",
      "Public Assets / Debt"
    ]
  },

  /* ============================================================
     2. EQUITIES — REGIONS / SECTORS / FACTORS
  ============================================================ */
  equity: {
    _label: "Equity",
    children: {
      "By Region": {
        children: {
          "World":            { children: [] },
          "Global":           { children: [] },
          "North America":    { children: [] },
          "Europe":           { children: [] },
          "Asia-Pacific":     { children: [] },
          "Latin America":    { children: [] },
          "Middle East & Africa": { children: [] }
        }
      },

      "By Sector": {
        children: [
          "Communication Services",
          "Consumer Discretionary",
          "Consumer Staples",
          "Energy",
          "Financials",
          "Health Care",
          "Industrials",
          "Information Technology",
          "Materials",
          "Real Estate",
          "Utilities"
        ]
      },

      "By Factor": {
        children: [
          "Value",
          "Growth",
          "Quality",
          "Momentum",
          "Low Volatility",
          "Size",
          "ESG"
        ]
      }
    }
  },

  /* ============================================================
     3. RATES — PURE RATE STRUCTURE
  ============================================================ */
  rates: {
    _label: "Rates",
    children: {
      "Policy Rates": {
        children: [
          "Federal Reserve",
          "ECB",
          "Bank of England",
          "Bank of Japan",
          "PBoC",
          "SNB",
          "Bank of Canada",
          "RBA",
          "RBNZ"
        ]
      },

      "Sovereign Yield Curves": {
        children: [
          "US",
          "Germany",
          "UK",
          "France",
          "Italy",
          "Japan",
          "China",
          "Australia"
        ]
      },

      "Swap Curves": {
        children: [
          "USD Swaps",
          "EUR Swaps",
          "GBP Swaps",
          "JPY Swaps"
        ]
      },

      "Forward Rates": {
        children: [
          "USD Forwards",
          "EUR Forwards",
          "GBP Forwards",
          "JPY Forwards"
        ]
      },

      "Corporate Rates": {
        children: [
          "Investment Grade",
          "High Yield",
          "Private Credit"
        ]
      }
    }
  },

  /* ============================================================
     4. CURRENCIES — FX COMPLETELY RESTRUCTURED
  ============================================================ */
  currencies: {
    _label: "Currencies",
    children: {
      "Major FX": {
        children: [
          "USD",
          "EUR",
          "JPY",
          "GBP",
          "CHF",
          "AUD",
          "CAD",
          "NZD"
        ]
      },
      "Emerging FX": {
        children: [
          "CNY",
          "INR",
          "BRL",
          "MXN",
          "ZAR",
          "TRY",
          "KRW",
          "IDR"
        ]
      },
      "Crypto Assets": {
        children: [
          "Bitcoin",
          "Ethereum",
          "Stablecoins",
          "Altcoins"
        ]
      }
    }
  },

  /* ============================================================
     5. COMMODITIES — PRO MARKET GROUPINGS
  ============================================================ */
  commodities: {
    _label: "Commodities",
    children: {
      "Energy": {
        children: [
          "Oil",
          "Natural Gas",
          "Products (Diesel/Gasoline)",
          "Coal"
        ]
      },
      "Metals": {
        children: [
          "Gold",
          "Silver",
          "Copper",
          "Iron Ore",
          "Aluminum"
        ]
      },
      "Agriculture": {
        children: [
          "Grains",
          "Soy Complex",
          "Sugar",
          "Coffee",
          "Cocoa"
        ]
      },
      "Livestock": {
        children: [
          "Cattle",
          "Hogs"
        ]
      }
    }
  },

  /* ============================================================
     6. REAL ASSETS — SIMPLE, PROFESSIONAL
  ============================================================ */
  "real-assets": {
    _label: "Real Assets",
    children: {
      "Real Estate": {
        children: []
      },
      "Infrastructure": {
        children: []
      }
    }
  }

};


  // path = [rootKey, level2Label, level3Label, ...]
  const path = [];

  // Get node at specific depth in the path:
  // depth 0 -> root level (macro/equity/...)
  // depth 1 -> its child, depth 2 -> grandchild, etc.
// depth 0 -> root node (macro/equity/...)
// depth 1 -> its child (e.g. "By Factor")
// depth 2 -> its grandchild, etc.
const getNodeAtDepth = depth => {
  // If depth is deeper than the current path, nothing to show
  if (depth >= path.length) return null;

  let node = navTree[path[0]];
  if (!node) return null;
  if (depth === 0) return node;

  for (let i = 1; i <= depth; i++) {
    if (!node.children) return null;

    if (Array.isArray(node.children)) {
      // array of leafs -> no deeper navigation
      return null;
    }

    const key = path[i];
    node = node.children[key];
    if (!node) return null;
  }

  return node;
};

  const renderLevel = () => {
    if (!path.length) return;

    // Apply theme on sub-section
    subSection.classList.remove("hidden");
    subSection.classList.add("visible");
    Object.values(themeClass).forEach(cls => subSection.classList.remove(cls));
    const rootKey = path[0];
    if (themeClass[rootKey]) subSection.classList.add(themeClass[rootKey]);

    // Reset wrapper and create 3 columns
    subWrapper.innerHTML = "";
    const columns = [];
    for (let i = 0; i < 3; i++) {
      const colDiv = document.createElement("div");
      colDiv.classList.add("sub-col");
      subWrapper.appendChild(colDiv);
      columns.push(colDiv);
    }

    // For each depth (0 = L2 column, 1 = L3 column, 2 = L4 column)
    for (let depth = 0; depth < 3; depth++) {
      const node = getNodeAtDepth(depth);
      if (!node || !node.children) continue;

      let children;
      if (Array.isArray(node.children)) {
        children = node.children;
      } else {
        children = Object.keys(node.children);
      }

      if (!children.length) continue;

      const colDiv = columns[depth];

      // Active label at this depth (the branch we are currently in)
      // For column depth = 0, active child label is path[1]
      // For depth = 1, active child is path[2], etc.
      const activeLabel = path[depth + 1];

      children.forEach(label => {
        let nextNode = null;
        if (!Array.isArray(node.children) && node.children) {
          nextNode = node.children[label];
        }

        const hasNext =
          nextNode &&
          nextNode.children &&
          (
            (Array.isArray(nextNode.children) && nextNode.children.length > 0) ||
            (!Array.isArray(nextNode.children) && Object.keys(nextNode.children).length > 0)
          );

        const box = document.createElement("div");
        box.classList.add("sub-box");
        if (hasNext) {
          box.classList.add("nav");
        } else {
          box.classList.add("leaf");
        }
        box.textContent = label;

        // Dim siblings, keep active one bright
        if (activeLabel) {
          if (label === activeLabel) {
            box.classList.add("active-sub");
          } else {
            box.classList.add("dimmed");
          }
        }

        box.addEventListener("click", () => {
          // We are clicking inside the column that corresponds to "depth"
          // So the parent path is path.slice(0, depth + 1)
          const basePath = path.slice(0, depth + 1);

          if (hasNext) {
            // Go deeper or change branch at this level
            path.length = basePath.length; // cut deeper levels
            path.push(label);
            renderLevel();
          } else {
            // Leaf -> go to page
            const slug = [...basePath, label]
              .map(x => x.toLowerCase().replace(/\s+/g, "-"))
              .join("/");
            window.location.href = `/history/${slug}/`;
          }
        });

        colDiv.appendChild(box);
      });
    }
  };

  const openRoot = root => {
    path.length = 0;
    path.push(root);

    if (hero) hero.classList.add("transparent");

    subSection.classList.remove("hidden");
    subSection.classList.add("visible");

    level1.querySelectorAll(".category-card").forEach(c => {
      const match = normalize(c.dataset.category) === root;
      c.classList.toggle("dimmed", !match);
      c.classList.toggle("active", match);
    });

    renderLevel();
  };

  const goBack = () => {
    if (path.length > 1) {
      path.pop();
      renderLevel();
      return;
    }

    // Back to initial state
    path.length = 0;

    if (hero) hero.classList.remove("transparent");
    level1.querySelectorAll(".category-card").forEach(c =>
      c.classList.remove("dimmed", "active")
    );
    subSection.classList.remove("visible");
    subSection.classList.add("hidden");
    subWrapper.innerHTML = "";
  };

  // Bind events
  level1.querySelectorAll(".category-card").forEach(card =>
    card.addEventListener("click", () => openRoot(normalize(card.dataset.category)))
  );
  backBtn.addEventListener("click", goBack);
});
