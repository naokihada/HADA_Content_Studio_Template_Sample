# Shared Studio Data Model

The portable core is shared with a future Story Studio consumer. Content and Story
schemas remain separate extensions around the same IDs and asset references.

## Core records

- `CharacterDefinition`: stable identity anchors and canonical reference-asset versions.
- `AppearanceVariant`: a view of the same character with a different proportion, style,
  outfit, or scene treatment. It keeps the parent character ID.
- `ItemDefinition`: an independently reusable vehicle, weapon, clothing item, accessory,
  or prop.
- `ItemVariant`: a specific version of one item, such as a seasonal uniform or a
  customized motorcycle. Its parent item remains stable across variants.
- `CharacterItemLink`: a junction record joining one character to one item with a role
  such as `wears`, `rides`, or `wields`. An optional item variant must belong to the
  linked parent item. Many links may point to the same item, so one uniform can be
  shared by multiple characters.
- `Outfit`: a named loadout composed from item IDs. It may be assigned to many
  characters; each component may select an item variant, and individual tailoring can
  be represented without duplicating the shared item.
- `AssetReference`: a versioned relative path and SHA-256 with role, visibility, origin,
  and rights information.

Story can load these records unchanged and add its own series, scene, timeline, canon,
and continuity data under `extensions.story` or Story-specific records. Core schemas
allow explicit extensions so Content does not need to predict all Story fields.

## Content records

Each mini-project uses `projects/<domain>/<project-id>/project.yaml` as its summary and
reference index. `domain` and tags are labels, not separate schemas. Reusable sourced
knowledge is stored under `knowledge/<domain>/<module-id>/knowledge.yaml`; audience-
specific adaptations stay in the project.

For a multi-output infographic series, the project may set
`extensions.content_studio.series_layout` with an orientation (`portrait` or `landscape`),
layout variation (`maximum` or `custom` with `layout_variation_details`), any explicitly
permitted additional shared elements, and whether next-page anticipation is required,
optional, or disabled. The template defaults are one fixed orientation, maximum layout
variation, no additional shared elements, and required page-to-page anticipation. These
values are series guidance; they do not change character identity, content accuracy,
readability, or publication requirements.

Female-character visual defaults are optionally set under
`extensions.content_studio.character_visual_defaults.female_character`. Any provided
fields override the template defaults independently; omitted fields inherit the
defaults. Supported settings include age/adult status, presentation, ordinary outfit,
allowed pants and outerwear contexts, the open-front outerwear exception, the target
fraction of summer short-sleeve looks, and the default swimming outfit. The reusable
example sets these to an adult age of 18, a neat/elegant female university-student
presentation, dress or one-piece outfits, the specified role-based clothing exceptions,
about one-third summer short-sleeve looks, and a one-piece competitive swimsuit for
swimming. An adult setting cannot be assigned to an age below 18.

The first production kind is `infographic`. A production points to knowledge, character,
item, profile, and asset IDs. Final publication records point to the exact transformed
asset version and hash. Private prompt-resolution sidecars retain the rendered prompt,
ordered versioned template layers, exact substitutions, source hashes, and referenced
asset versions for an infographic or compatible future Story work item.

- `PromptReview`: the agreed brief hash, fixed rubric, append-only candidate text and
  evaluation evidence, revision links, evaluator metadata, and selected prompt hash. It
  links to the matching prompt resolution before image generation.

An `ImageGeneration` record binds an immutable PNG/JPEG source master to its prompt,
work item, provider details, optional hashed generation-argument file, reviewer,
disposition, and SHA-256. The generated image's fixed rubric review is saved as
`assets/generations/<generation-id>/image-review.md` beside its provenance sidecar.
An `ImageDerivative`
record binds one accepted generation to a destination profile, hashed watermark, output
dimensions, toolchain, and metadata-scan result. A `PublicationRecord` can refer only
to a derivative that passed the configured profile and metadata checks.

## Artifact boundaries

Dev and Template contain schema definitions, tooling, and synthetic test fixtures only;
they contain no persistent character records. Only Sample has fictional character
instances. Tests create ephemeral data in temporary directories.
