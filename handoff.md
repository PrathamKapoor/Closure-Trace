# Developer Handoff

Closure-Trace is the ForgeHacks AI + Cybersecurity project built on SAT-SA /
TRUST-SAT. The Python package and CLI retain their established names.

## Start here

- [README](README.md): requirements, installation, local demo, and checks.
- [Documentation index](docs/README.md): architecture and component guides.
- [System flow](flow.md): data flow and component interactions.
- [Decision log](decisions.md): architectural choices and operational history.
- [API contract](docs/API_CONTRACT.md): hosted workbench integration.
- [Deployment runbook](deploy/README.md): hosted configuration and recovery.

## Local development

Install the Python requirements and package, then run
`python scripts/local_stack.py --seed-demo`. The stack initializes SQLite,
starts the API and worker, and loads synthetic submissions. Generated data
and login credentials remain in ignored `.satsa-local/`.

From `web/`, install dependencies with `npm ci`, set `SATSA_API_BASE_URL` to
`http://127.0.0.1:8000`, and run `npm run dev`. No external model credentials
are required for the default demo. See [provider setup](docs/LLM.md) before
enabling optional reviewer briefings with your own credentials.

## Verification

Run `python -m pytest tests/ -q` for backend tests and `npm run check` from
`web/` for lint, types, and the production build. PostgreSQL, S3, browser,
and hardware-provider checks need their documented services or tooling.
Historical test counts in engineering notes apply to their recorded commits.

## Security and deployment

Do not commit populated environment files, credentials, signing keys, local
databases, or runtime artifacts. Configuration templates contain placeholders.
The existing credential-rotation decision and its verification are recorded in
[D-023](decisions.md#d-023-rotate-the-exposed-administrator-credential-new-administrator-member-revoke-the-old-credential-itself).

Deployment references to `trustsat.mpst.me` describe the inherited TRUST-SAT
deployment. Publishing this repository does not deploy a separate Closure-Trace
instance. Follow the runbook and supply your own infrastructure configuration.

## Submission requirements

The ForgeHacks submission needs the public repository, a 2–4 minute public
demo video, a problem statement and target users, technical approach, impact,
and screenshots, architecture, or a testing link. Evaluation claims must retain
the [documented limitations](docs/CLAIMS.md).
