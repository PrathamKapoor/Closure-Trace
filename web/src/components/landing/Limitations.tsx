"use client";

import Link from "next/link";
import { Reveal } from "@/components/motion/Reveal";

const LIMITS = [
  {
    h: "Synthetic evidence, not field accuracy",
    p: "Detection is measured against declared synthetic ground truth and committed demo submissions. That is reproducible evidence about the implementation, not about how it would perform on real casework.",
  },
  {
    h: "Cryptography proves integrity, not truth",
    p: "TRUST-SAT's ML-DSA-65 signature shows the recorded state has not changed since finalization. It cannot show that the evidence was accurate or that the reviewer was right.",
  },
  {
    h: "Deterministic analysis, bounded scope",
    p: "The workers implement declared rules over the fields you submit. Anything the schema does not carry, the analysis cannot see, and every finding cites the records it used.",
  },
  {
    h: "Risk weights are a starting hypothesis",
    p: "The seven-dimension risk model is disclosed as a hypothesis pending expert calibration. Scores support prioritisation; they do not replace the reviewer's judgement.",
  },
];

export function Limitations() {
  return (
    <section id="limits" className="section" aria-labelledby="limits-h">
      <div className="section__inner">
        <Reveal>
          <p className="label label--accent">Honesty discipline</p>
        </Reveal>
        <Reveal delayMs={90}>
          <h2 id="limits-h" className="limits__statement" style={{ marginTop: 18 }}>
            NOT REAL-WORLD ACCURACY. <span className="neg">NOT A GUARANTEE OF TRUTH.</span> NOT A
            REPLACEMENT FOR HUMAN JUDGEMENT.
          </h2>
        </Reveal>
        <Reveal delayMs={160}>
          <p className="statement__big" style={{ marginTop: 26 }}>
            Closure-Trace is an <strong>evidence review system</strong>: deterministic analysis, a
            human decision, and a signature over the record.
          </p>
        </Reveal>

        <div className="limits__grid">
          {LIMITS.map((l, i) => (
            <Reveal key={l.h} className="limits__item" delayMs={i * 90}>
              <h3>{l.h}</h3>
              <p>{l.p}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

export function ClosingCta() {
  return (
    <section className="closing" aria-labelledby="closing-h">
      <div className="closing__inner">
        <Reveal>
          <p className="label label--accent">Run the review</p>
        </Reveal>
        <Reveal delayMs={90}>
          <h2 id="closing-h" className="closing__title">
            Read the evidence.
            <br />
            Record the decision.
          </h2>
        </Reveal>
        <Reveal delayMs={170}>
          <div className="closing__row">
            <Link href="/login" className="cta cta--primary">
              Open console <span className="cta__arrow" aria-hidden="true">-&gt;</span>
            </Link>
            <Link href="/methodology" className="cta cta--ghost">
              Read the methodology
            </Link>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
