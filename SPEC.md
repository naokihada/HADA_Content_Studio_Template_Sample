# HADA Content Studio Template — Master Specification

**Specification status:** Approved implementation plan
**Specification version:** 0.1.1
**Template version:** 0.1.1
**Base compatibility:** minimum 0.1.0; tested 0.1.1
**Status date:** 2026-11-04
**Scope:** Content Studio Dev, reusable Template, and local Sample artifacts.

## 1. Purpose

HADA Content Studio manages reusable, sourced knowledge and project-specific context,
then develops infographic productions from them. Its data model also provides a
portable character, item, appearance, asset, and provenance core that HADA Story Studio
can reuse. Story continuity and narrative planning belong to Story-specific extensions.

The system is an editorial and asset-management workflow. It does not claim that an
image-generation model is deterministic or that generated media can be recreated from
its prompt alone.

## 2. Goals and non-goals

Goals:

- Reuse knowledge modules across distinct mini-projects such as school study and
  motorcycle interests without forcing domain-specific records into one schema.
- Preserve evidence, attribution, approval state, exact generation prompt, assets, and
  versions from source through final publication.
- Treat an infographic as a static memory aid and reference, with the information depth
  of at least four complete slide-equivalent units; do not turn it into a practice or
  quiz sheet.
- Before prompt drafting, provide a decision-ready infographic proposal with an explicit
  page-equivalent count and sufficiently specific key points for every planned page.
- Save and review each image prompt before generation, including the agreed brief,
  candidate text and hashes, rubric evidence, evaluator identity, and selected prompt.
- Keep character identity stable while allowing appearance variants such as chibi
  proportions, styles, poses, and outfits.
- Model reusable items independently from characters, with many-to-many character-item
  links and composable outfits/loadouts.
- Keep accepted images and reusable character references as protected long-term assets;
  separate unselected candidates and one-time analysis references.
- Make external publication fail closed unless a Python-produced derivative has passed
  the selected destination profile and metadata checks.
- Keep the initial production module limited to infographics.

Non-goals for 0.1.1:

- Presentation, social carousel authoring, video, songs, animation, long-form fiction,
  Story continuity, or editing-software integration.
- Direct provider API automation. Generation may be performed in an external image
  service; this project records its prompt and imports the resulting source asset.
- Publishing or deploying to external services.
- Practice and assessment formats inside an infographic, including quizzes, exercises,
  fill-in-the-blank items, learner-response questions, self-checks, and answer keys.
- Automatic deletion by age/count. Only a specifically selected one-time analysis
  session can be explicitly discarded.

## 3. Base relationship and versioning

This is a specialized template with its own identity and version. `config/template-manifest.json`
is the source for `hada-content-studio-template` version `0.1.1`; Base compatibility is
separate and records minimum Base version `0.1.0` and tested Base version `0.1.1`.
Schema and content-data
versions are independent. The Base direct-template updater is not assumed to update
this specialized template. Base compatibility does not authorize a Base updater to
replace Content Studio files or version carriers. Adopt shared Base changes by reviewing
the local source files and applying only compatible changes under this SPEC. Update the
tested Base version only after verifying compatibility; keep Content Studio's own
version under its release policy.

## 4. Artifact boundaries and character-data rule

- **Dev:** implementation, schemas, tests, full human-owned `WHY.md`, and existing
  private imported AI logs. Contains no character instance records or character images.
- **Template:** reusable schemas, tools, policies, and empty examples only. Contains no
  character instance records, character images, project prompt-resolution records, or
  prompt-review archives.
- **Sample:** fictional `Cute Elf Girl` data and assets plus a tutorial infographic
  explaining template capabilities. Sample is local and must not be committed by the
  agent. Future publication must use only approved transformed derivatives; generated
  originals and internal prompt/provenance records are excluded from publication. Its
  existing artwork predates the four-SEU review policy and is not retroactively certified.

The reusable validator does not hard-code a sample character's name. A Sample manifest
may declare `artifacts.sample_character_name`; when present, validation requires that
display name to exist. This keeps the reusable Template generic while allowing this
local Sample to name its one fictional character.

Pre-existing user-owned files are preserved. Public artifact preparation never copies
Dev WHY history, AI logs, personal data, secrets, or unapproved raw masters.

### 4.1 WHY lifecycle

`WHY.md` is the human-owned, append-only-in-intent record of durable reasons, values,
priorities, and changes of mind. Before significant work, read the project-root
`WHY.md`. A missing file is a missing record, not evidence that the project has no
purpose or priorities.

When the project owner directly states a durable reason or explicitly adopts a proposed
reason, record it in the project-root `WHY.md`. Do not record transient task directions,
agent analysis, external facts, or inferred motivations. Do not ask the owner to repeat
or separately confirm a reason they just stated or adopted. If no reason was stated or
adopted, do not create content on the owner's behalf.

Use `python tools/record_why.py --root PROJECT_ROOT` to enter and append one reason.
The tool uses the local date, preserves existing content, and creates a generic WHY
placeholder only when the file is missing and nonblank reason text was supplied. The
interactive mode accepts multiple lines, including blank lines, and ends on a single
period line or EOF; blank-only input makes no change. If an existing WHY file is empty
or whitespace-only, the tool initializes its generic header while preserving existing
bytes, then appends the entry. The `--reason` option accepts an explicit entry directly.
The tool refuses a symlink or non-file `WHY.md`. The owner may also edit the file
directly. Preserve the owner's wording and do not invent supporting details,
attribution, or historical dates.

Record a change of mind as a new dated entry explaining what changed and what prior
direction it supersedes; keep the earlier entry. Record factual corrections as dated
clarifications that refer to the earlier entry. The repository-root `WHY.md` is the
only rationale-history scope declared by Content Studio 0.1.1. Mini-project
`project.yaml` purpose fields remain concise current descriptions, not historical WHY
logs. Do not create nested WHY files unless a future SPEC explicitly declares their
scope and lifecycle.

Dev retains its real project history. Reusable Template and Sample must each include a
generic purpose-only WHY placeholder; neither may contain Dev's private rationale or
invented sample motivation. Existing consumer WHY files remain user-owned and are
never overwritten by a template update.

### 4.2 Conversation logs and AI work area

Conversation logging is optional and off by default. Content Studio does not passively
collect or automatically retrieve chats. Existing imported files under `AI/Logs/` are
user-owned provenance; do not move, replace, or treat them as temporary material during
template updates. Conversation logs preserve source/history, production records hold
decisions, and `WHY.md` holds durable human reasons; one record type does not replace
another.

`AI/` is an explicitly bounded work area, not a blanket reset target. Content Studio
defines no reset command or automatic reset. A reset may target only specifically
identified disposable task scratch. Never clear the whole directory or remove durable
knowledge, assets, decisions, reports, imported logs, or unknown files.

## 5. Portable Studio Core

Core entities use stable IDs, explicit schema versions, source/rights metadata, and
forward-compatible optional extensions. Markdown is the human-readable content format;
small YAML/JSON records hold relationships and machine-checked fields. A database is
not required for 0.1.0.

### 5.1 Character and item model

- `CharacterDefinition` identifies a character and stores identity anchors, canonical
  reference IDs, provenance, and visibility. It does not hard-code one body proportion
  or art style as the sole valid depiction.
- `AppearanceVariant` applies a named presentation transform (for example chibi,
  realistic, outfit-specific, or scene-specific) while retaining the same character ID
  and identity anchors.
- `ItemDefinition` has its own stable ID and a broad kind/slot such as clothing,
  vehicle, weapon, accessory, or prop. An item can be referenced by multiple characters.
- `CharacterItemLink` is the canonical many-to-many association. It records character
  ID, item ID, role (wears, rides, wields, owns, or associated), optional variant,
  context, and validity. Do not duplicate ownership by embedding mutable item copies in
  each character record.
- `Outfit`/`Loadout` composes item IDs and can be shared by characters. Character-
  specific fitting or color variations are explicit link/variant data.
- `AssetReference` points to immutable asset IDs and versions by relative path and
  SHA-256, not by an unversioned filename alone.

Story can consume these core records without conversion. Story adds its own series,
scene, timeline, relationship changes, canon, and continuity schemas under a separate
extension namespace. Content-only learning fields do not enter the shared core.

### 5.2 Mini-project structure

Every mini-project has a stable ID and a `project.yaml` with title, domain/tags, purpose,
audience, scope, privacy/visibility, status, and referenced knowledge, characters,
items, and productions. Domain labels are open-ended; school entrance exams and
motorcycle hobbies do not require separate top-level data models. A project index is
derived from project records and is not a second editable source of truth.

## 6. Knowledge and evidence

Knowledge modules are independently reusable and scoped. Each claim distinguishes
source-backed fact, user experience, user decision, analysis/inference, and proposal.
External sources record locator, relevant passage/page, retrieval date when relevant,
verification state, and usage rights. Projects reference stable knowledge IDs and
versions; they do not silently modify shared source knowledge when adapting it for a
particular audience.

## 7. Prompt and generation provenance

Prompt templates are layered and customizable in this order: shared base, domain,
medium, project, character/item, and production request. A profile declares its ordered
default layers; a production may append project/entity/request layers without editing
the shared profile. Each layer has a stable ID, semantic version, and source file hash.
For the v0.1.1 release preparation, the default infographic profile and layout layer
both use version `0.1.1`, aligned with the Content Studio template version. Do not bump
these version strings independently without the owner's direction.
The resolver performs literal `{{variable}}` substitution from an explicit values file,
rejects unknown or unresolved placeholders, preserves layer order, and produces the
exact resolved prompt plus its SHA-256. It must not interpret prompt text as executable
code or fetch external instructions.

Each prompt resolution is an immutable private YAML sidecar linked to its production.
It stores the exact resolved prompt, profile ID/version, ordered layer IDs/versions/
paths/hashes, profile and values-file paths/hashes, actual substitution values,
referenced asset IDs/versions/hashes, and prompt hash. Validation reloads these exact
inputs, checks hashes and declared layer order, then recomposes the text to verify the
stored result. Later generation intake links provider/model, generation time or known
provider job ID, immutable source path/hash, reviewer, and disposition to that prompt
resolution. A profile name alone is insufficient provenance. Changing a prompt,
template layer, or reference creates a new resolution; existing sidecars are never
rewritten. Prompt records and provider identifiers remain internal and are not copied
into media metadata or publication artifacts.

Prompts and internal provider identifiers are private project records and are never
copied into public-safe media metadata. Changing a prompt or reference creates a new
generation/asset version; it does not rewrite the old record.

### 7.1 Pre-generation prompt archive and review

Before creating an image, agree the production brief with the user and preserve it at
`projects/<domain>/<project-id>/productions/infographic/prompts/<prompt-id>.brief.md`.
Save the prompt review record beside it as `<prompt-id>.prompt-review.yaml` and the
selected exact prompt as `<prompt-id>.prompt.md`. All three are private project records
and must stay outside publication directories. The prompt file contains only the exact
text to send to the image service; its UTF-8 SHA-256 is also recorded in the review
record. The existing prompt-resolution YAML remains the source record for layered
inputs. The review record links to that resolution, while the image-generation
provenance record remains the source of truth for provider/tool, optional generation
argument values with their project-relative source path and hash, generated source
hash, and generation time.

Build one 100-point prompt rubric from the agreed brief, including critical checks for
factual accuracy, explicit constraints, and contradictions. Keep that prompt rubric
and its weights fixed for that review. Evaluate the initial draft as candidate 1, then
create at most four revisions, for a maximum of five candidates. A prompt candidate
passes at 90 points or higher. This score evaluates prompt instructions before image
generation; it does not evaluate or approve the generated image and does not replace
the fixed post-generation infographic rubric in §7.2.
Each candidate stores its exact text and hash, criterion scores and evidence, critical
check results, evaluation time, and runtime-reported evaluator metadata. Each revision
identifies the immediately preceding candidate, the findings it addresses, and the
concrete changes made. A revision must address every recorded finding from its
predecessor; unrelated rewrites are not a substitute.

Stop at the first candidate scoring at least 90 and select it. A critical-check failure
cannot be offset by points from other criteria and cannot pass. If all five candidates
score below 90, select the highest-scoring candidate, record and report its score as
below threshold, and do not inflate its score. For a tie, prefer fewer unsupported
assumptions and clearer instructions; record the selection reason. The validator checks
record structure and arithmetic, not the truth or quality of an AI judgment.

A `selected_below_threshold` record preserves the best reviewed candidate for audit; it
does not authorize image generation. Only `selected_pass` with a score of at least 90
and all critical checks passing is eligible for generation. If no candidate passes,
stop before calling an image service and report the shortfall. Do not use a below-
threshold prompt as a disposable first attempt.

Record provider, API model ID, displayed model name, and reasoning strength for each
evaluation only when exposed by the runtime. Use `unknown` or `not_exposed` when a
value is unavailable; never infer the active model from a setting. Do not switch
evaluators automatically. If the evaluator becomes unavailable or an observable model
change occurs during the loop, stop comparison, record the halt, and do not generate an
image from that incomplete review.

Before the first and only image-generation attempt for a review, verify that the review
is `selected_pass`, all critical checks pass, and the brief, review record, and exact
selected prompt are saved and validate. Treat this first call as the intended production
attempt, not as a disposable trial. Before calling the image service, confirm that the
prompt explicitly carries the fixed content, character, visual, and hard-gate requirements
in §7.2; do not knowingly submit a prompt with a missing requirement or an unresolved
finding. The template does not call a provider or publish images. Generation is external
and non-deterministic, so even a fully reviewed prompt cannot guarantee the generated
image. If the result fails a gate, record the visible evidence, reject it, and report the
failure; do not call it an acceptable first try or retry automatically. Any later
generation requires an owner-directed next step and a new prompt review. Existing
pre-review prompts and images remain historical records: do not retroactively score,
rewrite, or imply they were reviewed before generation. New projects enable the review
gate; projects that predate it may retain their documented legacy state.
New `project.yaml` examples set `prompt_review_required: true`. Validation and image
intake require a completed prompt-review record for such productions. A missing flag is
treated as a legacy project setting and does not rewrite or reject prior generations.
Validation and image intake permit a generation record only for a `selected_pass` review
and at most one image-generation intake record per review. Because provider calls are
external, validation cannot prove that an unrecorded failed call did not occur.

### 7.2 Infographic content standard and generated-image review

An infographic is a static memory aid/reference. It presents organized knowledge for
later recall; it does not ask the reader to practice, answer, or test themselves. Do not
include quizzes, exercises, fill-in-the-blank items, prompts that ask the reader to
respond, self-checks, or answer keys. A complete, solved static example may be used as
an explanation or memory cue, but it must not leave a blank or ask the reader to solve
it. Informational sequences and declarative headings remain allowed.

#### Series layout policy

A project that publishes multiple infographic outputs as a series uses the project
setting `extensions.content_studio.series_layout`. Its effective settings are recorded
in the proposal and carried into each prompt. If the setting is absent, use portrait or
landscape as selected for that series, `layout_variation: maximum`, no additional shared
visual elements, and `next_page_anticipation: required`. A custom layout variation must
include a non-empty `layout_variation_details` rule.

- Keep one selected orientation (portrait or landscape) across the series. This is the
  only shared visual/layout element by default. A project may explicitly list additional
  shared elements in its setting; do not infer extra shared branding or layout rules.
- Under the default `maximum` variation, give every output page a distinct dominant
  composition, focal placement, and reading path. Under a configured `custom` rule,
  follow its explicit variation details. Avoid repeating a page skeleton, panel map,
  character placement, or dominant visual structure unless project settings allow that
  element to recur or the content makes a documented exception necessary for clarity.
- Make the next page feel inviting through a page-specific visual handoff or preview of
  its subject. Each page must still communicate its own facts completely; do not hide
  information, leave explanations unfinished, or use quizzes, questions, or exercises
  as a hook. Give the final page a clear visual and informational close.
- Do not pool content requirements across a series: every output infographic retains
  the existing minimum of four complete SEUs and twelve unique information points.
- Preserve legibility, factual accuracy, and the existing character requirements while
  varying page layouts. Layout variation is not permission to weaken these gates.

The setting is a configurable default, not a permanent lock. An explicit project value
overrides the defaults for that project. Record the effective orientation, variation
level, extra shared elements, and next-page anticipation setting in the proposal and
prompt-review brief so the generation prompt can follow them. New series outputs use
`profiles/prompts/infographic-series-defaults.yaml`; its request layer carries the
resolved settings and page-specific composition/handoff. Historical profile paths stay
unchanged for existing prompt resolutions.

#### Female-character appearance and wardrobe defaults

For new female character depictions, read the effective project setting at
`extensions.content_studio.character_visual_defaults.female_character`. Explicit
character canon and direct user instructions take precedence; project values override
the template defaults. A missing project value inherits the defaults below. Do not
rewrite existing character definitions or reference images to match them.

- Default presentation: an explicitly adult, 18-year-old female university student
  with a neat, refined, elegant, beautiful appearance.
- Default everyday outfit: a dress or one-piece garment. Trouser/pants looks are
  prohibited unless the outfit is a uniform, fieldwork clothing, or special attire.
- Outerwear is prohibited by default. It may be used for a uniform, fieldwork clothing,
  or special attire. Outside those contexts, an open-front outer layer is allowed only
  with an above-knee skirt, such as a blouse with an open white coat; closed-front coats,
  jackets, and cardigans remain disallowed.
- For swimming scenes, use a one-piece competitive swimsuit by default. Project or user
  settings may replace it.
- Across the distinct planned female-character outfit looks in a production or series,
  target approximately one-third short-sleeved summer outfits. Count each distinct look
  once rather than counting repeated copies. The project may change this target.

These values are stored under the mini-project's `extensions.content_studio` settings
and may be overridden field by field. The prompt must record the effective age/adult
status, presentation, outfit, permitted pants/outerwear contexts, summer outfit target,
and swimwear default where relevant. New single-output infographic prompts use
`profiles/prompts/infographic-defaults.yaml`; multi-output series use
`profiles/prompts/infographic-series-defaults.yaml`. Historical prompt profiles remain
unchanged for provenance.

#### Proposal before prompt drafting

Whenever the owner requests an infographic proposal or a new infographic production,
prepare a page-by-page content plan before drafting the image prompt. The proposal must
state an exact planned page-equivalent count of at least four; do not use an open-ended
count such as “four or more” in place of a concrete plan. A planning page is one SEU,
not a count of final image files or physical output pages. Unless the owner requests
multiple outputs, these planned pages may be composed into one infographic canvas.

For every planned page/SEU, list a specific title or focus, one clear takeaway, at least
three countable and non-redundant information points, the explanatory relationship
among them, and a static memory cue. Points must be concrete enough to guide content
selection and later prompt writing; topic labels or placeholders such as “key facts” do
not count. State known sources or distinguish facts, user decisions, and unresolved
items; never fill gaps with invented material. Give the whole proposal a stated audience,
purpose, scope, and intended single-canvas composition, including how the pages form a
coherent reading order. Include the required character depictions, identity anchors,
view separation, and differences in outfit, pose, and art style between full-body and
face close-up views.

Apply this planning policy by default without requiring the owner to restate it. Present
the page count, page-by-page points, visual direction, and material unresolved choices
as the natural proposal. Do not burden the proposal with a notice that internal checks
were applied. If the agreed subject cannot support the proposed number of accurate,
distinct pages, state the shortfall and offer a concrete scope expansion or split; do
not pad the outline or proceed to prompt generation as if the minimum were met.

#### Four slide-equivalent units (SEUs)

Before generation, outline the infographic as at least **four complete, distinct SEUs**.
One SEU is a self-contained, non-interactive knowledge module equivalent to one
informative slide. Each SEU must contain all of the following:

1. One distinct concept, distinction, process, cause, or other take-away.
2. At least three countable, non-redundant information units in total, including the
   take-away. A label, heading, decorative element, character illustration, or repeated
   fact does not count as an information unit.
3. An explicit explanatory relationship (for example, why, how, when, condition,
   cause-and-effect, contrast, or category membership).
4. At least one static memory cue that makes the relationship easier to recall, such as
   a diagram, comparison, visual grouping, mnemonic, or fully worked reference example.

The four-SEU minimum therefore requires at least 12 non-redundant information units,
four explanatory relationships, and four memory cues. Count each idea once across the
whole infographic; repeated ideas do not increase the total. Examples count only for
the distinct information they add. Do not use practice tasks to meet any count.

If the brief's subject cannot support four accurate, distinct SEUs, do not invent or
pad facts. Report the shortfall and expand the scope or use more than one infographic
before generation. Keep text legible; expand the canvas or split content into multiple
panels/images instead of shrinking text until it is difficult to read.

#### Fixed post-generation rubric

Review every generated infographic against this fixed 100-point rubric. Do not create,
remove, rename, or reweight criteria based on the image or brief. Record each score with
visible evidence from the image and the relevant planned SEU IDs.

This fixed rubric and its gates are also mandatory prompt-writing requirements: the
selected prompt must direct the image service to satisfy them on the first production
attempt. Prompt review remains a separate pre-generation review and cannot substitute
for this post-generation image review.

| Criterion | Weight | What the reviewer scores |
| --- | ---: | --- |
| Character appeal | 30 | Expressive, appealing presentation and styling (12); character presence and visual impact (10); coherent, distinctive presentation (8). |
| Content richness | 30 | Four-SEU coverage and completeness (12); useful explanation and relationships (10); specific, non-redundant information (8). |
| Layout and readability | 20 | Clear reading hierarchy (8); spacing and separation (6); balanced composition and relationship between content and character (6). |
| Memory-support design | 10 | Visual grouping, diagrams, comparisons, or other static cues that make the intended relationships easier to recall. |
| Text and technical fidelity | 10 | Correctly rendered, legible text (6); sufficient image quality and clean execution (4). |

The score is out of 100 and may also be shown as a score out of 10 by dividing by ten.
The prompt-review threshold of 90 applies only to prompt candidates; it is not an
image-acceptance threshold. Report the score and gate results without inventing an
image-score cutoff. The project owner decides acceptance when no hard gate has already
failed.

#### Non-compensating image gates

Any of the following blocks acceptance regardless of the weighted score:

- Any practice/test element listed above appears in the image.
- The content outline or image contains fewer than four complete SEUs, or reaches its
  count with duplicate, decorative, inaccurate, or invented material.
- The infographic does not show the same character at least once in each of these
  clearly distinguishable forms: full body, face close-up, and chibi proportions.
- The full-body and face close-up depictions do not meaningfully differ in outfit,
  pose, and art style.
- The same character is not recognizable across all depictions because its stable
  identity anchors were lost.
- Factual/source errors or materially unreadable text remain.
- The full-body and face close-up views visually merge into one connected composition.
  In that case the Layout and readability score is **0/20** and the image fails the
  gate. Give each view its own clearly bounded area with strong whitespace or another
  clear visual break; a thin divider or small gutter between two immediately adjacent
  views is not sufficient. Do not present them as one composite character panel.

A reviewer must state each gate as pass/fail and cite the visible evidence. This review
is of the generated result, so a high prompt score cannot substitute for it. Save the
review as `assets/generations/<generation-id>/image-review.md` beside the generation
provenance. Use the record outline in `docs/INFOGRAPHIC_REVIEW_CHECKLIST.md`.

## 8. Asset lifecycle, retention, and publication boundary

Non-reproducible AI outputs are source masters, not build artifacts. Preserve source
bytes and hash. Explicit intake copies supported PNG/JPEG source bytes without moving or
rewriting the input. Store accepted masters at
`assets/masters/<asset-id>/<version>/source.<ext>` and declined candidates at
`assets/discard_candidates/<asset-id>/<version>/source.<ext>`. Refuse existing targets.
Each generation sidecar under `assets/generations/<generation-id>/provenance.yaml`
records the prompt-resolution ID, provider/model when known, generation and review
timestamps, disposition, source path/hash, and reviewer. An accepted master and
recurring canonical character references are protected long-term assets. New versions
supersede by link; they do not overwrite accepted versions.

Only accepted masters may enter the export tool. The tool always decodes and re-encodes
pixels with Pillow, applies the selected logo watermark, writes a new durable derivative
under the linked infographic production's `exports/` directory, and creates a hashed
derivative sidecar. Social example profiles downscale within a configured bounding box
and encode a lossy JPEG at a profile-controlled quality. Website example profiles keep
pixel dimensions unchanged and encode PNG. Profile values are editable project policy,
not hard-coded service limits. Export never uploads or publishes.

The derivative metadata scanner is fail-closed for the supported output formats. It
allows only format-structural chunks/segments (PNG IHDR/IDAT/IEND and a standard JPEG
JFIF APP0 segment); EXIF, XMP, IPTC, comments, thumbnails, ICC profiles, other ancillary
chunks, and unexpected JPEG APP segments block the derivative from publication. The
scanner does not claim to detect or remove invisible signals encoded in image pixels.
Failed output and scan evidence are retained and marked blocked, not silently deleted.
`tools/record_publication.py` records a completed manual publication by referencing a
validated derivative; it performs no network operation and cannot record a raw master.

Unselected candidates live under `discard_candidates/` and never appear in publication
indexes. They are not automatically deleted. One-time third-party style-analysis
inputs live in an ignored, isolated transient session; after the explicitly requested
analysis, the session source is discarded. It is not registered as a reusable character
or style reference. Only separately approved, generalized notes may be retained.

### 8.1 Deterministic Python export profiles

- `social`: Python resizes/downscales, applies the configured logo watermark, and uses
  the configured lossy output quality. The untouched master remains private.
- `website`: Python applies the logo watermark without resizing. The untouched master
  remains private.
- Unconfigured destinations have no export route. Provider outputs are never copied
  directly into a publication directory.
- Run metadata stripping after image transformations. Remove supported EXIF, XMP,
  IPTC, comments, thumbnails, and other nonessential metadata; inspect the written
  derivative. If required checks cannot run or fail, mark it non-publishable.
- Metadata stripping does not claim to remove invisible embedded signals. Such signals
  are tracked separately and are not falsely reported as absent.
- A publication record stores destination/platform, public URL or identifier, date,
  production and asset versions, derivative hash, and export-profile version. Do not
  store account credentials.

### 8.2 Build and durable outputs

`build/` is ignored and may contain only outputs proven byte-for-byte reproducible from
versioned inputs, configuration, and pinned tool versions. AI generations, selected
images, final infographics, and publication records are durable project data, never
discarded as build output. If a transformation is not byte-reproducible, its accepted
result is stored as a versioned durable artifact.

## 9. Initial directory contract

### 9.1 Root, temporary files, and cleanup

The project root is controlled: add a root item only when it is declared in this SPEC
and classified in `config/template-manifest.json`. Ignore known reproducible caches
and explicitly designated `tmp/` and `temp/` scratch paths. Do not blanket-ignore
`tests/` or `output/`, which may contain source tests or retained deliverables. An
`output/` path is generated only when its owner classifies it as generated. Preserve
unknown files and deliverables. Content Studio does not automatically delete temporary
files by age/count or apply a “keep latest” rule; cleanup requires a specific approved
target and retention policy.

```text
AGENTS.md, SPEC.md, ReSPEC.md, WHY.md, README.md, CHANGELOG.md, TEMPLATE_BASE.md
config/                         canonical template and project manifests
schemas/common/                 character, item, relationship, asset, provenance
schemas/content/                mini-project, knowledge, infographic production
knowledge/<domain>/<module-id>/ reusable sourced knowledge
assets/characters/<character-id>/ character definitions and permanent references
assets/items/<item-id>/         reusable item definitions and asset references
assets/outfits/<outfit-id>/     shared item compositions/loadouts
assets/relationships/            character-item many-to-many link records
assets/masters/<asset-id>/<version>/            private immutable accepted sources
assets/generations/<generation-id>/             private provenance and image-review.md
assets/discard_candidates/<asset-id>/<version>/  retained unselected sources
projects/<domain>/<project-id>/ isolated mini-project context and production records
projects/<domain>/<project-id>/productions/infographic/exports/ durable derivatives
projects/<domain>/<project-id>/productions/infographic/prompts/ private briefs, reviews, and selected prompts
docs/                           infographic proposal, content, and generated-image review policy
docs/INFOGRAPHIC_PROPOSAL_GUIDELINE.md page-by-page proposal format and internal default workflow
profiles/                       prompt layers and infographic/SNS/website profiles
profiles/prompts/layers/        versioned shared and medium prompt fragments
profiles/exports/               example social and website transformation profiles
schemas/common/                  portable character/item/asset record contracts
schemas/content/                 mini-project/knowledge/infographic record contracts
reference_analysis/transient/   ignored one-time analysis sessions only
build/                          ignored, byte-identical reproducible outputs only
tools/                          validation, prompt resolution, copy-only intake, Python image export, publication records, WHY recording
tests/                          schema, policy, provenance, export and publication gates
AI/README.md                    work-area/reset rules; existing Dev logs are preserved
```

The shared record contracts are versioned JSON Schemas. Human-edited record instances
use YAML with equivalent fields. `tools/validate.py` validates supported schema keywords,
record paths, unique IDs, and cross-record references; Dev/Template roles reject all
character instance paths while Sample allows only its declared fictional data.

The Sample alone has character instance data. Its generated original stays outside any
future public artifact; a watermarked, sanitized derivative may be used in the sample
infographic. Reusable schemas and fictional schema-validation fixtures are not character
records and may exist in Dev/Template tests.

## 10. Validation requirements

Validation must cover manifest/version compatibility; stable unique IDs; resolvable
many-to-many item links; character identity/variant references; Story-core compatibility
fixtures; source and rights provenance; prompt sidecar completeness; immutable masters;
approved/rejected separation; path containment; no raw-master publication; Python
profile behavior; watermark/profile settings; metadata checks; publication records; and
absence of character instance data in Dev and Template artifacts. Intake/export checks
include byte-preserved source hashes, no-overwrite paths, accepted-only source gating,
social resizing/lossy encoding, website dimension preservation, watermark application,
metadata scanner failure behavior, deterministic repeated hashes, and publication
records that resolve only to verified derivatives. Prompt checks include
deterministic layer ordering, required substitution handling, unresolved placeholder
rejection, layer and reference hash verification, and exact-prompt hash verification.
Prompt-review validation also checks brief and selected-prompt hashes; candidate count,
order, and text hashes; rubric weights and score arithmetic; critical-check capping;
revision findings and mapped changes; evaluator metadata; first-pass or best-candidate
selection; prompt-resolution linkage; and that only a `selected_pass` review authorizes
an image-generation record. Template-role validation rejects all private project and
prompt records. Generation provenance also validates project-relative generation-
argument files, parsed values, and SHA-256 hashes.
The generated-image rubric is a required manual review: `tools/validate.py` does not
inspect pixels, count SEUs, recognize chibi proportions, assess character appeal, or
verify the truth of a review report. A report does not replace the owner's acceptance.
All artifact roles include `tools/record_why.py` and a root `WHY.md`. Static review
confirms that the recorder appends only explicit input, preserves prior text, does
nothing on blank input, refuses unsafe WHY targets, and performs no network or Git
operations. Dev WHY history must not appear in Template or Sample.

Tests use synthetic fixtures only and do not invoke image-generation services. Image
generation itself is recorded as external and non-deterministic. Export verification
uses deterministic fixture images and compares repeated output hashes.

## 11. ReSPEC and phases

Each phase updates this SPEC before behavior changes, implements only phase-owned
files, validates and reviews its scoped diff, and reconciles actual status in ReSPEC.
After a validated Dev phase, create one local checkpoint commit containing only that
phase's files. Never push. The public Template and Sample repositories must not be
committed by the agent.

- **Phase 1 — contract and repository boundaries:** complete. Added the master SPEC,
  operating contract, Base compatibility and independent 0.1.0 version manifest,
  project example, artifact boundaries, AI work-area rule, ignore policy, and version
  mirrors. Later implementation phases remain planned.
- **Phase 2 — shared schemas and project catalog:** complete. Added versioned portable
  record schemas, a reference/relationship validator, a deterministic read-only
  mini-project catalog, and synthetic tests for reusable item links and Story extension
  fields. Dev contains no character instance records.
- **Phase 3 — prompt composition and private provenance sidecars:** complete. Added
  deterministic layered resolution, literal substitution, write-once private sidecars,
  exact profile/value/layer/reference hashes, recomposition validation, and synthetic
  coverage. No character instance data was added to Dev.
- **Phase 4 — immutable asset intake and Python export profiles:** complete. Added
  byte-preserving copy-only intake, accepted/discard-candidate storage, provider-linked
  generation records, social JPEG and website PNG watermark profiles, fail-closed PNG/
  JPEG metadata scanning, durable derivative records, and a local post-publication
  recorder. Repeated export hashes match; no network or raw-master publication route
  exists.
- **Phase 5 — Sample character data and capability infographic:** complete. The local
  Sample contains exactly one fictional character, two appearance variants sharing its
  character ID, a reusable clothing item/variant and outfit link, layered prompt
  provenance, private immutable source masters, and a Japanese template-capability
  infographic. Python produced separate website and social derivatives. The Template
  has no character records or images; Template and Sample remain uncommitted.
- **Phase 6 — final cross-artifact validation and ReSPEC:** complete. Three ReSPEC
  loops checked the shared schema/data model, source-to-derivative workflow and privacy/
  version/Git boundaries. Dev, Template, and Sample tests pass independently; each
  role-specific validator passes. No external publication occurred.
- **Phase 7 — prompt archive and review gate:** complete. Added incremental prompt
  candidate archiving, 100-point evaluation records with hard checks and revision links,
  evaluator identity capture, selected prompt hash verification, and a project-level
  gate before image intake. Historical records remain unchanged; no provider calls occur.
- **Phase 8 — Base 0.1.1 WHY lifecycle alignment:** complete. Adopted the human-owned,
  append-only-in-intent lifecycle, explicit user-stated/adopted-reason trigger, and
  shared recorder across Dev, Template, and Sample. Content Studio retains its
  independent v0.1.1 and single declared WHY scope; the Sample aligns to v0.1.1.
  All roles include a generic public placeholder where appropriate, and their
  validators require the root WHY and recorder without exposing Dev history.
- **Phase 9 — static memory-aid infographic standard and fixed visual rubric:** Dev
  contract, documentation, and default prompt profile implemented. The reusable
  Template checkout remains to be reconciled without overwriting its existing local
  changes; Sample's existing image and prompt records remain historical and are not
  retroactively scored.
- **Phase 10 — Base 0.1.1 operational-policy alignment:** completed in Dev. Ported the
  compatible local WHY recorder behavior, root/temporary-file boundaries, AI Reset
  scope, and conversation-log preservation rules. Content Studio's root-only WHY scope
  and independent version remain authoritative; Base's direct-project updater was not
  applied.
- **Phase 11 — fixed image criteria and first-attempt preparation:** completed in Dev.
  The prompt-writing checklist requires the fixed image score and gates; only a passing
  prompt review authorizes generation. The first generation call is treated as the
  intended production attempt, and a gate failure is recorded and reported, not accepted
  as an expected trial.
- **Phase 12 — decision-ready infographic proposals:** completed in Dev. Every proposal
  now states an exact count of at least four page-equivalent SEUs and lists specific
  points, relationships, memory cues, evidence status, and visual placement per page.
  The internal workflow applies this by default without asking the owner to restate it
  or announcing internal checks.
- **Phase 13 — configurable series layout policy:** completed in Dev. Multi-output
  infographic series now default to one fixed orientation, maximum page-to-page layout
  variation, no additional shared design elements, and a required visual handoff to the
  next page. Mini-project settings can override these values. A dedicated prompt profile,
  proposal and review guidance, and deterministic configuration validation support the
  policy without changing the ordinary infographic profile or the v0.1.1 version.
- **Phase 14 — configurable female-character visual defaults:** completed in Dev.
  Female-character defaults now cover explicit adult age/presentation, everyday outfits,
  pants and outerwear exceptions, summer short-sleeve target, and swimming attire. Project
  settings can override individual fields; new prompt profiles include the policy while
  historical profiles remain unchanged. No version bump was made.
