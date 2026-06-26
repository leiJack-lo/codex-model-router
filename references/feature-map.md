# Feature Map

Use this map to explain what the skill covers and what remains a UI/manual step.

## CC Switch

Mainstream features to guide:

- Provider management for Claude, Codex, Gemini, and OpenClaw-style routes.
- Local routing / live takeover for Codex, Claude, and Gemini.
- Codex DeepSeek-style routing through a local Responses-compatible bridge.
- Proxy/failover status inspection.
- MCP, prompts, and skills management as CC Switch UI concepts.
- Official Codex login preservation and rollback.

What the script can do safely:

- Detect CC Switch database/settings/log presence.
- Print redacted provider/proxy summary.
- Enable or disable only the Codex proxy/takeover row.
- Write Codex `config.toml` to point at the local CC Switch bridge using `env_key`.
- Restore official Codex routing.
- Print clear manual next steps for provider creation and API key storage.

What remains UI/manual unless the user explicitly requests deeper automation:

- Creating provider records with real API keys.
- Editing provider endpoint URLs.
- Editing MCP/prompt/skill content inside CC Switch.
- Changing Claude/Gemini routes during a Codex-only task.

For public README wording, say "guided setup" rather than "fully automatic setup" for CC Switch provider creation, because real provider keys and endpoint choices belong in CC Switch UI or environment variables.

## BigPizzaV3 Codex++

Mainstream features to guide:

- Launcher/manager and app update flow.
- Relay profiles for official OpenAI or third-party providers.
- Diagnostics and backups.
- UI enhancements: session delete, markdown export, project move, conversation timeline, scroll restore, native menu placement.
- Advanced UI additions: thread id badge, conversation view, Zed remote open, upstream worktree create.

What the script can do safely:

- Detect Codex++ settings/status files.
- Print redacted enhancement and relay state.
- Apply `delete-only`, `safe-ui`, or `power-ui` enhancement presets.
- Preserve OpenAI Official relay while enabling UI enhancements.
- Back up Codex++ settings before edits.

What should remain UI/manual unless explicitly requested:

- Storing relay API keys in Codex++ settings.
- Enabling mobile control or other remote-control features.
- Installing arbitrary user scripts.
- Mixing BigPizzaV3 Codex++ with the b-nnett tweak system without a clear reason.

## b-nnett Codex++

This is a separate tweak system for Codex desktop. Use it only when the user specifically wants tweak-store style patching. It can modify UI, add settings pages, run main-process code, and use native OS features, so treat it as higher risk than BigPizzaV3's manager flow.
