/**
 * Closure-Trace entry composition: the sculptural stage and its copy on the
 * left, the console-access panel on the right, and the handover between the
 * full-bleed presentation and the split layout.
 *
 * The sequence is decorative only: the headline and both calls to action are
 * in the document from the first paint, and the graphics layer failing (no
 * WebGL, blocked context, reduced motion) never delays or disables them.
 */
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Stage, StageAtmosphere } from "./Stage";
import { useReducedMotion } from "@/lib/motion";

const INTRO_KEY = "closure_trace_intro_played";
const HERO_APPEAR_MS = 2000;
const HANDOVER_MS = 4250;
const HANDOVER_INSTANT_MS = 260;

/** The console workflow, previewed in the access panel. */
const STEPS = [
  { num: "01", text: "Evidence intake and validation" },
  { num: "02", text: "Gap analysis, risk and reviewer briefing" },
  { num: "03", text: "Human decision, recorded with a reason" },
  { num: "04", text: "TRUST-SAT finalization and verification" },
];

export function Entry() {
  const reduced = useReducedMotion();
  const [live, setLive] = useState(false);
  const [heroVisible, setHeroVisible] = useState(false);
  const [split, setSplit] = useState(false);
  const [instant] = useState(() => {
    try {
      return sessionStorage.getItem(INTRO_KEY) === "1";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    const raf = requestAnimationFrame(() => setLive(true));
    const heroTimer = window.setTimeout(
      () => setHeroVisible(true),
      instant ? 0 : reduced ? 0 : HERO_APPEAR_MS
    );
    const handover = window.setTimeout(
      () => {
        setSplit(true);
        try {
          sessionStorage.setItem(INTRO_KEY, "1");
        } catch {
          /* private mode: the full sequence simply plays again */
        }
      },
      instant ? HANDOVER_INSTANT_MS : reduced ? 200 : HANDOVER_MS
    );
    return () => {
      cancelAnimationFrame(raf);
      window.clearTimeout(heroTimer);
      window.clearTimeout(handover);
    };
  }, [instant, reduced]);

  return (
    <div
      id="entry"
      className={`entry ${live ? "entry--live" : ""} ${heroVisible ? "entry--hero-live" : ""} ${
        split ? "entry--split" : ""
      }`}
    >
      <div className="entry__atmosphere" aria-hidden="true" />
      <StageAtmosphere className="entry__grain" />

      <div className="entry__main">
        <section className="hero-stage" aria-label="Closure-Trace">
          <Stage lettersLive={live} sculptureLive={heroVisible} decorated={live} instant={instant} />

          <div className="entry__copy">
            <p className="label label--accent">Security review integrity</p>
            <h1 className="entry__headline">Closed is a status. Reviewed is a process.</h1>
            <p className="entry__sub">
              Trace security alerts from evidence to human decision, and verify that the recorded
              review has not changed.
            </p>
            <div className="entry__ctas">
              <Link href="/login" className="cta cta--primary">
                Open console <span className="cta__arrow" aria-hidden="true">-&gt;</span>
              </Link>
              <a href="#workflow" className="cta cta--ghost">
                See the workflow
              </a>
            </div>
          </div>
        </section>

        <section className="auth-stage" aria-label="Console access">
          <div className="entry__panel-slot">
            <div className="entry__panel-inner">
              <p className="label label--accent">Closure-Trace / Access</p>
              <h2 className="entry__heading">Open the console.</h2>
              <p className="entry__sub">
                Evidence intake, findings, risk, human review and TRUST-SAT verification, behind
                one issued credential.
              </p>
              <ol className="entry__steps">
                {STEPS.map((s) => (
                  <li key={s.num}>
                    <span className="entry__step-num" aria-hidden="true">
                      {s.num}
                    </span>
                    {s.text}
                  </li>
                ))}
              </ol>
              <Link href="/login" className="cta cta--primary entry__submit">
                Open console <span className="cta__arrow" aria-hidden="true">-&gt;</span>
              </Link>
              <p className="entry__micro">
                Session held in an HttpOnly cookie. The credential is never stored.
              </p>
            </div>
          </div>

          <p className="auth-stage__foot label" aria-hidden="true">
            Deterministic analysis &middot; Human decision &middot; ML-DSA-65 signed
          </p>
        </section>
      </div>
    </div>
  );
}
