"use client";

import Link from "next/link";
import { useState } from "react";
import type { HistoryPage } from "../data/history";

const categories = [
  { id: "macro", label: "Macro", color: "#ff009d" },
  { id: "equity", label: "Equity", color: "#00ff80" },
  { id: "rates", label: "Rates", color: "#ff8000" },
  { id: "commodities", label: "Commodities", color: "#fff800" },
  { id: "currencies", label: "Currencies", color: "#ff3434" },
  { id: "real-assets", label: "Real Assets", color: "#00fff7" },
] as const;

export function HistoryExplorer({ pages }: { pages: HistoryPage[] }) {
  const [selected, setSelected] = useState("rates");
  const published = pages.filter((page) => page.assetClass === selected);
  const selectedCategory = categories.find((category) => category.id === selected)!;

  return (
    <div className="history-landing">
      <section className="history-hero" aria-labelledby="history-title">
        <p className="eyebrow">Historical research atlas</p>
        <h1 id="history-title">
          Decades of data.<br />
          <span>Patterns that matter.</span>
          <i className="typing-cursor" aria-hidden="true" />
        </h1>
        <p className="hero-copy">
          Explore the forces that shaped markets, one asset class and one cycle at a time.
        </p>
      </section>

      <section className="category-grid" aria-label="History asset classes">
        {categories.map((category) => {
          const count = pages.filter((page) => page.assetClass === category.id).length;
          const isSelected = category.id === selected;
          return (
            <button
              key={category.id}
              type="button"
              className={`category-card ${isSelected ? "selected" : ""}`}
              style={{ "--category-color": category.color } as React.CSSProperties}
              onClick={() => setSelected(category.id)}
              aria-pressed={isSelected}
            >
              <span>{category.label}</span>
              <small>{count ? `${count} published` : "In preparation"}</small>
            </button>
          );
        })}
      </section>

      <section
        className="published-section"
        aria-live="polite"
        style={{ "--category-color": selectedCategory.color } as React.CSSProperties}
      >
        <div className="section-heading">
          <div>
            <p className="eyebrow">{selectedCategory.label}</p>
            <h2>{published.length ? "Published research" : "Next in the archive"}</h2>
          </div>
          <span className="status-pill">{published.length} live</span>
        </div>

        {published.length ? (
          <div className="article-grid">
            {published.map((page) => (
              <Link className="article-card" href={`/history/${page.slug}`} key={page.slug}>
                <span className="article-kicker">{page.category} · {page.subcategory}</span>
                <strong>{page.title}</strong>
                <span className="article-cta">Open research <b aria-hidden="true">→</b></span>
              </Link>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            This asset class is intentionally unpublished for now. The live archive currently begins with policy rates.
          </div>
        )}
      </section>
    </div>
  );
}
