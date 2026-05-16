import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Sperm Analysis",
  description: "Research dashboard for sperm detection, motility, morphology, and fertility decision support"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <main>{children}</main>
      </body>
    </html>
  );
}

