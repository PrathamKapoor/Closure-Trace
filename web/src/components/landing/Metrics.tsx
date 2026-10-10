"use client";

import { useCountUp, useInView } from "@/lib/motion";
import { Reveal } from "@/components/motion/Reveal";

interface MetricDef {
  value: number;
  decimals: number;
  suffix?: string;
  label: string;
  note: string;
}

/**
 * Verified figures only, each with its scope attached. Sources:
 * docs/CLAIMS.md (coverage, smoke, benchmark rows) and
 * reports/CONTROLLED_BENCHMARK_RESULTS.md.
 */
const METRICS: MetricDef[] = [
  {
    value: 92.5,
    decimals: 1,
    suffix: "%",
    label: "Line coverage",
    note: "satsa/ + evaluation/, measured",
  },
  {
    value: 5,
    decimals: 0,
    suffix: " / 5",
    label: "Expected finding families detected",
    note: "Controlled synthetic corpus",
  },
  {
    value: 2.56,
    decimals: 2,
    suffix: "×",
    label: "Recall lift at top 10%",
    note: "vs measured random baseline (simulated)",
  },
  {
    value: 20,
    decimals: 0,
    suffix: " / 20",
    label: "Deployment smoke checks",
    note: "HTTP topology, local run",
  },
];

function Metric({ m, active, delay }: { m: MetricDef; active: boolean; delay: number }) {
  const raw = useCountUp(m.value, active, 1500 + delay, m.decimals);
  const display = m.decimals === 0 ? Number(raw).toLocaleString("en-US") : raw;
  return (
    <div className="metric">
      <p className="metric__value num">
        {display}
        <span className="metric__suffix">{m.suffix}</span>
      </p>
      <p className="metric__label">{m.label}</p>
      <p className="metric__note">{m.note}</p>
    </div>
  );
}

export function Metrics() {
  const [ref, inView] = useInView<HTMLDivElement>(0.3);
  return (
    <section id="metrics" className="section" aria-labelledby="metrics-h">
      <div className="section__inner">
        <div className="section__head">
          <div>
            <Reveal>
              <p className="label label--accent">Verified results</p>
            </Reveal>
            <Reveal delayMs={80}>
              <h2 id="metrics-h" className="section__title">
                Numbers from the repository. Nothing invented.
              </h2>
            </Reveal>
          </div>
          <Reveal delayMs={160}>
            <p className="label">Each figure carries its scope</p>
          </Reveal>
        </div>

        <div ref={ref} className="metrics__grid">
          {METRICS.map((m, i) => (
            <Metric key={m.label} m={m} active={inView} delay={i * 120} />
          ))}
        </div>

        <div className="metrics__explain">
          <Reveal>
            <span className="label label--accent">What these are</span>
            <p>
              Engineering and controlled-corpus results: test and coverage measurements over the
              codebase, detection of declared finding families against a synthetic ground truth,
              and a deployment smoke run over the real HTTP topology. They show the system runs,
              verifies and detects as designed on declared inputs.
            </p>
          </Reveal>
          <Reveal delayMs={120}>
            <span className="label">What these are not</span>
            <p>
              They are not detection accuracy against real investigations. The controlled
              benchmark counts extra family emissions against precision (0.4167), and the
              prioritisation lift is measured against a random baseline on the same synthetic
              population, labelled simulated in the source. No real-world examiner dataset exists
              in this repository to measure against.
            </p>
          </Reveal>
        </div>
        <Reveal delayMs={160}>
          <p className="metrics__src label">
            Source: docs/CLAIMS.md · reports/CONTROLLED_BENCHMARK_RESULTS.md
          </p>
        </Reveal>
      </div>
    </section>
  );
}
