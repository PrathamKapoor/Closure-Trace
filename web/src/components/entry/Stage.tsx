/**
 * The sculptural stage: two wordmark planes around the WebGL sculpture, with
 * the vignette, technical rules and labels the composition is drawn on.
 *
 * Client-only: the engines and the grain renderer are loaded after mount so
 * nothing here touches window, document or WebGL while the server renders the
 * page, and a failed or blocked GPU degrades to the 2D fallback (or to the
 * plain background) without taking the copy or the CTAs with it.
 */
"use client";

import dynamic from "next/dynamic";
import type { ReactNode } from "react";
import { WordPlane } from "./Wordmark";
import "./stage.css";

const NeuralStage = dynamic(() => import("./NeuralStage"), { ssr: false, loading: () => null });
const Grainient = dynamic(() => import("../Grainient/Grainient").then((m) => ({ default: m.Grainient })), {
  ssr: false,
  loading: () => null,
});

/** Decorative field labels along the stage grid. */
const FIELD_LABELS = ["Evidence / submitted", "Findings / computed", "Decision / human"];

interface StageProps {
  /** Glyph assembly has started. */
  lettersLive: boolean;
  /** The sculpture may fade in. */
  sculptureLive: boolean;
  /** Rules and labels have settled in. */
  decorated?: boolean;
  instant?: boolean;
  dimmed?: boolean;
  /** Placement of the sculpture's visual mass inside the stage. */
  framing?: { x?: number; y?: number; scale?: number };
  className?: string;
  children?: ReactNode;
}

export function Stage({
  lettersLive,
  sculptureLive,
  decorated = false,
  instant = false,
  dimmed = false,
  framing,
  className,
  children,
}: StageProps) {
  return (
    <div
      className={[
        "hero-stage__scene",
        sculptureLive ? "hero-stage__scene--live" : "",
        decorated ? "hero-stage__scene--decorated" : "",
        className ?? "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="entry__depth">
        <WordPlane live={lettersLive} instant={instant} plane="back" dimmed={dimmed} />
        <NeuralStage className="entry__stage" emergeDelayMs={0} framing={framing} />
        <WordPlane live={lettersLive} instant={instant} plane="front" dimmed={dimmed} />
      </div>

      <div className="entry__vignette" aria-hidden="true" />

      <div className="entry__rules" aria-hidden="true">
        <span className="entry__rule entry__rule--gutter" />
        <span className="entry__rule entry__rule--split" />
      </div>
      <ul className="entry__labels" aria-hidden="true">
        {FIELD_LABELS.map((label, i) => (
          <li key={label} className={`entry__label entry__label--${i + 1}`}>
            {label}
          </li>
        ))}
      </ul>

      {children}
    </div>
  );
}

interface AtmosphereProps {
  className?: string;
  /** Smaller, calmer field for the sign-in panel. */
  compact?: boolean;
}

/**
 * The atmospheric field behind the composition: a slow grain-and-gradient wash
 * with a static radial fallback if WebGL is unavailable.
 */
export function StageAtmosphere({ className, compact = false }: AtmosphereProps) {
  return (
    <div className={className} aria-hidden="true">
      <Grainient
        className="ct-grain"
        color1={compact ? "#0c0a1e" : "#0e0b20"}
        color2={compact ? "#141033" : "#17123a"}
        color3="#030306"
        timeSpeed={0.28}
        warpStrength={0.26}
        warpFrequency={1.8}
        warpSpeed={0.11}
        warpAmplitude={55}
        blendAngle={128}
        blendSoftness={0.85}
        rotationAmount={36}
        grainAmount={0.05}
        grainScale={1.3}
        contrast={1.02}
        gamma={1.1}
        saturation={0.86}
        centerY={-0.04}
        zoom={1.9}
      />
    </div>
  );
}
