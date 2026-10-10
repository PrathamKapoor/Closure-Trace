"use client";

import { Reveal } from "@/components/motion/Reveal";

/**
 * Two complementary tracks over one submission: computed findings on one side,
 * the human decision on the other, converging on the signed record. SVG with
 * CSS-driven signal flow (offset-path); static under reduced motion.
 */
export function ReviewFlow() {
  return (
    <section id="review" className="section" aria-labelledby="dual-h">
      <div className="section__inner">
        <div className="section__head">
          <div>
            <Reveal>
              <p className="label label--accent">Analysis and review</p>
            </Reveal>
            <Reveal delayMs={80}>
              <h2 id="dual-h" className="section__title">
                Two tracks. One record.
              </h2>
            </Reveal>
          </div>
          <Reveal delayMs={160}>
            <p className="label">Fig. 01 · Computed and human tracks</p>
          </Reveal>
        </div>

        <Reveal delayMs={120}>
          <svg
            className="dual__figure"
            viewBox="0 0 1200 440"
            role="img"
            aria-label="Diagram: submitted evidence flows into computed findings and, separately, into a supervisor's decision; both are bound into one record that TRUST-SAT verifies."
          >
            <defs>
              <radialGradient id="nodeGlow">
                <stop offset="0%" stopColor="#7b5cff" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#7b5cff" stopOpacity="0" />
              </radialGradient>
              <radialGradient id="nodeGlowBlue">
                <stop offset="0%" stopColor="#4d9fff" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#4d9fff" stopOpacity="0" />
              </radialGradient>
            </defs>

            <path d="M 170 220 C 300 220, 340 110, 520 110" fill="none" stroke="rgba(123,92,255,0.4)" strokeWidth="1" />
            <path d="M 170 220 C 300 220, 340 330, 520 330" fill="none" stroke="rgba(77,159,255,0.4)" strokeWidth="1" />
            <path d="M 700 110 C 860 110, 890 220, 1010 220" fill="none" stroke="rgba(123,92,255,0.4)" strokeWidth="1" />
            <path d="M 700 330 C 860 330, 890 220, 1010 220" fill="none" stroke="rgba(77,159,255,0.4)" strokeWidth="1" />

            <circle
              r="2.6"
              fill="#b7a6ff"
              className="dual__signal"
              style={{ offsetPath: "path('M 170 220 C 300 220, 340 110, 520 110')" }}
            />
            <circle
              r="2.6"
              fill="#8fc2ff"
              className="dual__signal dual__signal--b"
              style={{ offsetPath: "path('M 170 220 C 300 220, 340 330, 520 330')" }}
            />
            <circle
              r="2.2"
              fill="#b7a6ff"
              className="dual__signal dual__signal--c"
              style={{ offsetPath: "path('M 700 110 C 860 110, 890 220, 1010 220')" }}
            />
            <circle
              r="2.2"
              fill="#8fc2ff"
              className="dual__signal dual__signal--d"
              style={{ offsetPath: "path('M 700 330 C 860 330, 890 220, 1010 220')" }}
            />

            <g>
              <circle cx="120" cy="220" r="26" fill="url(#nodeGlow)" opacity="0.35" className="dual__pulse" />
              <circle cx="120" cy="220" r="4" fill="#f4f4f6" />
              <text x="120" y="262" textAnchor="middle" className="dual__svg-label">
                EVIDENCE
              </text>
            </g>
            <g>
              <circle cx="610" cy="110" r="34" fill="url(#nodeGlow)" opacity="0.4" className="dual__pulse dual__pulse--b" />
              <circle cx="610" cy="110" r="5" fill="#b7a6ff" />
              <text x="610" y="70" textAnchor="middle" className="dual__svg-label">
                COMPUTED FINDING
              </text>
              <text x="610" y="146" textAnchor="middle" className="dual__svg-sub">
                deterministic rules, cited records
              </text>
            </g>
            <g>
              <circle cx="610" cy="330" r="34" fill="url(#nodeGlowBlue)" opacity="0.4" className="dual__pulse dual__pulse--c" />
              <circle cx="610" cy="330" r="5" fill="#8fc2ff" />
              <text x="610" y="296" textAnchor="middle" className="dual__svg-label">
                HUMAN DECISION
              </text>
              <text x="610" y="368" textAnchor="middle" className="dual__svg-sub">
                supervisor, recorded reason
              </text>
            </g>
            <g>
              <circle cx="1060" cy="220" r="30" fill="url(#nodeGlow)" opacity="0.35" className="dual__pulse dual__pulse--d" />
              <circle cx="1060" cy="220" r="4.5" fill="#f4f4f6" />
              <text x="1060" y="262" textAnchor="middle" className="dual__svg-label">
                VERIFIED RECORD
              </text>
            </g>
          </svg>
        </Reveal>

        <div className="dual__legend">
          <Reveal className="dual__cell" delayMs={100}>
            <h3>
              <span className="label label--accent">Track 01</span> Computed findings
            </h3>
            <p>
              Deterministic workers read the submitted alerts, cases, escalations and dispositions
              and surface gaps such as a fast closure or a critical alert with no escalation. Each
              finding names its rule and the evidence records behind it, so the reasoning can be
              inspected rather than trusted.
            </p>
          </Reveal>
          <Reveal className="dual__cell" delayMs={200}>
            <h3>
              <span className="label label--accent">Track 02</span> Human decision
            </h3>
            <p>
              A supervisor reads the reviewer briefing, then records accept, defer, escalate or
              close with a reason bound to their identity. The recommendation never becomes the
              decision on its own: the recorded decision is a separate, non-overwriting object.
            </p>
          </Reveal>
        </div>
        <Reveal delayMs={240}>
          <p className="dual__note">
            TRUST-SAT binds the recorded review state and decision. It does not prove the evidence
            is true or the reviewer is correct.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
