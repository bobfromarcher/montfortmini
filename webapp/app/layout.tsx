import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "montfortmini — The open creative workbench",
  description: "An open-source creative workbench for reference-guided object edits and motion transfer.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
