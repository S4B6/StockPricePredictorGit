import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { HistoryArticle } from "../../components/history-article";
import { SiteShell } from "../../components/site-shell";
import { getHistoryPage, historyPages } from "../../data/history";

type PageProps = { params: Promise<{ slug: string[] }> };

export function generateStaticParams() {
  return historyPages.map((page) => ({ slug: page.slug.split("/") }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const page = getHistoryPage(slug.join("/"));
  if (!page) return {};
  const description = `${page.title}: historical policy-rate context from Markets Since 1998.`;
  return {
    title: page.title,
    description,
    openGraph: { title: page.title, description, images: [] },
    twitter: { card: "summary", title: page.title, description, images: [] },
  };
}

export default async function HistoryDetail({ params }: PageProps) {
  const { slug } = await params;
  const page = getHistoryPage(slug.join("/"));
  if (!page) notFound();
  return (
    <SiteShell>
      <HistoryArticle page={page} />
    </SiteShell>
  );
}
