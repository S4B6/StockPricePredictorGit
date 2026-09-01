import pageData from "./history-pages.json";

export type HistoryPage = {
  id: number;
  title: string;
  slug: string;
  assetClass: string;
  category: string;
  subcategory: string;
  lastUpdate: string;
  content: string;
};

export const historyPages = pageData as HistoryPage[];

export function getHistoryPage(slug: string) {
  return historyPages.find((page) => page.slug === slug);
}

export function articleHeadings(content: string) {
  return Array.from(content.matchAll(/<h2[^>]*>([\s\S]*?)<\/h2>/gi)).map(
    (match, index) => ({
      id: `section-${index + 1}`,
      label: match[1].replace(/<[^>]+>/g, "").trim(),
    }),
  );
}

export function addHeadingIds(content: string) {
  let index = 0;
  const withHeadings = content.replace(/<h2([^>]*)>/gi, (_match, attributes: string) => {
    index += 1;
    return `<h2${attributes} id="section-${index}">`;
  });

  return withHeadings.replace(
    /<span class="explain" data-explain="([^"]*)"/gi,
    (_match, explanation: string) => {
      const plainText = explanation
        .replace(/<br\s*\/?\s*>/gi, " — ")
        .replace(/<[^>]+>/g, "")
        .replace(/&quot;/g, "'");
      return `<span class="explain" data-explain="${explanation}" title="${plainText}"`;
    },
  );
}
