"use client";

import { useInView } from "@/lib/motion";
import { Reveal } from "@/components/motion/Reveal";

/** The workflow the console actually runs, in order. */
const STAGES = [
  {
    num: "01",
    name: "Evidence intake",
    desc: "Alert, case, escalation and disposition histories uploaded and validated record by record.",
  },
  {
    num: "02",
    name: "Gap analysis",
    desc: "Deterministic workers flag premature closures, missing escalations and execution gaps, each citing its records.",
  },
  {
    num: "03",
    name: "Risk and confidence",
    desc: "A decomposable risk score and evidence confidence, reported as separate dimensions.",
  },
  {
    num: "04",
    name: "Reviewer briefing",
    desc: "A generated briefing that states what is deterministic, what is model-assisted, and which findings it cites.",
  },
  {
    num: "05",
    name: "Human decision",
    desc: "A supervisor records accept, defer, escalate or close, with a reason bound to their identity.",
  },
  {
    num: "06",
    name: "TRUST-SAT",
    desc: "Finalization signs the run state and the decision with an ML-DSA-65 post-quantum signature; verification checks the record has not changed.",
  },
];

export function Pipeline() {
  const [ref, inView] = useInView<HTMLDivElement>(0.25);
  return (
    <section id="workflow" className="section" aria-labelledby="pipeline-h">
      <div className="section__inner">
        <div className="section__head">
          <div>
            <Reveal>
              <p className="label label--accent">How it works</p>
            </Reveal>
            <Reveal delayMs={80}>
              <h2 id="pipeline-h" className="section__title">
                From submitted evidence to a verified decision.
              </h2>
            </Reveal>
          </div>
          <Reveal delayMs={160}>
            <p className="label">Six steps, one recorded trail</p>
          </Reveal>
        </div>

        <div ref={ref} className={`pipeline ${inView ? "pipeline--in" : ""}`}>
          <div className="pipeline__track">
            <span className="pipeline__spine" aria-hidden="true" />
            {STAGES.map((s, i) => (
              <div
                key={s.num}
                className="pipeline__stage"
                style={{ ["--pd" as string]: `${200 + i * 130}ms` }}
              >
                <p className="pipeline__num">{s.num}</p>
                <p className="pipeline__name">{s.name}</p>
                <p className="pipeline__desc">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
