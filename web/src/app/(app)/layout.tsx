import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

// next/font self-hosts these at build time: no runtime font CDN request.
const fontSans = Geist({ subsets: ["latin"], variable: "--font-geist-sans" });
const fontMono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono" });

export const metadata: Metadata = {
  title: { template: "%s · Closure-Trace", default: "Closure-Trace · Evidence to decision" },
  description:
    "Closure-Trace reviews submitted security alert and case histories for investigation gaps, premature closures and missed escalations, connects findings to evidence, supports human review, and verifies the integrity of the recorded decision (TRUST-SAT, ML-DSA-65).",
};

export const viewport: Viewport = { themeColor: "#ffffff", colorScheme: "light" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${fontSans.variable} ${fontMono.variable}`}>
      <body className="min-h-dvh">{children}</body>
    </html>
  );
}
