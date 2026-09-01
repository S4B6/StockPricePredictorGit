import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://markets-since-1998-history.buzzy-chub-1681.chatgpt.site"),
  title: {
    default: "Markets Since 1998 — History",
    template: "%s — Markets Since 1998",
  },
  description: "Historical market and macro research, beginning with policy rates.",
  openGraph: {
    title: "Markets Since 1998",
    description: "History, context, perspective.",
    type: "website",
    images: [
      {
        url: "/og.png",
        width: 1200,
        height: 630,
        alt: "Markets Since 1998 — History, context, perspective.",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Markets Since 1998",
    description: "History, context, perspective.",
    images: ["/og.png"],
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
