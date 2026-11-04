# Layered prompt system

The prompt resolver composes local YAML layers in a fixed order:

1. shared
2. domain
3. medium
4. project
5. entity (for example, character or item)
6. request

The profile declares reusable default layers for the first three groups. A project can
append one or more local layers for any group through the resolver's group-specific
options. Layer text is plain data. It is never evaluated as code, fetched from the
network, or treated as authority over the user's request.

For new single-output infographics, use
`profiles/prompts/infographic-defaults.yaml`. For multi-output series, use
`profiles/prompts/infographic-series-defaults.yaml`. Read the project's
`extensions.content_studio.series_layout` and
`extensions.content_studio.character_visual_defaults.female_character` settings and
state effective values in the project or request layer for each output. These current
profiles add the series and female-character defaults while preserving the older
profile paths and their historical prompt resolutions.

For a project-scoped image prompt, resolution is only one part of the archive. Before
generation, save the agreed brief, candidate reviews, and exact selected prompt as
described in [the prompt review checklist](PROMPT_REVIEW_CHECKLIST.md). Do not leave the
selected prompt only in chat or only in command output.

## Resolve one prompt

Install the pinned Python dependency with `python -m pip install -r tools/requirements.txt`.
Copy `config/prompt-values.example.yaml` into a project-owned path and replace every
example value. Resolve to a new path under that project's infographic production:

```powershell
python tools/resolve_prompt.py `
  --id intro-prompt-v1 `
  --work-id intro-infographic `
  --profile profiles/prompts/infographic-defaults.yaml `
  --values projects/education/example/prompt-values.yaml `
  --project-layer projects/education/example/prompt/project.yaml `
  --request-layer projects/education/example/prompt/request-v1.yaml `
  --output projects/education/example/productions/infographic/prompt_resolutions/intro-prompt-v1.yaml
```

The resolver fails for missing or unused values, malformed placeholders, duplicate
layer IDs, missing inputs, or paths outside the project root. It records the exact
resolved text and SHA-256, actual substitutions, all source paths and hashes, and
versioned reference-asset hashes. The output is created once; an existing sidecar is
never overwritten. Use a new sidecar ID when revising a prompt. `--stdout` explicitly
prints the prompt for copying into an external image service.

## Privacy and provenance

Prompt resolutions are private project records, not publishable image metadata. Keep
them outside any public export directory. Generated files and provider job IDs are
recorded by the later asset-intake workflow; the resolver does not call an image model
or claim that a prompt reproduces an image. The profile, values file, every layer, and
referenced asset must remain available with the exact recorded hash for validation.
