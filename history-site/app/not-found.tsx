import Link from "next/link";
import { SiteShell } from "./components/site-shell";

export default function NotFound() {
  return (
    <SiteShell>
      <section className="not-found">
        <p className="eyebrow">404 · Unpublished research</p>
        <h1>This page is not in the public archive yet.</h1>
        <p>The History collection currently begins with policy rates.</p>
        <Link href="/history">Return to History</Link>
      </section>
    </SiteShell>
  );
}
