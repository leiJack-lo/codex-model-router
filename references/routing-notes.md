# Routing Notes

## Official OpenAI Login

Codex official login normally uses `~/.codex/auth.json` with OAuth token fields and `~/.codex/config.toml` without a third-party `model_provider` override. A healthy smoke test shows `provider: openai` in `codex exec` startup output.

## CC Switch / DeepSeek

Codex uses the OpenAI Responses API. DeepSeek's public OpenAI-compatible API is Chat Completions, not Responses. Therefore, a direct Codex provider pointed at `https://api.deepseek.com` can fail with 404 or unsupported-model errors. Use a local bridge such as CC Switch that accepts Codex's Responses-shaped calls and translates them to the downstream provider.

Recommended Codex config shape for a local bridge:

```toml
model_provider = "ccswitch"
model = "deepseek-v4-flash"

[model_providers.ccswitch]
name = "CC Switch DeepSeek"
base_url = "http://127.0.0.1:<port>/v1"
wire_api = "responses"
env_key = "DEEPSEEK_API_KEY"
```

The value of `DEEPSEEK_API_KEY` belongs in the environment, not in this file.

## CC Switch Claude / Codex / Gemini Routing

CC Switch stores cross-app routing state in its local SQLite database. For a safe read-only overview, inspect only:

- `proxy_config`: `app_type`, enable flags, live takeover flag, listen address/port, failover flag.
- `providers`: `app_type`, `name`, `category`, `provider_type`, current flag, failover flag.
- `provider_endpoints`: endpoint counts only.

Avoid printing `settings_config` or raw endpoint URLs in user-facing reports, because they can contain credentials, private gateway hosts, or account-specific details.

To keep Claude routed through CC Switch while restoring official Codex login, change only `proxy_config` rows where `app_type='codex'`. Do not modify Claude, Claude Desktop, Gemini, or OpenClaw provider rows during a Codex-only recovery.

## Codex++ Risk

Codex++ tools can enhance UI and session workflows, but they may depend on Codex desktop internals or injected scripts. After Codex updates, verify official login, plugin availability, and model provider state before assuming the enhancement layer is healthy.

For the common "delete unwanted sessions from the left sidebar" workflow, prefer enabling Codex++'s own `codexAppSessionDelete` UI enhancement while keeping its relay selection on an official/OpenAI profile. Use direct `session_index.jsonl` archiving only as an emergency fallback when Codex++ UI injection is unavailable or broken.

Observed BigPizzaV3 Codex++ settings live under `~/.codex-session-delete/settings.json`. Relevant non-secret fields include:

- `enhancementsEnabled`: master switch for UI enhancements.
- `codexAppSessionDelete`: session delete button capability.
- `activeRelayId` and `relayProfiles`: can unexpectedly switch Codex routing if left on a DeepSeek/custom profile.

When the user's goal is UI enhancement rather than model routing, set `enhancementsEnabled=true`, `codexAppSessionDelete=true`, and keep `activeRelayId` on an official/OpenAI relay profile.
