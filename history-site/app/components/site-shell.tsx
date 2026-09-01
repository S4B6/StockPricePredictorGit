import Link from "next/link";

export function SiteShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="site-shell">
      <header className="site-header">
        <div className="site-header-inner">
          <Link className="brand" href="/history" aria-label="Markets Since 1998 home">
            <span className="brand-mark" aria-hidden="true">M98</span>
            <span>Markets Since 1998</span>
          </Link>
          <nav aria-label="Primary navigation">
            <Link className="nav-link active" href="/history" aria-current="page">
              History
            </Link>
          </nav>
        </div>
      </header>

      <main className="site-main">{children}</main>

      <footer className="site-footer">
        <p>Markets Since 1998 · Historical market research</p>
        <p>Research and education only — not investment advice.</p>
      </footer>
    </div>
  );
}
