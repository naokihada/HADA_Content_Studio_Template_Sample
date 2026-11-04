# Changelog

## [0.1.1] - 2026-11-04

### Added

- Pre-generation prompt briefs, immutable candidate and review archives, evaluator
  metadata, revision evidence, selected prompt text, and hashed generation arguments.
- A configurable project gate requiring prompt review before image generation.
- Legacy prompt records remain unchanged and are not retroactively scored.
- Base 0.1.1 WHY lifecycle rules and the append-only `tools/record_why.py` recorder.

### Changed

- Infographics are static memory aids with at least four slide-equivalent knowledge
  units; practice and quiz content is excluded.
- Added a fixed post-generation image rubric with character, content, layout, memory,
  and technical criteria, plus non-compensating image gates.
- Added the fixed image score and gates to the prompt-writing requirements. Image
  generation now requires a passing prompt review; a below-threshold candidate is kept
  for audit and cannot be used as a throwaway first attempt.
- Added a default infographic proposal policy with an exact page-equivalent count and
  sufficiently detailed, evidence-aware points for every planned page.
- Added configurable multi-output series layout policy: a shared portrait/landscape
  orientation, maximum page-to-page layout variation by default, no additional recurring
  visual elements unless configured, and page-specific handoffs that build anticipation.
- Added configurable female-character visual defaults for adult presentation, dresses and
  one-piece outfits, role-based pants/outerwear exceptions, summer short-sleeve variety,
  and one-piece competitive swimwear.
- Updated the default infographic prompt content for the memory-aid standard while
  keeping its profile and layer version strings aligned at 0.1.1.
- Adopted Base 0.1.1's multiline WHY recorder behavior and its root/temp-file, AI Reset,
  and user-owned conversation-log boundaries, adapted to Content Studio's root-only WHY
  scope and existing `AI/Logs/` location.

## [0.1.0] - 2026-11-02

### Added

- Initial Content Studio contract based on HADA Base 0.1.0.
- Shared character, reusable item, many-to-many association, asset, and provenance
  model designed for Story Studio compatibility.
- Infographic-first production, immutable source assets, Python export profiles,
  publication records, and strict raw-generation publication boundary.
- Configurable sample-character validation and role-isolated test fixtures.
- Separate local Sample demonstration with one stable character identity, chibi
  appearance, reusable outfit links, private prompt/source provenance, and a Japanese
  capability infographic. Sample assets are not included in the reusable Template.
