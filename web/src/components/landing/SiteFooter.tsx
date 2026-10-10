import Link from "next/link";

const REPO = "https://github.com/PrathamKapoor/Closure-Trace";

export function SiteFooter() {
  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__top">
          <div>
            <p className="footer__brand">CLOSURE-TRACE</p>
            <p className="footer__desc">
              Evidence review for security alerts and case histories: investigation gaps and
              premature closures surfaced for human decision, with the recorded review bound by
              TRUST-SAT, an ML-DSA-65 post-quantum signature.
            </p>
          </div>
          <div className="footer__cols">
            <div className="footer__col">
              <span className="label">Product</span>
              <ul>
                <li>
                  <Link href="/login">Open console</Link>
                </li>
                <li>
                  <a href="#workflow">Workflow</a>
                </li>
                <li>
                  <a href="#limits">Limitations</a>
                </li>
              </ul>
            </div>
            <div className="footer__col">
              <span className="label">Documentation</span>
              <ul>
                <li>
                  <Link href="/methodology">Methodology</Link>
                </li>
                <li>
                  <Link href="/security">Security and TRUST-SAT</Link>
                </li>
                <li>
                  <a href={REPO} rel="noopener noreferrer">
                    Repository
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div className="footer__base">
          <p>
            Closure-Trace · MIT licensed · Built on the SAT-SA supervisory analytics system ·
            Presentation components adapted from the mental.ai frontend, attribution retained
          </p>
          <p>TRUST-SAT is the integrity layer, not a claim about truth.</p>
        </div>
      </div>
    </footer>
  );
}
