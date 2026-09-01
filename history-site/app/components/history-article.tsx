import Link from "next/link";
import { addHeadingIds, articleHeadings, type HistoryPage } from "../data/history";
import { DataRestorationNotice, GlobalRateChart } from "./rate-charts";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(value));
}

export function HistoryArticle({ page }: { page: HistoryPage }) {
  const headings = articleHeadings(page.content);
  const html = addHeadingIds(page.content);
  const parts = html.split(/(\[CHART\d+\])/g);
  const isGlobal = page.slug.endsWith("key-global-policy-rates");

  return (
    <div className="article-page rates-theme">
      <div className="article-toolbar">
        <Link href="/history" className="back-link">
          <span aria-hidden="true">←</span> History
        </Link>
        <span>{page.category} · {page.subcategory}</span>
      </div>

      <header className="article-header">
        <p className="eyebrow">Rates research</p>
        <h1>{page.title}<i className="title-cursor" aria-hidden="true" /></h1>
        <p className="article-meta">Last editorial update: {formatDate(page.lastUpdate)}</p>
      </header>

      <nav className="mini-toc" aria-label="On this page">
        <span>On this page</span>
        {headings.map((heading) => (
          <a key={heading.id} href={`#${heading.id}`}>{heading.label}</a>
        ))}
      </nav>

      <article className="article-copy">
        {parts.map((part, index) => {
          const marker = part.match(/^\[CHART(\d+)\]$/);
          if (marker) {
            const chartIndex = Number(marker[1]);
            return isGlobal ? (
              <GlobalRateChart index={chartIndex} key={`chart-${chartIndex}`} />
            ) : (
              <DataRestorationNotice institution={page.subcategory} key={`chart-${chartIndex}`} />
            );
          }
          return <div key={`copy-${index}`} dangerouslySetInnerHTML={{ __html: part }} />;
        })}
      </article>
    </div>
  );
}
