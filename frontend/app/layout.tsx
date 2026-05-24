import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "GeoSite Agent",
  description: "Real estate development analysis dashboard"
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
