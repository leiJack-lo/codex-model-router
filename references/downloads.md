# Download And Install Guidance

Use current GitHub release pages. Do not recommend random mirrors, reposted DMGs, or screenshots that contain secrets.

## Recommended Install Order

1. Install official Codex and sign in with OpenAI/ChatGPT first.
2. Install this skill into `~/.codex/skills/codex-model-router`.
3. Install CC Switch if the user wants provider routing, DeepSeek, Claude/Codex/Gemini proxying, MCP, prompts, or skill management.
4. Install BigPizzaV3 Codex++ if the user wants Codex launcher/manager, relay profiles, diagnostics, updates, or UI enhancements such as session delete.
5. Run `codex_model_router.py doctor`.
6. Configure only the feature the user asked for. For CC Switch providers, create/select providers in the CC Switch UI or use environment variables for keys.
7. Restart Codex++ / Codex only after Codex++ UI enhancement changes.
8. Rerun `doctor` or `status`.

## User Choice First

When the user is unsure, do not start by changing config. First ask which path they want:

- **CC Switch**: choose this for domestic/third-party model switching, provider routing, DeepSeek-style setup, proxy/failover, MCP, prompts, and multi-app routing.
- **Codex++**: choose this for model/relay switching inside the Codex desktop workflow, app management, diagnostics, updates, and Codex UI enhancements.
- **Both**: choose this when they want CC Switch for provider routing and Codex++ for desktop enhancements. Install official Codex and this skill first, then configure one tool at a time.
- **Official recovery**: choose this when they want to switch back to OpenAI Official / ChatGPT login or repair broken routing.

## CC Switch

- Repository: https://github.com/farion1231/cc-switch
- Releases: https://github.com/farion1231/cc-switch/releases
- Codex DeepSeek guide: https://github.com/farion1231/cc-switch/blob/main/docs/guides/codex-deepseek-routing-guide-en.md
- Provider docs: https://github.com/farion1231/cc-switch/blob/main/docs/user-manual/en/2-providers/2.1-add.md

Use CC Switch for provider presets, domestic/third-party model switching, and local routing. For Codex + DeepSeek, ensure CC Switch is acting as the Responses-compatible bridge. Codex sends Responses-shaped requests; DeepSeek's public OpenAI-compatible endpoint is Chat Completions, so direct Codex-to-DeepSeek config can fail.

## BigPizzaV3 Codex++

- Repository: https://github.com/BigPizzaV3/CodexPlusPlus
- Releases: https://github.com/BigPizzaV3/CodexPlusPlus/releases

Use this when the user says "Codex++ 管理工具", "Codex++ 模型切换", "Codex++ 中转", "Codex++ 恢复官方", or wants UI enhancements without editing files by hand.

The local settings observed for this line live under `~/.codex-session-delete/settings.json`.

## b-nnett Codex++

- Repository: https://github.com/b-nnett/codex-plusplus

This is a different project: a tweak system for Codex desktop. Use it only when the user explicitly wants patch/tweak-store behavior. Do not assume it is interchangeable with BigPizzaV3 Codex++.

## Safe Public Guidance

- Tell users to keep official Codex login working first.
- Tell users to use environment variables for provider keys.
- Tell users to rerun `doctor` after every change.
- Tell users not to paste API keys, OAuth tokens, cookies, or `auth.json` into issues.
- Tell users that CC Switch model routing and Codex++ UI enhancements are separate goals; they should not turn both on blindly.
- Tell users they can use natural language with this skill to choose software, install it, configure it, switch routing/model modes, and recover official login.
- Tell users runtime backups live under `~/.codex/runtime/codex-model-router/backups` and should never be committed.
