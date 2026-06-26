# codex-model-router

A Codex skill for people who want to use **CC Switch** and **Codex++** without hand-editing fragile Codex configuration.

The goal is simple: let Codex guide the download, installation, diagnosis, setup, and recovery flow for:

- official Codex / OpenAI login
- CC Switch provider routing
- Codex++ installation and UI enhancement setup
- safe rollback when local configuration gets messy

It is not a replacement for CC Switch or Codex++. It is a guided setup and recovery layer around them.

## Why this exists

CC Switch, Codex++, and official Codex configuration are useful, but they can become confusing when used together.

Common problems:

- You want CC Switch for DeepSeek or other provider routing.
- You want Codex++ for launcher, diagnostics, updates, relay profiles, or UI enhancements.
- You still want official Codex / OpenAI login to keep working.
- You do not want to open several apps and manually guess which setting changed what.
- You are new to CC Switch or Codex++ and do not know the safe install/config order.

This skill turns those tasks into Codex prompts and deterministic checks.

## What it can help with

- Print a practical install guide for Codex, CC Switch, Codex++, and this skill.
- Diagnose Codex auth, model provider, CC Switch state, and Codex++ state with redacted output.
- Explain which parts should be configured in the CC Switch UI and which parts can be configured by script.
- Route Codex through a local CC Switch bridge using an environment variable for the provider key.
- Inspect and apply safe Codex++ UI enhancement presets.
- Restore official/default Codex routing when configuration gets messy.
- Create backups before local configuration changes.

## Install

Clone or download this repository, then place the skill folder here:

```bash
mkdir -p ~/.codex/skills
cp -R codex-model-router ~/.codex/skills/
```

Restart Codex so it reloads local skills.

Then ask Codex:

```text
Use $codex-model-router to run doctor and guide my CC Switch / Codex++ setup.
```

## First commands

Run the install guide:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py install-guide
```

Run a redacted health check:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py doctor
```

Show current Codex auth/routing status:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py status
```

## Example prompts

```text
Use $codex-model-router to tell me how to install Codex, CC Switch, and Codex++ in the right order.
```

```text
Use $codex-model-router to check whether my Codex, CC Switch, and Codex++ configuration is safe.
```

```text
Use $codex-model-router to help me configure CC Switch for Codex, but keep API keys in environment variables.
```

```text
Use $codex-model-router to restore official Codex mode after my local routing config got messy.
```

## Safety model

- Do not paste API keys, OAuth tokens, cookies, `auth.json`, or private config dumps into issues.
- Provider keys should live in environment variables, not in public screenshots or repository files.
- The script prints redacted summaries and avoids dumping secret fields.
- Backups are written outside the shareable skill folder under `~/.codex/runtime/codex-model-router/backups`.
- CC Switch provider creation with real API keys should normally happen in CC Switch UI or through environment variables.

## Related projects

- CC Switch: <https://github.com/farion1231/cc-switch>
- BigPizzaV3 Codex++: <https://github.com/BigPizzaV3/CodexPlusPlus>
- b-nnett Codex++ tweak system: <https://github.com/b-nnett/codex-plusplus>

These are separate projects. This skill only helps you reason about and safely configure a local Codex setup around them.
