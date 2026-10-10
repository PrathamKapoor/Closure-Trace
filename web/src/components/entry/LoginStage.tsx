"use client";

import { Stage, StageAtmosphere } from "./Stage";
import "./stage.css";

/**
 * The entry sculpture as the sign-in page's visual panel: the same stage,
 * wordmark planes and grain field as the landing entry, composed into the
 * left column of the authentication screen. Decorative; the form beside it is
 * the real credential form and works with this layer removed.
 */
export function LoginStage() {
  return (
    <div className="ct-visual ct-login-visual">
      <StageAtmosphere className="ct-grain" compact />
      <Stage lettersLive sculptureLive decorated />
    </div>
  );
}
