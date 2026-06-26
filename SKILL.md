---
name: codex-model-router
description: Guided download, installation, feature explanation, configuration, switching, diagnosis, and recovery for Codex with CC Switch and Codex++. Use when the user wants to understand what CC Switch or Codex++ does, choose which one to install, download/install either tool, configure Codex to use domestic/third-party models through CC Switch, configure Codex++ model switching or Codex UI enhancements, switch between official OpenAI login and local routing, or recover from broken Codex config.
---

# Codex Model Router

Use this skill as a guided setup and recovery control panel for Codex + CC Switch + Codex++. The target user may not understand what CC Switch or Codex++ does, how to download/install them, how to configure model switching, or how to safely combine them with official Codex login. Lead by asking which tool or goal the user wants, explain the relevant tool's function briefly, then guide download, installation, configuration, switching, and verification. The desired experience is: the user talks to Codex in natural language, and Codex helps complete software configuration, modification, switching, and official-login recovery.

## Default Flow

When the user asks for setup, installation, repair, or "what should I do", first identify the user's target. If unclear, ask one short question:

```text
你主要想做哪件事：1）用 CC Switch 切换国产/第三方模型；2）用 Codex++ 做模型切换和 Codex 增强；3）两个都装；4）恢复官方登录/官方模式？
```

Then explain the relevant tool:

- **CC Switch**: for routing Codex/Claude/Gemini through providers such as DeepSeek, domestic models, or other third-party model services. It helps switch model providers and manage local routing.
- **Codex++**: for Codex desktop management, relay/model switching, diagnostics, updates, and UI enhancements such as session delete, markdown export, project move, timeline, scroll restore, and native menu placement.
- **Official mode**: for keeping or restoring OpenAI/ChatGPT login and default Codex routing.

For download/install guidance, run the targeted install guide:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-model-router/scripts/codex_model_router.py" install-guide --target all
```

Use `--target cc-switch` when the user chose CC Switch, and `--target codex-plus-plus` when the user chose Codex++.

Before and after configuration changes, run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-model-router/scripts/codex_model_router.py" doctor
```

Then choose one path:

- **Official mode**: keep or restore Codex on OpenAI/ChatGPT login. Use `restore-official` if any third-party provider is active and the user wants official mode.
- **CC Switch routing**: guide CC Switch installation, provider creation, environment-variable key storage, Codex route enablement, then point Codex at the local CC Switch bridge.
- **Codex++ setup**: guide Codex++ installation, model/relay choice, mainstream enhancement settings, optionally apply the `safe-ui` preset, then restart Codex++ and Codex.
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
使用 codex-model-router，先问我想用 CC Switch 还是 Codex++，再带我下载安装和配置。
```

```text
使用 codex-model-router，介绍 CC Switch 和 Codex++ 分别能做什么，然后让我选择。
```

```text
Use $codex-model-router to configure Codex through CC Switch for DeepSeek or another domestic model, using an environment variable for the key.
```

```text
使用 codex-model-router，带我配置 Codex++ 的模型切换和常用 Codex 增强功能。
```

```text
Use $codex-model-router to restore Codex official mode after CC Switch or Codex++ broke my config.
```

## Installation Guidance

When the user needs download/install help, run or summarize:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py install-guide
```

Targeted guides:

```bash
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py install-guide --target cc-switch
python3 ~/.codex/skills/codex-model-router/scripts/codex_model_router.py install-guide --target codex-plus-plus
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

Use CC Switch when the user wants Codex/Claude/Gemini to switch domestic or third-party models, especially DeepSeek-style routing. Explain that CC Switch is mainly for provider/model routing, proxy/failover, MCP, prompts, and skills management. Read [feature-map.md](references/feature-map.md) before explaining feature coverage.

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

Use BigPizzaV3 Codex++ when the user wants Codex desktop management, model/relay switching, diagnostics, updates, or UI enhancements. Explain that it can help switch models and enable Codex improvements such as session delete, export, project move, timeline, scroll restore, and native menu placement. Keep the active relay on OpenAI Official when the user only wants UI improvements.

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
