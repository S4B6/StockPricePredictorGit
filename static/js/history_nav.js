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

  const getNodeAtDepth = depth => {
    if (depth >= path.length) return null;

    let node = navTree[path[0]];
    if (!node) return null;
    if (depth === 0) return node;

    for (let i = 1; i <= depth; i++) {
      if (!node.children) return null;

      if (Array.isArray(node.children)) return null;

      const key = path[i];
      node = node.children[key];
      if (!node) return null;
    }
    return node;
  };

  const renderLevel = () => {
    if (!path.length) return;

    subSection.classList.remove("hidden");
    subSection.classList.add("visible");

    Object.values(themeClass).forEach(cls => subSection.classList.remove(cls));
    const rootKey = path[0];
    if (themeClass[rootKey]) subSection.classList.add(themeClass[rootKey]);

    subWrapper.innerHTML = "";
    const columns = [];
    for (let i = 0; i < 3; i++) {
      const colDiv = document.createElement("div");
      colDiv.classList.add("sub-col");
      subWrapper.appendChild(colDiv);
      columns.push(colDiv);
    }

    for (let depth = 0; depth < 3; depth++) {
      const node = getNodeAtDepth(depth);
      if (!node || !node.children) continue;

      let children = Array.isArray(node.children)
        ? node.children
        : Object.keys(node.children);

      if (!children.length) continue;

      const colDiv = columns[depth];
      const activeLabel = path[depth + 1];

      children.forEach(label => {
        let nextNode = null;
        if (!Array.isArray(node.children)) nextNode = node.children[label];

        const hasNext =
          nextNode &&
          nextNode.children &&
          (
            (Array.isArray(nextNode.children) && nextNode.children.length > 0) ||
            (!Array.isArray(nextNode.children) && Object.keys(nextNode.children).length > 0)
          );

        const box = document.createElement("div");
        box.classList.add("sub-box");
        box.textContent = label;

        if (hasNext) box.classList.add("nav");
        else box.classList.add("leaf");

        if (activeLabel) {
          if (label === activeLabel) box.classList.add("active-sub");
          else box.classList.add("dimmed");
        }

        box.addEventListener("click", () => {
          const basePath = path.slice(0, depth + 1);

          if (hasNext) {
            path.length = basePath.length;
            path.push(label);
            renderLevel();
          } else {
            const slug = [...basePath, label]
              .map(x => x.toLowerCase().replace(/\s+/g, "-"))
              .join("/");

            // **Only on leaf → transition**
            navigateWithTransition(`/history/${slug}/`);
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

    path.length = 0;

    if (hero) hero.classList.remove("transparent");
    level1.querySelectorAll(".category-card").forEach(c =>
      c.classList.remove("dimmed", "active")
    );
    subSection.classList.remove("visible");
    subSection.classList.add("hidden");
    subWrapper.innerHTML = "";
  };

  level1.querySelectorAll(".category-card").forEach(card =>
    card.addEventListener("click", () => openRoot(normalize(card.dataset.category)))
  );
  backBtn.addEventListener("click", goBack);
});