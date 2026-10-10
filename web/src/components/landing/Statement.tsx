"use client";

import { Reveal } from "@/components/motion/Reveal";

const LINES = [
  { text: "CLOSED IS NOT REVIEWED.", cls: "statement__line--accent", cue: null },
  { text: "FROM EVIDENCE", cls: "", cue: "01 · Submitted" },
  { text: "TO FINDINGS", cls: "", cue: "02 · Computed" },
  { text: "TO DECISION", cls: "", cue: "03 · Human" },
];

export function Statement() {
  return (
    <section className="statement" aria-label="Statement">
      <div className="statement__inner">
        {LINES.map((l, i) => (
          <Reveal key={l.text} delayMs={i * 90}>
            <div className={`statement__line ${l.cls}`}>
              <span>{l.text}</span>
              {l.cue && <span className="statement__cue">{l.cue}</span>}
            </div>
          </Reveal>
        ))}
        <Reveal delayMs={380}>
          <p className="statement__big">
            A closed alert can still hide an incomplete investigation.{" "}
            <strong>Closure-Trace makes the review trail visible</strong>: every finding cites the
            records behind it, every decision carries a recorded reason, and the final state is
            signed so a later change is detectable.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
