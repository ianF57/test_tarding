import type { Metadata } from "next";
import React from "react";

export const metadata: Metadata = {
  title: "Trading Research",
  description: "Strategy generation and recommendation dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
