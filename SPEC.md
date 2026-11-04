# HADA Content Studio Template — Master Specification

**Specification status:** Approved implementation plan
**Specification version:** 0.1.1
**Template version:** 0.1.1
**Base compatibility:** minimum 0.1.0; tested 0.1.1
**Status date:** 2026-11-03
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
- Automatic deletion by age/count. Only a specifically selected one-time analysis
  session can be explicitly discarded.

## 3. Base relationship and versioning

This is a specialized template with its own identity and version. `config/template-manifest.json`
is the source for `hada-content-studio-template` version `0.1.1`; Base compatibility is
separate and records minimum Base version `0.1.0` and tested Base version `0.1.1`.
Schema and content-data
versions are independent. The Base direct-template updater is not assumed to update
this specialized template.

## 4. Artifact boundaries and character-data rule

- **Dev:** source code, schemas, tests, and release preparation. Local workspaces may also contain private project-owner context, archives, or unreviewed assets; these stay outside reusable packages.
- **Template:** reusable schemas, tools, policies, and empty examples only. Contains no
  character instance records or character images.
- **Sample:** fictional `Cute Elf Girl` data and assets plus a tutorial infographic
  explaining template capabilities. Sample is local and must not be committed by the
  agent. Future publication must use only approved transformed derivatives; generated
  originals and internal prompt/provenance records are excluded from publication.

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
placeholder only when the file is missing and nonblank reason text was supplied. Blank
input makes no change. It refuses a symlink or non-file `WHY.md`. The owner may also
edit the file directly. Preserve the owner's wording and do not invent supporting
details, attribution, or historical dates.

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

## 5. Portable Studio Core

Core entities use stable IDs, explicit schema versions, source/rights metadata, and
forward-compatible optional extensions. Markdown is the human-readable content format;
small YAML/JSON records hold relationships and machine-checked fields. A database is
not required for 0.1.1.

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

```text
AGENTS.md, SPEC.md, ReSPEC.md, README.md, CHANGELOG.md, TEMPLATE_BASE.md
config/                         canonical template and project manifests
schemas/common/                 character, item, relationship, asset, provenance
schemas/content/                mini-project, knowledge, infographic production
knowledge/<domain>/<module-id>/ reusable sourced knowledge
assets/characters/<character-id>/ character definitions and permanent references
assets/items/<item-id>/         reusable item definitions and asset references
assets/outfits/<outfit-id>/     shared item compositions/loadouts
assets/relationships/            character-item many-to-many link records
assets/masters/<asset-id>/<version>/            private immutable accepted sources
assets/generations/<generation-id>/             private generation provenance
assets/discard_candidates/<asset-id>/<version>/  retained unselected sources
projects/<domain>/<project-id>/ isolated mini-project context and production records
projects/<domain>/<project-id>/productions/infographic/exports/ durable derivatives
profiles/                       prompt layers and infographic/SNS/website profiles
profiles/prompts/layers/        versioned shared and medium prompt fragments
profiles/exports/               example social and website transformation profiles
schemas/common/                  portable character/item/asset record contracts
schemas/content/                 mini-project/knowledge/infographic record contracts
reference_analysis/transient/   ignored one-time analysis sessions only
build/                          ignored, byte-identical reproducible outputs only
tools/                          validation, prompt resolution, copy-only intake, Python image export, publication records
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
  Sample exercises one fictional identity, same-ID appearance variants, reusable items,
  prompt provenance, protected source assets, and a capability infographic. The
  reusable Template remains free of character records and image files. Template and
  Sample working trees are local and uncommitted.
- **Phase 6 — final cross-artifact validation and ReSPEC:** complete. Three ReSPEC
  loops checked the data contract, prompt/media lifecycle, and privacy/version/Git
  boundaries. Dev, Template, and Sample tests and role-specific validators pass. No
  external publication occurred.- **Phase 6 — final cross-artifact validation and ReSPEC:** complete.
