---
name: codex-model-router
description: Guided download, installation, diagnosis, configuration, and recovery for Codex with CC Switch and Codex++. Use when the user wants help installing or understanding CC Switch/Codex++, configuring Codex around those tools, routing through CC Switch safely, enabling Codex++ mainstream setup options, preserving or restoring official OpenAI/ChatGPT login, storing model keys through environment variables, or recovering from broken Codex config.
---

# Codex Model Router

Use this skill as a guided setup and recovery control panel for Codex + CC Switch + Codex++. The target user may not understand how to download, install, configure, or safely combine these tools, and may not want to hand-edit software settings. Lead with the user's goal, explain the safe setup path briefly, run deterministic scripts where appropriate, and verify after every change.

## Default Flow

When the user asks for setup, repair, or "what should I do", run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-model-router/scripts/codex_model_router.py" doctor
```

Then choose one path:

- **Official mode**: keep Codex on OpenAI/ChatGPT login. Use `restore-official` if any third-party provider is active.
- **CC Switch routing**: enable CC Switch's Codex route, then point Codex at the local CC Switch bridge with an environment-variable key.
- **Codex++ setup**: guide installation and mainstream settings, optionally apply the `safe-ui` preset, then restart Codex++ and Codex.
- **Recovery**: list backups, restore a selected backup, and rerun `doctor` plus an optional `codex exec --ephemeral` smoke test.

## User Prompt Recipes

Give users simple prompts they can paste into Codex:

```text
Use $codex-model-router to run a full doctor check and tell me what is unsafe.
```

```text
Use $codex-model-router to tell me how to install Codex, CC Switch, and Codex++ in the right order.
```

```text
Use $codex-model-router to configure Codex through CC Switch for DeepSeek, using DEEPSEEK_API_KEY from my environment.
```

```text
Use $codex-model-router to restore Codex official mode after CC Switch or Codex++ broke my config.
```

## Installation Guidance

When the user needs download/install help, run or summarize:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py install-guide
```

Prefer GitHub Releases from the project repositories. Read [downloads.md](references/downloads.md) for source links and project identity notes.

## Official Login Health

Run:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py status
```

Healthy evidence:

- `auth.exists=True`
- `mode=600`
- `auth_mode=chatgpt` or another official Codex auth mode
- `tokens=True`
- `Routing: provider=openai/default` unless the user intentionally enabled CC Switch

Optional strong proof:

```bash
codex exec --ephemeral --skip-git-repo-check "Return exactly: official-login-ok"
```

Treat output showing `provider: openai` and `official-login-ok` as official login working.

## CC Switch Workflows

Use CC Switch for provider presets, Claude/Codex/Gemini local routing, proxy/failover, MCP, prompts, and skills management. Read [feature-map.md](references/feature-map.md) before explaining feature coverage.

Inspect redacted routing state:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py ccswitch-summary
```

Enable CC Switch takeover for Codex only, after explicit user confirmation:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py enable-ccswitch-codex \
  --confirm enable-ccswitch-codex
```

Point Codex at the local CC Switch bridge. `--base-url` may be omitted; the script uses CC Switch's Codex listen port when it can detect it.

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py enable-ccswitch \
  --model "deepseek-v4-flash" \
  --env-key "DEEPSEEK_API_KEY"
```

Use environment variables for keys:

```bash
export DEEPSEEK_API_KEY="..."
```

Do not write real API keys into `config.toml`, screenshots, reports, or GitHub issues.

Disable CC Switch takeover for Codex only, leaving Claude/Gemini routes alone:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py disable-ccswitch-codex \
  --confirm disable-codex-takeover
```

## Codex++ Workflows

Use BigPizzaV3 Codex++ for launcher/manager, relay profiles, diagnostics, updates, and UI enhancements. Keep the active relay on OpenAI Official when the user only wants UI improvements.

Inspect redacted Codex++ state:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py codexplusplus-status
```

Enable mainstream safe UI enhancements:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py configure-codexplusplus \
  --preset safe-ui \
  --confirm configure-codexplusplus
```

The `safe-ui` preset enables session delete, markdown export, project move, conversation timeline, scroll restore, and native menu placement. It preserves OpenAI Official relay when available. Backups are written outside the skill folder under `~/.codex/runtime/codex-model-router/backups`.

For only the delete-session button:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py enable-codexplusplus-session-delete \
  --confirm enable-codexplusplus-session-delete
```

Restart Codex++ and Codex after changing Codex++ settings so UI injection reloads.

## Restore And Backup

Restore official OpenAI/default mode:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py restore-official
```

List backups:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py backups
```

Restore a selected backup only after the user confirms the exact path:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py restore-backup --backup-dir "<backup-dir>"
```

## Emergency Sidebar Session Archiving

Prefer Codex++'s own session-delete UI. Use direct archiving only when Codex++ UI injection is unavailable or broken:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py sessions --query "<title-or-id>"
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py archive-session \
  --id "<session-id>" \
  --confirm archive-session
```

This backs up `session_index.jsonl` and moves matching session JSONL files into `~/.codex/archived_sessions/<timestamp>/<id>/` without printing session contents.

## Safety Rules

- Never print API keys, OAuth tokens, cookies, authorization headers, or passwords.
- Always run `doctor` or `status` before and after changing config.
- Always rely on script backups before modifying `~/.codex/config.toml`, `~/.codex/auth.json`, `~/.cc-switch/cc-switch.db`, or `~/.codex-session-delete/settings.json`.
- Keep runtime backups out of GitHub. They live under `~/.codex/runtime/codex-model-router/backups`, not inside the shareable skill directory.
- Do not enable CC Switch Codex takeover unless the user explicitly wants model routing through CC Switch.
- Do not change Claude/Gemini/OpenClaw routes when the user asks only about Codex.
- Do not switch Codex++ away from OpenAI Official when the user only wants UI enhancements.
- Treat UI claims as weak evidence; verify through file state and a Codex smoke test.

## References

- Read [downloads.md](references/downloads.md) for GitHub sources and install guidance.
- Read [feature-map.md](references/feature-map.md) before explaining which CC Switch/Codex++ features this skill covers.
- Read [routing-notes.md](references/routing-notes.md) when explaining protocol conversion, local routing, or login preservation.
