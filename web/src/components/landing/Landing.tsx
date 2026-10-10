"use client";

import { useEffect, useState } from "react";
import { Entry } from "@/components/entry/Entry";
import { SiteNav } from "./SiteNav";
import { SiteFooter } from "./SiteFooter";
import { Statement } from "./Statement";
import { Pipeline } from "./Pipeline";
import { ReviewFlow } from "./ReviewFlow";
import { Metrics } from "./Metrics";
import { ClosingCta, Limitations } from "./Limitations";


const INTRO_KEY = "closure_trace_intro_played";

export function Landing() {
  const [settled, setSettled] = useState(false);
  const [instant] = useState(() => {
    try {
      return sessionStorage.getItem(INTRO_KEY) === "1";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    const timer = setTimeout(() => setSettled(true), instant ? 200 : 980);
    return () => clearTimeout(timer);
  }, [instant]);

  return (
    <>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <SiteNav introSettled={settled} />
      <main id="main">
        <Entry />
        <Statement />
        <Pipeline />
        <ReviewFlow />
        <Metrics />
        <Limitations />
        <ClosingCta />
        <SiteFooter />
      </main>
    </>
  );
}
