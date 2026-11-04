# HADA Content Studio — Agent Contract

Read `SPEC.md` and `ReSPEC.md` before significant work. Read the project-root
`WHY.md` before significant work; it records human reasons. A missing file is a missing
record, not evidence that the project has no purpose or priorities. `SPEC.md` is the
approved behavior contract; `ReSPEC.md` reports what the implementation currently
does.

## Authority and scope

- Follow the user's latest explicit direction. Keep facts, user decisions, analysis,
  proposals, and unknowns clearly distinguished.
- Update `SPEC.md` before changing behavior. Validate and reconcile `ReSPEC.md` after
  each implementation phase.
- Treat pre-existing, untracked, user-owned, and unknown files as protected. Inspect
  Git state before and after work. Never use reset, clean, destructive checkout, or
  history rewriting to discard work.
- `WHY.md` is human-owned. Record only durable reasons directly stated by the user or
  explicitly adopted from a proposal. Use `python tools/record_why.py --root PROJECT_ROOT`
  to append one dated entry; do not record transient directions, agent analysis,
  external facts, or inferred motivations. Do not ask the user to repeat or separately
  confirm a reason they just stated or adopted. Preserve earlier entries and never
  invent attribution or backdate a record.
- The repository-root `WHY.md` is the only rationale-history scope declared for Content
  Studio 0.1.1. Mini-project `project.yaml` purpose fields are current summaries, not
  historical WHY logs. Do not add nested WHY files without first declaring their scope
  in `SPEC.md`.
- The root is controlled. Add a path only when it is declared in `SPEC.md` and
  classified in `config/template-manifest.json`.
- Do not put character instance records or character images in Dev or reusable Template.
  Only the Sample may contain its fictional character data.
- Do not automatically delete accepted, unselected, reference, user, or unknown assets.

## Data and image safety

- Store reusable knowledge separately from each mini-project's audience, purpose,
  scope, and adaptation.
- Preserve stable character, item, asset, prompt, and production IDs. Link items to
  characters through the declared many-to-many relationship; do not copy mutable item
  definitions into character records.
- Retain exact resolved image-generation prompts and provenance sidecars privately.
- A generated original is a protected, non-reproducible source master. It must never be
  placed in a publication path or directly exposed externally.
- Create public derivatives only with the specified Python profile. Reject unconfigured
  destinations and failed metadata checks. Do not claim removal of invisible embedded
  signals unless separately verified.
- Keep permanent approved assets and character reference sheets distinct from
  `discard_candidates/` and one-time transient analysis inputs.
- `build/` is for byte-identical reproducible outputs only. Preserve final and
  non-reproducible image outputs as durable project artifacts.

## Base, versions, and Git

- `config/template-manifest.json` is the canonical Content Studio version and ownership
  source. Content Studio has an independent version; Base compatibility is separate.
- Base 0.1.1 is the tested compatibility reference, not authorization to run the direct-Base
  updater against this specialized template.
- Never push. Commit only completed, validated Dev phase files after scoped diff review.
  Never commit the public Template or Sample repositories as the agent.
- Do not publish, deploy, or send files to external services without explicit direction.

## Verification and reporting

- Use deterministic validation for schemas, hashes, asset relationships, publication
  gates, exact output profiles, and version mirrors.
- Report what changed, checks run, remaining decisions, and the local commit ID when a
  phase checkpoint is created. Never report an unrun check as passing.
