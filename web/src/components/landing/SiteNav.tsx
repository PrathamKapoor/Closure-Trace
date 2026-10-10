"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const LINKS = [
  { href: "#workflow", label: "Workflow" },
  { href: "#review", label: "Review" },
  { href: "#limits", label: "Limitations" },
  { href: "/methodology", label: "Methodology" },
];

interface Props {
  /** The intro has settled; the bar may appear. */
  introSettled?: boolean;
}

export function SiteNav({ introSettled = true }: Props) {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <>
      <header
        className={`nav ${scrolled ? "nav--scrolled" : ""} ${introSettled ? "" : "nav--hidden-intro"}`}
      >
        <Link href="/" className="nav__wordmark" aria-label="Closure-Trace home">
          <span>CLOSURE</span>
          <span className="nav__wordmark-dot" aria-hidden="true" />
          <span>TRACE</span>
        </Link>
        <nav className="nav__links" aria-label="Primary">
          {LINKS.map((l) => (
            <Link key={l.label} href={l.href} className="nav__link">
              {l.label}
            </Link>
          ))}
          <Link href="/login" className="nav__cta">
            Open console
          </Link>
        </nav>
        <button
          type="button"
          className="nav__burger"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-controls="nav-overlay"
        >
          {open ? "Close" : "Menu"}
        </button>
      </header>
      <div
        id="nav-overlay"
        className={`nav__overlay ${open ? "nav__overlay--open" : ""}`}
        aria-hidden={!open}
      >
        {LINKS.map((l) => (
          <Link key={l.label} href={l.href} onClick={() => setOpen(false)}>
            {l.label}
          </Link>
        ))}
        <Link href="/login" className="nav__overlay-cta" onClick={() => setOpen(false)}>
          Open console
        </Link>
      </div>
    </>
  );
}
