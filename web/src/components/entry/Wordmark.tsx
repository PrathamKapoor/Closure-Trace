/**
 * The entry wordmark, painted as two metrically identical glyph planes: one
 * behind the sculpture and one in front. Only the front plane draws, so every
 * visible glyph sits above the metal while the layering structure (and the
 * scene's depth) is preserved.
 *
 * The glyph list is derived from the product name, and the scattered start
 * poses, spacing and per-glyph delays are computed from the word's own length
 * in normalised units. A longer name therefore keeps the same total spread and
 * the same ~0.8s assembly window as the source composition instead of
 * inheriting hard-coded constants for a nine-glyph word.
 */

const WORD = "CLOSURE-TRACE";
const GLYPHS = Array.from(WORD);

/** Assembly window and spread, expressed against the reference nine-glyph word. */
const REF_STEPS = 8;
const DX_STEP = -0.05;
const DY_STEP = 0.16;
const DY_OFFSET = 0.3;
const ROT_BASE = 3;
const ROT_SPAN = 8;
const DELAY_BASE = 150;
const DELAY_SPAN = 85 * REF_STEPS;

function pose(i: number, count: number) {
  const steps = Math.max(1, count - 1);
  const u = i / steps;
  const mid = (count - 1) / 2;
    const rot = (i % 2 === 0 ? 1 : -1) * (ROT_BASE + u * ROT_SPAN);
    return {
      dx: `${(i - mid) * DX_STEP * (REF_STEPS / steps)}em`,
      dy: `${((i - mid) * DY_STEP * (REF_STEPS / steps) + DY_OFFSET).toFixed(3)}em`,
      rot: `${rot.toFixed(2)}deg`,
      delay: Math.round(DELAY_BASE + (DELAY_SPAN * i) / steps),
    };
}

interface Props {
  live: boolean;
  instant?: boolean;
  plane: "back" | "front";
  dimmed?: boolean;
}

export function WordPlane({ live, instant = false, plane, dimmed = false }: Props) {
  return (
    <div
      className={`entry__word-plane entry__word-plane--${plane} ${dimmed ? "entry__word-plane--dim" : ""}`}
      aria-hidden="true"
    >
      <span className="entry__word">
        {GLYPHS.map((ch, i) => {
          const p = pose(i, GLYPHS.length);
          // Keep both planes metrically aligned, but paint every glyph above
          // the sculpture: the back plane is laid out, then suppressed.
          const suppressed = plane === "back";
          return (
            <span
              key={i}
              className={`entry__letter ${ch === "-" ? "entry__letter--dash" : ""} ${live ? "entry__letter--in" : ""} ${
                suppressed ? "entry__letter--behind" : ""
              }`}
              style={{
                ["--lx" as string]: p.dx,
                ["--ly" as string]: p.dy,
                ["--lr" as string]: p.rot,
                ["--ld" as string]: `${instant ? i * 28 : p.delay}ms`,
              }}
            >
              {ch}
            </span>
          );
        })}
      </span>
    </div>
  );
}
