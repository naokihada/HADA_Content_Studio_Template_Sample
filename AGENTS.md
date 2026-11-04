# HADA Content Studio — Agent Contract

Read `SPEC.md`, `ReSPEC.md`, and the project-root `WHY.md` before significant work.
`WHY.md` records human reasons and priorities; a missing file is a missing record, not
evidence that the project has no purpose. `SPEC.md` is the approved behavior contract;
`ReSPEC.md` reports what the implementation currently does.

## Authority and scope

- Follow the user's latest explicit direction. Keep facts, user decisions, analysis,
  proposals, and unknowns clearly distinguished.
- Update `SPEC.md` before changing behavior. Validate and reconcile `ReSPEC.md` after
  each implementation phase.
- Treat pre-existing, untracked, user-owned, and unknown files as protected. Inspect
  Git state before and after work. Never use reset, clean, destructive checkout, or
  history rewriting to discard work.
- Do not automatically delete temporary files or outputs. Ignore only known caches and
  designated `tmp/` or `temp/` scratch paths; do not blanket-ignore `tests/` or
  `output/`, which may hold source tests or retained deliverables. Preserve unknown
  files unless their ownership and retention policy are explicit.
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

- When the owner asks for an infographic proposal, plan, or production, automatically
  prepare an exact page-equivalent count and a complete page-by-page SEU outline with
  the minimum information points, explanation, memory cue, evidence status, and visual
  placement required by `docs/INFOGRAPHIC_PROPOSAL_GUIDELINE.md`. Apply this by default
  without asking the owner to restate it. Present the substantive proposal naturally;
  do not announce internal checks or expose the internal workflow.
- Treat every infographic as a static memory aid/reference. Exclude quizzes, exercises,
  fill-in-the-blank items, questions that ask for a response, self-checks, and answer
  keys. Use `docs/INFOGRAPHIC_REVIEW_CHECKLIST.md`; plan at least four complete SEUs
  before generation and save the generated-image review beside the provenance before
  acceptance or export.
- Every infographic includes the same character in a full-body view, a face close-up,
  and a clearly chibi depiction. Preserve identity anchors. Give the full-body and face
  close-up views strongly separate areas, and vary outfit, pose, and art style between
  them. A merged/connected full-body and close-up layout scores 0/20 for layout and
  fails its hard gate.
- For new female-character depictions, read
  `extensions.content_studio.character_visual_defaults.female_character`. Explicit
  character canon and direct user instructions take precedence; project settings
  override template defaults. If no value is set, use an adult 18-year-old neat,
  refined, beautiful female university-student presentation; dresses or one-piece
  outfits by default; trousers only for uniforms, fieldwork, or special attire; and no
  outerwear except in those contexts or an open-front layer with an above-knee skirt.
  Swimming defaults to a one-piece competitive swimsuit. Across distinct planned looks,
  target about one-third short-sleeved summer outfits. Carry effective values into the
  proposal and prompt; never silently alter existing character canon or references.
- For a multi-output infographic series, read
  `extensions.content_studio.series_layout` from the project settings and carry its
  effective values into the proposal and prompts. Defaults are one portrait/landscape
  orientation for the series, maximum page-to-page layout variation, no additional
  shared visual elements, and a required next-page handoff. Under the default maximum
  setting, plan a distinct dominant composition and reading path for every output page.
  Follow a configured custom variation rule when present. Make the next page inviting
  while keeping each page's information complete and avoiding quizzes, questions, or
  withheld facts. The final page gets a clear close. Explicit project settings override
  these defaults; do not silently add shared series branding or repeat layouts.
- Do not invent or change post-generation rubric criteria, weights, or score cutoffs.
  The MAX5 prompt review evaluates prompt text only; it cannot approve the generated
  image.
- Store reusable knowledge separately from each mini-project's audience, purpose,
  scope, and adaptation.
- Preserve stable character, item, asset, prompt, and production IDs. Link items to
  characters through the declared many-to-many relationship; do not copy mutable item
  definitions into character records.
- Retain exact resolved image-generation prompts and provenance sidecars privately.
- For new single-output infographic prompts, use
  `profiles/prompts/infographic-defaults.yaml`; for multi-output series, use
  `profiles/prompts/infographic-series-defaults.yaml`. Keep older profile files
  available for historical sidecar validation; do not edit their contents.
- Before external image generation, save the agreed brief, prompt-review record, and
  exact selected prompt under the infographic production's `prompts/` directory. Use
  the fixed five-candidate/90-point review policy and validate the archive first. The
  selected prompt must explicitly encode the fixed infographic score criteria and all
  hard gates in `docs/INFOGRAPHIC_REVIEW_CHECKLIST.md`; only `selected_pass` authorizes
  generation. Treat the first generation call as the production attempt, never as a
  disposable trial or an acceptable planned failure.
- Save candidate 1 and its evaluation before drafting a revision; append each later
  candidate without changing prior text or evidence. Once the user agrees to the brief,
  do not add another prompt-approval step unless the brief or scope changes.
- Preserve exact candidate text and hashes, criterion evidence, critical-check results,
  revision-to-finding links, and runtime-reported evaluator metadata. Never infer a
  hidden model ID or switch evaluators automatically. Stop the review if the evaluator
  is unavailable or its observable identity changes.
- Keep pre-review prompts and generations as historical data; never rewrite them as if
  they had been reviewed before generation.
- Use one image-generation attempt for each authorized `selected_pass` prompt review.
  Do not retry or switch generation/evaluation models automatically. If the output fails
  an image gate, reject it, record evidence, and report the failure; any further
  generation requires an owner-directed next step and a new prompt review.
- A generated original is a protected, non-reproducible source master. It must never be
  placed in a publication path or directly exposed externally.
- Record available image-generation arguments in the generation provenance using a
  project-relative, hashed YAML file. Do not include credentials, API keys, or tokens.
- Create public derivatives only with the specified Python profile. Reject unconfigured
  destinations and failed metadata checks. Do not claim removal of invisible embedded
  signals unless separately verified.
- Keep permanent approved assets and character reference sheets distinct from
  `discard_candidates/` and one-time transient analysis inputs.
- `build/` is for byte-identical reproducible outputs only. Preserve final and
  non-reproducible image outputs as durable project artifacts.

## Conversation logs and AI Reset

- Conversation logging is optional and off by default. Do not passively collect or
  automatically retrieve chats. Existing imported files in `AI/Logs/` are user-owned
  provenance; never move, replace, or delete them during template updates.
- Keep conversation history separate from durable decisions and rationale: logs preserve
  provenance, production/project records hold decisions, and `WHY.md` holds durable
  human reasons.
- Treat `AI/` as a bounded work area. Content Studio has no whole-directory reset
  command or automatic cleanup. A reset may target only specifically identified
  disposable task scratch; preserve durable knowledge, assets, decisions, reports,
  logs, and unknown files.

## Base, versions, and Git

- `config/template-manifest.json` is the canonical Content Studio version and ownership
  source. Content Studio has an independent version; Base compatibility is separate.
- Base 0.1.1 is the tested compatibility reference, not authorization to run the
  direct-Base updater against this specialized template. Bring over only compatible
  local Base policy changes after reviewing the files; never replace Content Studio's
  identity, version, or domain rules with Base values.
- Never push. Commit only completed, validated Dev phase files after scoped diff review.
  Never commit the public Template or Sample repositories as the agent.
- Do not publish, deploy, or send files to external services without explicit direction.

## Verification and reporting

- Use deterministic validation for schemas, hashes, asset relationships, publication
  gates, exact output profiles, and version mirrors.
- Report what changed, checks run, remaining decisions, and the local commit ID when a
  phase checkpoint is created. Never report an unrun check as passing.
