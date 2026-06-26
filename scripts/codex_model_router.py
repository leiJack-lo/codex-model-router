#!/usr/bin/env python3
"""Manage Codex model routing and safe recovery without exposing secrets."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import stat
import sys
from datetime import datetime
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
CONFIG_PATH = CODEX_HOME / "config.toml"
AUTH_PATH = CODEX_HOME / "auth.json"
SESSION_INDEX_PATH = CODEX_HOME / "session_index.jsonl"
SESSIONS_PATH = CODEX_HOME / "sessions"
ARCHIVED_SESSIONS_PATH = CODEX_HOME / "archived_sessions"
STATE_ROOT = CODEX_HOME / "runtime" / "codex-model-router"
LEGACY_SKILL_STATE = CODEX_HOME / "skills" / "codex-model-router" / "state"
CODEX_PLUSPLUS_HOME = Path.home() / ".codex-session-delete"
CODEX_PLUSPLUS_SETTINGS_PATH = CODEX_PLUSPLUS_HOME / "settings.json"
CODEX_PLUSPLUS_STATUS_PATH = CODEX_PLUSPLUS_HOME / "latest-status.json"


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_toml(path: Path) -> dict:
    if not path.exists() or tomllib is None:
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def auth_summary() -> dict:
    summary = {
        "path": str(AUTH_PATH),
        "exists": AUTH_PATH.exists(),
        "mode": None,
        "auth_mode": None,
        "has_tokens": False,
        "has_openai_api_key_entry": False,
        "last_refresh": None,
    }
    if not AUTH_PATH.exists():
        return summary
    summary["mode"] = oct(stat.S_IMODE(AUTH_PATH.stat().st_mode))[2:]
    try:
        data = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        summary["error"] = f"unreadable auth json: {exc}"
        return summary
    tokens = data.get("tokens") if isinstance(data, dict) else None
    summary["auth_mode"] = data.get("auth_mode") if isinstance(data, dict) else None
    summary["last_refresh"] = data.get("last_refresh") if isinstance(data, dict) else None
    summary["has_tokens"] = isinstance(tokens, dict) and bool(tokens.get("access_token") and tokens.get("refresh_token"))
    summary["has_openai_api_key_entry"] = isinstance(data, dict) and "OPENAI_API_KEY" in data
    return summary


def routing_summary() -> dict:
    config = load_toml(CONFIG_PATH)
    providers = config.get("model_providers", {}) if isinstance(config.get("model_providers"), dict) else {}
    ccswitch = providers.get("ccswitch", {}) if isinstance(providers.get("ccswitch"), dict) else {}
    env_key = ccswitch.get("env_key")
    return {
        "config_path": str(CONFIG_PATH),
        "config_exists": CONFIG_PATH.exists(),
        "provider": config.get("model_provider"),
        "model": config.get("model"),
        "has_ccswitch_provider": bool(ccswitch),
        "ccswitch_base_url": ccswitch.get("base_url"),
        "ccswitch_wire_api": ccswitch.get("wire_api"),
        "ccswitch_env_key": env_key,
        "ccswitch_env_present": bool(env_key and os.environ.get(str(env_key))),
    }


def ecosystem_summary() -> dict:
    return {
        "cc_switch": {
            "db_exists": (Path.home() / ".cc-switch" / "cc-switch.db").exists(),
            "settings_exists": (Path.home() / ".cc-switch" / "settings.json").exists(),
            "log_exists": (Path.home() / ".cc-switch" / "logs" / "cc-switch.log").exists(),
            "desktop_support_exists": (Path.home() / "Library" / "Application Support" / "com.ccswitch.desktop").exists(),
        },
        "codex_plus_plus": {
            "config_dir_exists": (Path.home() / ".config" / "Codex++").exists(),
            "session_delete_settings_exists": CODEX_PLUSPLUS_SETTINGS_PATH.exists(),
            "codex_backups_count": len(list((CODEX_HOME / "backups").glob("codex-plus-live-*"))) if (CODEX_HOME / "backups").exists() else 0,
        },
    }


def ccswitch_db_path() -> Path:
    return Path.home() / ".cc-switch" / "cc-switch.db"


def ccswitch_proxy_rows() -> list[dict]:
    db_path = ccswitch_db_path()
    if not db_path.exists():
        return []
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            "select app_type, proxy_enabled, enabled, live_takeover_active, listen_address, listen_port, auto_failover_enabled from proxy_config order by app_type"
        ).fetchall()
    except sqlite3.Error:
        rows = []
    finally:
        con.close()
    return [dict(row) for row in rows]


def ccswitch_codex_base_url(default_port: int = 15721) -> str:
    for row in ccswitch_proxy_rows():
        if row.get("app_type") == "codex":
            address = row.get("listen_address") or "127.0.0.1"
            port = row.get("listen_port") or default_port
            return f"http://{address}:{port}/v1"
    return f"http://127.0.0.1:{default_port}/v1"


def load_json_file(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_json_file(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def codexplusplus_settings_summary() -> dict:
    settings = load_json_file(CODEX_PLUSPLUS_SETTINGS_PATH)
    status_data = load_json_file(CODEX_PLUSPLUS_STATUS_PATH)
    profiles = settings.get("relayProfiles") if isinstance(settings.get("relayProfiles"), list) else []
    active_id = settings.get("activeRelayId")
    active_profile = next((p for p in profiles if isinstance(p, dict) and p.get("id") == active_id), None)
    official_profiles = [
        {"id": p.get("id"), "name": p.get("name")}
        for p in profiles
        if isinstance(p, dict) and (p.get("relayMode") == "official" or "official" in str(p.get("name", "")).casefold())
    ]
    return {
        "settings_path": str(CODEX_PLUSPLUS_SETTINGS_PATH),
        "settings_exists": CODEX_PLUSPLUS_SETTINGS_PATH.exists(),
        "status": status_data.get("status"),
        "helper_port": status_data.get("helper_port"),
        "codex_app": status_data.get("codex_app"),
        "enhancements_enabled": settings.get("enhancementsEnabled"),
        "session_delete_enabled": settings.get("codexAppSessionDelete"),
        "markdown_export_enabled": settings.get("codexAppMarkdownExport"),
        "project_move_enabled": settings.get("codexAppProjectMove"),
        "conversation_timeline_enabled": settings.get("codexAppConversationTimeline"),
        "relay_profiles_enabled": settings.get("relayProfilesEnabled"),
        "launch_mode": settings.get("launchMode"),
        "active_relay_id": active_id,
        "active_relay_name": active_profile.get("name") if isinstance(active_profile, dict) else None,
        "active_relay_mode": active_profile.get("relayMode") if isinstance(active_profile, dict) else None,
        "official_profiles": official_profiles,
    }


def codexplusplus_status(args: argparse.Namespace) -> int:
    summary = codexplusplus_settings_summary()
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Codex++ settings: exists={summary['settings_exists']} path={summary['settings_path']}")
        print(f"Runtime: status={summary['status']} helper_port={summary['helper_port']} codex_app={summary['codex_app']}")
        print(
            f"Enhancements: master={summary['enhancements_enabled']} session_delete={summary['session_delete_enabled']} "
            f"markdown_export={summary['markdown_export_enabled']} project_move={summary['project_move_enabled']} timeline={summary['conversation_timeline_enabled']}"
        )
        print(
            f"Relay: profiles_enabled={summary['relay_profiles_enabled']} launch_mode={summary['launch_mode']} "
            f"active={summary['active_relay_name'] or summary['active_relay_id']} mode={summary['active_relay_mode']}"
        )
        if summary["official_profiles"]:
            names = ", ".join(f"{p['name']}({p['id']})" for p in summary["official_profiles"])
            print(f"Official relay profiles: {names}")
    return 0


def enable_codexplusplus_session_delete(args: argparse.Namespace) -> int:
    if args.confirm != "enable-codexplusplus-session-delete":
        print("Refusing to edit Codex++ settings without --confirm enable-codexplusplus-session-delete", file=sys.stderr)
        return 2
    settings = load_json_file(CODEX_PLUSPLUS_SETTINGS_PATH)
    if not settings:
        print(f"Codex++ settings not found or unreadable: {CODEX_PLUSPLUS_SETTINGS_PATH}", file=sys.stderr)
        return 2
    backup_file(CODEX_PLUSPLUS_SETTINGS_PATH, "codexplusplus_settings_before_session_delete_enable")
    settings["enhancementsEnabled"] = True
    settings["codexAppSessionDelete"] = True
    if args.preserve_official_relay:
        profiles = settings.get("relayProfiles") if isinstance(settings.get("relayProfiles"), list) else []
        official = next(
            (
                p
                for p in profiles
                if isinstance(p, dict) and (p.get("relayMode") == "official" or "official" in str(p.get("name", "")).casefold())
            ),
            None,
        )
        if official and official.get("id"):
            settings["activeRelayId"] = official["id"]
        settings["providerSyncLastSelectedProvider"] = "openai"
        settings["providerSyncSavedProviders"] = ["openai"]
    save_json_file(CODEX_PLUSPLUS_SETTINGS_PATH, settings)
    print("Enabled Codex++ session delete enhancement.")
    if args.preserve_official_relay:
        print("Preserved official/OpenAI relay selection to avoid changing Codex model routing.")
    print("Restart Codex++ / Codex app for UI injection changes to take effect.")
    return 0


CODEX_PLUSPLUS_PRESETS = {
    "delete-only": {
        "codexAppSessionDelete": True,
    },
    "safe-ui": {
        "codexAppSessionDelete": True,
        "codexAppMarkdownExport": True,
        "codexAppProjectMove": True,
        "codexAppConversationTimeline": True,
        "codexAppThreadScrollRestore": True,
        "codexAppNativeMenuPlacement": True,
    },
    "power-ui": {
        "codexAppSessionDelete": True,
        "codexAppMarkdownExport": True,
        "codexAppProjectMove": True,
        "codexAppConversationTimeline": True,
        "codexAppThreadIdBadge": True,
        "codexAppConversationView": True,
        "codexAppThreadScrollRestore": True,
        "codexAppZedRemoteOpen": True,
        "zedRemoteProjectRegistryEnabled": True,
        "codexAppUpstreamWorktreeCreate": True,
        "codexAppNativeMenuPlacement": True,
    },
}


def configure_codexplusplus(args: argparse.Namespace) -> int:
    if args.confirm != "configure-codexplusplus":
        print("Refusing to edit Codex++ settings without --confirm configure-codexplusplus", file=sys.stderr)
        return 2
    settings = load_json_file(CODEX_PLUSPLUS_SETTINGS_PATH)
    if not settings:
        print(f"Codex++ settings not found or unreadable: {CODEX_PLUSPLUS_SETTINGS_PATH}", file=sys.stderr)
        return 2
    preset = CODEX_PLUSPLUS_PRESETS[args.preset]
    backup_file(CODEX_PLUSPLUS_SETTINGS_PATH, f"codexplusplus_settings_before_{args.preset}")
    settings["enhancementsEnabled"] = True
    for key, value in preset.items():
        settings[key] = value
    if args.preserve_official_relay:
        profiles = settings.get("relayProfiles") if isinstance(settings.get("relayProfiles"), list) else []
        official = next(
            (
                p
                for p in profiles
                if isinstance(p, dict) and (p.get("relayMode") == "official" or "official" in str(p.get("name", "")).casefold())
            ),
            None,
        )
        if official and official.get("id"):
            settings["activeRelayId"] = official["id"]
        settings["providerSyncLastSelectedProvider"] = "openai"
        settings["providerSyncSavedProviders"] = ["openai"]
    save_json_file(CODEX_PLUSPLUS_SETTINGS_PATH, settings)
    enabled = ", ".join(sorted(preset))
    print(f"Applied Codex++ preset: {args.preset}")
    print(f"Enabled: {enabled}")
    if args.preserve_official_relay:
        print("Preserved official/OpenAI relay selection to avoid changing Codex model routing.")
    print("Restart Codex++ / Codex app for UI injection changes to take effect.")
    return 0


def ccswitch_summary(_args: argparse.Namespace) -> int:
    db_path = ccswitch_db_path()
    if not db_path.exists():
        print(f"CC Switch database not found: {db_path}", file=sys.stderr)
        return 2
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        proxy_rows = con.execute(
            "select app_type, proxy_enabled, enabled, live_takeover_active, listen_address, listen_port, auto_failover_enabled from proxy_config order by app_type"
        ).fetchall()
        provider_rows = con.execute(
            "select app_type, id, name, category, provider_type, is_current, in_failover_queue from providers order by app_type, sort_index, name"
        ).fetchall()
        endpoint_rows = con.execute(
            "select app_type, provider_id, count(*) as endpoint_count from provider_endpoints group by app_type, provider_id"
        ).fetchall()
    finally:
        con.close()

    endpoint_counts = {(row["app_type"], row["provider_id"]): row["endpoint_count"] for row in endpoint_rows}
    print(f"CC Switch database: {db_path}")
    print("Proxy config:")
    for row in proxy_rows:
        listen = f"{row['listen_address']}:{row['listen_port']}"
        print(
            f"- {row['app_type']}: proxy_enabled={bool(row['proxy_enabled'])} enabled={bool(row['enabled'])} "
            f"live_takeover={bool(row['live_takeover_active'])} listen={listen} failover={bool(row['auto_failover_enabled'])}"
        )
    print("Providers:")
    for row in provider_rows:
        endpoint_count = endpoint_counts.get((row["app_type"], row["id"]), 0)
        print(
            f"- {row['app_type']} / {row['name']}: type={row['provider_type'] or '-'} category={row['category'] or '-'} "
            f"current={bool(row['is_current'])} failover={bool(row['in_failover_queue'])} endpoints={endpoint_count}"
        )
    return 0


def enable_ccswitch_codex(args: argparse.Namespace) -> int:
    if args.confirm != "enable-ccswitch-codex":
        print("Refusing to edit CC Switch state without --confirm enable-ccswitch-codex", file=sys.stderr)
        return 2
    db_path = ccswitch_db_path()
    if not db_path.exists():
        print(f"CC Switch database not found: {db_path}", file=sys.stderr)
        return 2
    backup_file(db_path, "ccswitch_enable_codex")
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(
            "update proxy_config set proxy_enabled=1, enabled=1, live_takeover_active=1, updated_at=datetime('now') where app_type='codex'"
        )
        con.commit()
    finally:
        con.close()
    print(f"Enabled CC Switch Codex routing rows={cur.rowcount}. Claude/Gemini rows were not changed.")
    return 0


def doctor(_args: argparse.Namespace) -> int:
    auth = auth_summary()
    routing = routing_summary()
    eco = ecosystem_summary()
    cpp = codexplusplus_settings_summary()
    proxy_rows = ccswitch_proxy_rows()
    codex_proxy = next((row for row in proxy_rows if row.get("app_type") == "codex"), None)

    print("Codex Model Router Doctor")
    print(f"- Codex home: {CODEX_HOME}")
    print(f"- Official login: exists={auth['exists']} mode={auth['mode']} auth_mode={auth['auth_mode']} tokens={auth['has_tokens']}")
    print(f"- Active Codex routing: provider={routing['provider'] or 'openai/default'} model={routing['model'] or 'default'} ccswitch_provider={routing['has_ccswitch_provider']}")
    print(f"- CC Switch detected: db={eco['cc_switch']['db_exists']} settings={eco['cc_switch']['settings_exists']} desktop_support={eco['cc_switch']['desktop_support_exists']}")
    if codex_proxy:
        print(
            f"- CC Switch Codex route: proxy_enabled={bool(codex_proxy.get('proxy_enabled'))} "
            f"enabled={bool(codex_proxy.get('enabled'))} live_takeover={bool(codex_proxy.get('live_takeover_active'))} "
            f"base_url={ccswitch_codex_base_url()}"
        )
    print(
        f"- Codex++ detected: settings={cpp['settings_exists']} running={cpp['status']} "
        f"enhancements={cpp['enhancements_enabled']} session_delete={cpp['session_delete_enabled']} "
        f"active_relay={cpp['active_relay_name'] or cpp['active_relay_id']} mode={cpp['active_relay_mode']}"
    )

    print("Recommended next actions:")
    if not eco["cc_switch"]["db_exists"]:
        print("- CC Switch is not configured yet. Install it from GitHub Releases, add providers in the CC Switch UI, then rerun doctor.")
    if not cpp["settings_exists"]:
        print("- BigPizzaV3 Codex++ is not configured yet. Install it from GitHub Releases if you want Codex UI enhancements.")
    if not auth["exists"] or not auth["has_tokens"]:
        print("- Sign in to official Codex/OpenAI first, then rerun: codex-model-router doctor")
    if routing["provider"] not in (None, "openai") and not routing["has_ccswitch_provider"]:
        print("- Unknown third-party provider is active. Restore official mode: codex_model_router.py restore-official")
    if routing["has_ccswitch_provider"]:
        print("- Codex is configured for CC Switch. To return official: codex_model_router.py restore-official")
    if eco["cc_switch"]["db_exists"] and codex_proxy and not bool(codex_proxy.get("enabled")):
        print("- To route Codex through CC Switch: enable-ccswitch-codex, then enable-ccswitch with your model/env key.")
    if (
        eco["cc_switch"]["db_exists"]
        and codex_proxy
        and bool(codex_proxy.get("enabled"))
        and bool(codex_proxy.get("live_takeover_active"))
        and routing["provider"] in (None, "openai")
    ):
        print("- CC Switch Codex takeover is active while Codex config is official. If you want official-only mode, run disable-ccswitch-codex.")
    if cpp["settings_exists"] and not cpp["enhancements_enabled"]:
        print("- To enable Codex++ mainstream UI enhancements safely: configure-codexplusplus --preset safe-ui --confirm configure-codexplusplus")
    if cpp["settings_exists"] and cpp["active_relay_mode"] not in (None, "official"):
        print("- Codex++ active relay is not official. Use configure-codexplusplus with preserve-official-relay or restore official routing before public demos.")
    print("- For download links and install steps: codex_model_router.py install-guide")
    return 0


def install_guide(_args: argparse.Namespace) -> int:
    print("Install Guide")
    print("1. Install Codex first and sign in with official OpenAI/ChatGPT.")
    print("2. Install CC Switch from GitHub Releases: https://github.com/farion1231/cc-switch/releases")
    print("   Official repo: https://github.com/farion1231/cc-switch")
    print("   Use it for provider presets, Claude/Codex/Gemini local routing, MCP, and skills management.")
    print("   Add real providers/API keys in the CC Switch UI or environment; this script will not print or store secret values.")
    print("3. Install BigPizzaV3 Codex++ from GitHub Releases: https://github.com/BigPizzaV3/CodexPlusPlus/releases")
    print("   Official repo: https://github.com/BigPizzaV3/CodexPlusPlus")
    print("   Use it for Codex launcher/manager, relay profiles, diagnostics, updates, and UI enhancements.")
    print("4. Optional advanced tweak system: https://github.com/b-nnett/codex-plusplus")
    print("   This is a different Codex++ project that patches Codex and loads tweaks. Do not mix it casually with BigPizzaV3 Codex++.")
    print("5. After installing, ask Codex: Use $codex-model-router to run doctor and guide setup.")
    print("6. Runtime backups are stored outside the skill at ~/.codex/runtime/codex-model-router/backups.")
    return 0


def status(args: argparse.Namespace) -> int:
    result = {
        "codex_home": str(CODEX_HOME),
        "auth": auth_summary(),
        "routing": routing_summary(),
        "ecosystem": ecosystem_summary(),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Codex home: {result['codex_home']}")
        auth = result["auth"]
        print(f"Auth: exists={auth['exists']} mode={auth['mode']} auth_mode={auth['auth_mode']} tokens={auth['has_tokens']} last_refresh={auth['last_refresh']}")
        routing = result["routing"]
        print(f"Routing: provider={routing['provider'] or 'openai/default'} model={routing['model'] or 'default'} ccswitch={routing['has_ccswitch_provider']}")
        if routing["has_ccswitch_provider"]:
            env_state = "set" if routing["ccswitch_env_present"] else "missing"
            print(f"CC Switch: base_url={routing['ccswitch_base_url']} wire_api={routing['ccswitch_wire_api']} env_key={routing['ccswitch_env_key']} env={env_state}")
        eco = result["ecosystem"]
        print(f"Detected: cc-switch-db={eco['cc_switch']['db_exists']} codex++-config={eco['codex_plus_plus']['config_dir_exists']} codex++-backups={eco['codex_plus_plus']['codex_backups_count']}")
    return 0


def make_backup(reason: str) -> Path:
    backup_dir = STATE_ROOT / "backups" / f"{now_stamp()}_{reason}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    for path in (CONFIG_PATH, AUTH_PATH):
        if path.exists():
            shutil.copy2(path, backup_dir / path.name)
    print(f"Backup: {backup_dir}")
    return backup_dir


def backup_file(path: Path, reason: str) -> Path:
    backup_dir = STATE_ROOT / "backups" / f"{now_stamp()}_{reason}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy2(path, backup_dir / path.name)
    print(f"Backup: {backup_dir}")
    return backup_dir


def disable_ccswitch_codex(args: argparse.Namespace) -> int:
    if args.confirm != "disable-codex-takeover":
        print("Refusing to edit CC Switch state without --confirm disable-codex-takeover", file=sys.stderr)
        return 2
    db_path = ccswitch_db_path()
    if not db_path.exists():
        print(f"CC Switch database not found: {db_path}", file=sys.stderr)
        return 2
    backup_file(db_path, "ccswitch_disable_codex")
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(
            "update proxy_config set proxy_enabled=0, enabled=0, live_takeover_active=0, updated_at=datetime('now') where app_type='codex'"
        )
        con.commit()
    finally:
        con.close()
    print(f"Disabled CC Switch Codex takeover rows={cur.rowcount}. Claude/Gemini provider settings were not changed.")
    return 0


def read_session_index() -> list[dict]:
    if not SESSION_INDEX_PATH.exists():
        return []
    rows = []
    for line in SESSION_INDEX_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def session_files(session_id: str) -> list[Path]:
    if not SESSIONS_PATH.exists():
        return []
    return sorted(SESSIONS_PATH.rglob(f"*{session_id}.jsonl"))


def session_list(args: argparse.Namespace) -> int:
    rows = read_session_index()
    query = args.query.casefold() if args.query else None
    if query:
        rows = [row for row in rows if query in str(row.get("thread_name", "")).casefold() or query in str(row.get("id", "")).casefold()]
    rows.sort(key=lambda row: str(row.get("updated_at", "")), reverse=True)
    for row in rows[: args.limit]:
        session_id = str(row.get("id", ""))
        files = session_files(session_id)
        file_state = "file" if files else "missing-file"
        print(f"{row.get('updated_at', '-')}  {session_id}  {file_state}  {row.get('thread_name', '')}")
    print(f"Shown {min(len(rows), args.limit)} of {len(rows)} matching sessions.")
    return 0


def rewrite_session_index(rows: list[dict]) -> None:
    SESSION_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    SESSION_INDEX_PATH.write_text(text, encoding="utf-8")


def archive_session(args: argparse.Namespace) -> int:
    if args.confirm != "archive-session":
        print("Refusing to archive a session without --confirm archive-session", file=sys.stderr)
        return 2
    rows = read_session_index()
    target_rows = [row for row in rows if str(row.get("id")) == args.id]
    if not target_rows:
        print(f"Session id not found in index: {args.id}", file=sys.stderr)
        return 2
    files = session_files(args.id)
    if not files and not args.index_only:
        print(f"Session file not found for id {args.id}; pass --index-only to remove only the sidebar index entry.", file=sys.stderr)
        return 2
    backup_file(SESSION_INDEX_PATH, "session_index_before_archive")
    archive_root = ARCHIVED_SESSIONS_PATH / now_stamp() / args.id
    archive_root.mkdir(parents=True, exist_ok=False)
    for path in files:
        rel = path.relative_to(SESSIONS_PATH)
        dest = archive_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(dest))
    kept = [row for row in rows if str(row.get("id")) != args.id]
    rewrite_session_index(kept)
    print(f"Archived session {args.id}: index_removed=1 files_moved={len(files)} archive={archive_root}")
    return 0


def parse_header(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        return stripped
    return None


def remove_ccswitch_block(lines: list[str]) -> list[str]:
    output: list[str] = []
    skipping = False
    for line in lines:
        header = parse_header(line)
        if header in {"[model_providers.ccswitch]", "[model_providers.\"ccswitch\"]"}:
            skipping = True
            continue
        if skipping and header:
            skipping = False
        if not skipping:
            output.append(line)
    return output


def set_top_level_value(lines: list[str], key: str, value: str) -> list[str]:
    rendered = f'{key} = "{value}"\n'
    output: list[str] = []
    replaced = False
    inserted = False
    for line in lines:
        if parse_header(line) and not inserted and not replaced:
            output.append(rendered)
            inserted = True
        if line.startswith(f"{key} ") or line.startswith(f"{key}="):
            if not replaced:
                output.append(rendered)
                replaced = True
            continue
        output.append(line)
    if not replaced and not inserted:
        output.insert(0, rendered)
    return output


def remove_top_level_keys(lines: list[str], keys: set[str]) -> list[str]:
    output: list[str] = []
    in_top = True
    for line in lines:
        if parse_header(line):
            in_top = False
        if in_top and any(line.startswith(f"{key} ") or line.startswith(f"{key}=") for key in keys):
            continue
        output.append(line)
    return output


def write_config(text: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(text.rstrip() + "\n", encoding="utf-8")
    os.chmod(CONFIG_PATH, 0o600)


def restore_official(_args: argparse.Namespace) -> int:
    make_backup("restore_official")
    current = load_toml(CONFIG_PATH)
    provider = current.get("model_provider")
    model = str(current.get("model") or "")
    remove_keys = {"model_provider"}
    if provider == "ccswitch" or model.startswith("deepseek"):
        remove_keys.add("model")
    lines = read_text(CONFIG_PATH).splitlines(keepends=True)
    lines = remove_ccswitch_block(lines)
    lines = remove_top_level_keys(lines, remove_keys)
    write_config("".join(lines))
    if AUTH_PATH.exists():
        os.chmod(AUTH_PATH, 0o600)
    print("Restored official/default Codex routing. Run status and an ephemeral smoke test next.")
    return 0


def enable_ccswitch(args: argparse.Namespace) -> int:
    make_backup("enable_ccswitch")
    base_url = args.base_url or ccswitch_codex_base_url()
    lines = read_text(CONFIG_PATH).splitlines(keepends=True)
    lines = remove_ccswitch_block(lines)
    lines = set_top_level_value(lines, "model_provider", "ccswitch")
    lines = set_top_level_value(lines, "model", args.model)
    provider_block = (
        "\n[model_providers.ccswitch]\n"
        f'name = "{args.name}"\n'
        f'base_url = "{base_url}"\n'
        'wire_api = "responses"\n'
        f'env_key = "{args.env_key}"\n'
    )
    write_config("".join(lines).rstrip() + "\n" + provider_block)
    if not os.environ.get(args.env_key):
        print(f"Warning: environment variable {args.env_key} is not set in this shell.")
    print(f"Enabled Codex config for CC Switch routing at {base_url}. Verify CC Switch is running, then run status and a Codex smoke test.")
    return 0


def backups(_args: argparse.Namespace) -> int:
    roots = [STATE_ROOT / "backups", LEGACY_SKILL_STATE / "backups", CODEX_HOME / "backups"]
    found = []
    for root in roots:
        if root.exists():
            found.extend(path for path in root.iterdir() if path.is_dir())
    for path in sorted(found):
        has_config = (path / "config.toml").exists()
        has_auth = (path / "auth.json").exists()
        print(f"{path} config={has_config} auth={has_auth}")
    return 0


def restore_backup(args: argparse.Namespace) -> int:
    backup_dir = Path(args.backup_dir).expanduser()
    if not backup_dir.is_dir():
        print(f"Backup directory not found: {backup_dir}", file=sys.stderr)
        return 2
    config_backup = backup_dir / "config.toml"
    auth_backup = backup_dir / "auth.json"
    if not config_backup.exists():
        print(f"Backup has no config.toml: {backup_dir}", file=sys.stderr)
        return 2
    make_backup("before_restore_backup")
    shutil.copy2(config_backup, CONFIG_PATH)
    os.chmod(CONFIG_PATH, 0o600)
    if auth_backup.exists():
        shutil.copy2(auth_backup, AUTH_PATH)
        os.chmod(AUTH_PATH, 0o600)
    print(f"Restored backup: {backup_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    doctor_parser = sub.add_parser("doctor", help="Run a redacted one-shot health check and print recommended next actions")
    doctor_parser.set_defaults(func=doctor)

    install_parser = sub.add_parser("install-guide", help="Print GitHub download links and setup order")
    install_parser.set_defaults(func=install_guide)

    status_parser = sub.add_parser("status", help="Show redacted Codex auth/routing status")
    status_parser.add_argument("--json", action="store_true", help="Print JSON")
    status_parser.set_defaults(func=status)

    official_parser = sub.add_parser("restore-official", help="Restore default official OpenAI routing")
    official_parser.set_defaults(func=restore_official)

    cc_parser = sub.add_parser("enable-ccswitch", help="Route Codex through a local CC Switch bridge")
    cc_parser.add_argument("--base-url", help="Local bridge base URL. Defaults to CC Switch Codex listen port or http://127.0.0.1:15721/v1")
    cc_parser.add_argument("--model", default="deepseek-v4-flash", help="Model name exposed by the bridge")
    cc_parser.add_argument("--env-key", default="DEEPSEEK_API_KEY", help="Environment variable that stores the API key")
    cc_parser.add_argument("--name", default="CC Switch DeepSeek", help="Codex provider display name")
    cc_parser.set_defaults(func=enable_ccswitch)

    backups_parser = sub.add_parser("backups", help="List skill and Codex++ backups")
    backups_parser.set_defaults(func=backups)

    ccs_parser = sub.add_parser("ccswitch-summary", help="Show redacted CC Switch provider and proxy routing state")
    ccs_parser.set_defaults(func=ccswitch_summary)

    enable_codex_parser = sub.add_parser("enable-ccswitch-codex", help="Enable CC Switch live takeover for Codex only")
    enable_codex_parser.add_argument("--confirm", required=True, help="Must be: enable-ccswitch-codex")
    enable_codex_parser.set_defaults(func=enable_ccswitch_codex)

    disable_codex_parser = sub.add_parser("disable-ccswitch-codex", help="Disable CC Switch live takeover for Codex only")
    disable_codex_parser.add_argument("--confirm", required=True, help="Must be: disable-codex-takeover")
    disable_codex_parser.set_defaults(func=disable_ccswitch_codex)

    cpp_status_parser = sub.add_parser("codexplusplus-status", help="Show redacted Codex++ enhancement and relay settings")
    cpp_status_parser.add_argument("--json", action="store_true", help="Print JSON")
    cpp_status_parser.set_defaults(func=codexplusplus_status)

    cpp_enable_parser = sub.add_parser("enable-codexplusplus-session-delete", help="Enable Codex++ session delete UI enhancement safely")
    cpp_enable_parser.add_argument("--confirm", required=True, help="Must be: enable-codexplusplus-session-delete")
    cpp_enable_parser.add_argument(
        "--preserve-official-relay",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep Codex++ active relay on an official/OpenAI profile when possible",
    )
    cpp_enable_parser.set_defaults(func=enable_codexplusplus_session_delete)

    cpp_config_parser = sub.add_parser("configure-codexplusplus", help="Apply a safe Codex++ UI enhancement preset")
    cpp_config_parser.add_argument("--preset", choices=sorted(CODEX_PLUSPLUS_PRESETS), default="safe-ui")
    cpp_config_parser.add_argument("--confirm", required=True, help="Must be: configure-codexplusplus")
    cpp_config_parser.add_argument(
        "--preserve-official-relay",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep Codex++ active relay on an official/OpenAI profile when possible",
    )
    cpp_config_parser.set_defaults(func=configure_codexplusplus)

    sessions_parser = sub.add_parser("sessions", help="List Codex sidebar sessions without reading session content")
    sessions_parser.add_argument("--query", help="Filter by session id or visible title")
    sessions_parser.add_argument("--limit", type=int, default=20)
    sessions_parser.set_defaults(func=session_list)

    archive_parser = sub.add_parser("archive-session", help="Soft-delete a Codex sidebar session by archiving it")
    archive_parser.add_argument("--id", required=True, help="Session id from the sessions command")
    archive_parser.add_argument("--confirm", required=True, help="Must be: archive-session")
    archive_parser.add_argument("--index-only", action="store_true", help="Remove index entry even when the session file is missing")
    archive_parser.set_defaults(func=archive_session)

    restore_parser = sub.add_parser("restore-backup", help="Restore config/auth from a selected backup directory")
    restore_parser.add_argument("--backup-dir", required=True)
    restore_parser.set_defaults(func=restore_backup)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
