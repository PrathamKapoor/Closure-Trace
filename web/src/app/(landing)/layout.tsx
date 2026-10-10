import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "@fontsource-variable/inter";
import "./landing.css";
import "./closure.css";

// The landing page has its own root layout and stylesheets: the entry
// composition (sculpture, wordmark, sections) is scoped to this route, so
// nothing here can restyle the workbench, sign-in controls or console tables.
// Navigating between the two is a full page load.
const fontSans = Geist({ subsets: ["latin"], variable: "--font-geist-sans" });
const fontMono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono" });

export const metadata: Metadata = {
  title: "Closure-Trace: evidence to decision, verified",
  description:
    "Closure-Trace reviews submitted security alert and case histories for investigation gaps, premature closures and missed escalations, connects findings to evidence, supports human review, and verifies the integrity of the recorded decision with TRUST-SAT (ML-DSA-65).",
};

export const viewport: Viewport = { themeColor: "#050507", colorScheme: "dark" };

export default function LandingLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${fontSans.variable} ${fontMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
