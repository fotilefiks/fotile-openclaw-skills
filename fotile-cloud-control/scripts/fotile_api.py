#!/usr/bin/env python3
"""
FOTILE Cloud Control - Python client and CLI.

A small, dependency-light client for the FOTILE open cloud device channel.
It uses `requests` when installed and falls back to the standard library
otherwise, so no third-party package is strictly required.
It supports the three operations an AI agent needs:

  * list_devices()   -> DeviceDiscovery
  * get_status()     -> DeviceSnapshot
  * control()        -> DeviceCommand

Configuration (in priority order, first match wins):

  1. Environment variable  FOTILE_API_KEY   (for CI and developer shells)
  2. File  ./.fotile_key                    (per-project, already gitignored)
  3. File  ~/.fotile/api_key                (per-user, written by `login`)

  FOTILE_API_KEY   Your personal AI Key (starts with `ft-cn-`).
                   Sent as `Authorization: Bearer <key>`. Never logged or echoed.
  FOTILE_API_BASE  Optional. API base URL.
                   Defaults to https://api-test.fotile.com (staging, internal
                   testing only). Override it to point at production or any
                   other deployment, e.g. FOTILE_API_BASE=https://api.fotile.com
  FOTILE_CORP_ID   Optional. The ecosystem enterprise (grantee) id.
                   Not needed for the AI channel: the server overwrites
                   thirdPartyId/granteeId with its own channel id and resolves
                   the user from your key. Required only for direct
                   cloud-to-cloud integrations that call /open-cloud/v1/api.

Most users never set an environment variable. They either run

    python fotile_api.py login

and paste the key when prompted (input is hidden), or hand the key to their
agent, which calls `login <key>` on their behalf. Both paths store the key in
~/.fotile/api_key with owner-only permissions.

Library usage:

    from fotile_api import FotileAPI
    api = FotileAPI()                       # finds the key automatically
    for d in api.list_devices():
        print(d["thirdPartyDevId"], d.get("prodId"))
    print(api.get_status(["1145153645"]))
    api.control(prod_id="...", device_id="1145153645",
                sid="PowerSwitch", command={"PowerSwitch": 0})

CLI usage:

    python fotile_api.py login                 # interactive, hidden input
    python fotile_api.py login ft-cn-xxxx      # non-interactive (agent-friendly)
    python fotile_api.py whoami                # which key/source, is it valid
    python fotile_api.py devices
    python fotile_api.py status 1145153645 1145153646
    python fotile_api.py control <prodId> <deviceId> <sid> '{"PowerSwitch": 0}'
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import stat
import sys
import time
import urllib.error
import urllib.request
import uuid
from typing import Any, Dict, List, Optional, Tuple

# `requests` is optional. Some agent runtimes reset their Python environment
# between sessions and lose installed packages; falling back to the standard
# library keeps the skill usable with zero third-party dependencies.
try:
    import requests
except ImportError:  # pragma: no cover - depends on the host environment
    requests = None  # type: ignore[assignment]

# API base. Currently pinned to staging for internal testing.
# Switch DEFAULT_API_BASE to the production host once it is provisioned.
DEFAULT_API_BASE = "https://api-test.fotile.com"

# Personal-key channel. Unlike /open-cloud/v1/api (user access token,
# cloud-to-cloud partners), this path authenticates with a personal AI Key and
# only exposes DeviceDiscovery / DeviceSnapshot / DeviceCommand.
API_PATH = "/open-cloud/v1/ai/api"

DEFAULT_TIMEOUT = 15

# Retries on rate limiting only (HTTP 429 / business code 42901).
MAX_RETRIES = 2

# DeviceDiscovery caps the implicit first page at 50 devices. Sending explicit
# page/pageSize makes the server also return payload.total / payload.hasMore.
# One large page is preferred over iterating small pages: the server's paged
# SQL has no ORDER BY, so page boundaries are not stable and paging in small
# steps can duplicate or drop devices. Iterating is only a fallback for the
# (currently hypothetical) case of more devices than one large page holds.
DISCOVERY_PAGE_SIZE = 1000
DISCOVERY_MAX_PAGES = 20
# DeviceSnapshot accepts many ids, but keep each request bounded for accounts
# with hundreds of devices (and to stay under per-call rate limits).
SNAPSHOT_BATCH_SIZE = 20

# Cloud-to-cloud namespaces.
NS_DISCOVERY = "DeviceDiscovery"
NS_SNAPSHOT = "DeviceSnapshot"
NS_COMMAND = "DeviceCommand"

# Where a key can live. Checked in order; the first hit wins.
KEY_ENV = "FOTILE_API_KEY"
KEY_FILE_LOCAL = ".fotile_key"
KEY_FILE_USER = os.path.join("~", ".fotile", "api_key")

# Prefix of every personal key. Used for cheap validation before we store one.
KEY_PREFIX = "ft-cn-"

# Network exceptions worth retrying. Built at import time because their type
# set depends on whether requests is installed.
_NETWORK_ERRORS: Tuple[type, ...] = (urllib.error.URLError, OSError)
if requests is not None:
    _NETWORK_ERRORS = (requests.RequestException,) + _NETWORK_ERRORS


class _Response:
    """Tiny response shim so the rest of the client is transport-agnostic."""

    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text

    def json(self) -> Any:
        return json.loads(self.text)


def _http_post(url: str, headers: Dict[str, str], body: Dict[str, Any],
               timeout: int) -> _Response:
    """POST a JSON body, using requests when present and urllib otherwise."""
    raw = json.dumps(body).encode("utf-8")
    if requests is not None:
        resp = requests.post(url, headers=headers,
                             data=raw.decode("utf-8"), timeout=timeout)
        return _Response(resp.status_code, resp.text)
    req = urllib.request.Request(url, data=raw, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(
                req, timeout=timeout,
                context=ssl.create_default_context()) as resp:
            return _Response(resp.status, resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # HTTPError is itself a file-like response. Keep status and body so the
        # caller can surface the real business code instead of a bare error.
        try:
            text = exc.read().decode("utf-8", "replace")
        finally:
            exc.close()
        return _Response(exc.code, text)


def _candidate_key_files() -> List[str]:
    """Paths to probe for a stored key, highest priority first."""
    return [
        os.path.abspath(KEY_FILE_LOCAL),
        os.path.expanduser(KEY_FILE_USER),
    ]


def _read_key_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except (OSError, UnicodeDecodeError):
        return ""


def resolve_api_key() -> Tuple[str, str]:
    """
    Locate the AI Key.

    :returns: (key, source) where source is a human-readable origin such as
              "environment", ".fotile_key", "~/.fotile/api_key", or "" when
              nothing was found.
    """
    env_key = os.getenv(KEY_ENV, "").strip()
    if env_key:
        return env_key, "environment (" + KEY_ENV + ")"
    for path in _candidate_key_files():
        key = _read_key_file(path)
        if key:
            shown = KEY_FILE_USER if path.endswith(os.path.join(".fotile", "api_key")) \
                else KEY_FILE_LOCAL
            return key, shown
    return "", ""


def save_api_key(key: str) -> str:
    """
    Persist the key to ~/.fotile/api_key with owner-only permissions.

    Written to the user-level file rather than the current directory so the
    key keeps working regardless of which project the user opens next.

    :returns: the path written.
    """
    path = os.path.expanduser(KEY_FILE_USER)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Create with 0600 from the start so the key is never world-readable,
    # even for the brief window before an explicit chmod.
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    mode = stat.S_IRUSR | stat.S_IWUSR
    fd = os.open(path, flags, mode)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(key + "\n")
    finally:
        try:
            os.chmod(path, mode)
        except OSError:
            pass  # best effort on filesystems without POSIX permissions
    return path


def mask_key(key: str) -> str:
    """Show only the prefix, so keys can be mentioned safely in logs/chat."""
    if not key:
        return "<empty>"
    return key[:11] + "****"


# Shown when no key is configured. Written for a non-technical user: tells them
# exactly where to get a key and offers the two ways to hand it over, instead
# of asking them to set an environment variable they have never heard of.
#
# Keep the mini-program path in sync with SKILL.md ("Scenario A"). If it changes,
# change it in both places.
MINI_PROGRAM = "「方太知味」小程序"
KEY_MENU_PATH = "【待确认：获取 AI Key 的菜单路径】"

MISSING_KEY_MESSAGE = (
    "尚未配置方太 AI Key。\n"
    "获取方式：打开微信 → " + MINI_PROGRAM + " → 登录你的方太账号 → " + KEY_MENU_PATH +
    " → 点「获取 AI Key」，复制那串 ft-cn- 开头的字符。\n"
    "配置方式（任选一种）：\n"
    "  1) 直接把 Key 发给个人 AI Agent，它会替你配置好；\n"
    "  2) 在本目录运行：python scripts/fotile_api.py login ，按提示粘贴 Key（输入不显示）。\n"
    "提示：Key 可随时在同一页面撤销，撤销后所有使用它的 Agent 立即失效。"
)


class FotileAPIError(RuntimeError):
    """Raised when the cloud returns a non-zero business code or a transport error."""

    def __init__(self, message: str, code: Optional[int] = None,
                 http_status: Optional[int] = None):
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.hint = ERROR_HINTS.get(code) if code is not None else None

    def __str__(self) -> str:  # pragma: no cover - trivial
        parts = [super().__str__()]
        if self.code is not None:
            parts.append(f"code={self.code}")
        if self.http_status is not None:
            parts.append(f"http={self.http_status}")
        if self.hint:
            parts.append(f"hint: {self.hint}")
        return " | ".join(parts)


# Plain-language guidance for the business codes an agent will actually meet.
# Keeping this next to the client means the agent can act on a code without
# having to look anything up.
ERROR_HINTS: Dict[int, str] = {
    40001: "malformed request (bad JSON, missing namespace, or non-numeric device id)",
    40100: "no credential sent; check that FOTILE_API_KEY is set",
    40101: "the AI Key is not valid; ask the user for a new one",
    40102: "the key and the x-user header refer to different users",
    40103: "this AI Key has been revoked; ask the user to issue a new one",
    40104: "this AI Key has expired; ask the user to issue a new one",
    40301: "this operation is not available through the AI channel",
    40302: "the device is not bound to this user's account",
    40304: "the user has reached the maximum number of AI Keys",
    40305: "this model has no standardized protocol mapping, so it cannot be "
           "controlled; do not retry with another sid — offer a status read "
           "instead and point the user to the FOTILE app",
    40306: "this function is not mapped for this model — the appliance is "
           "controllable, but this particular sid has no expression. Read the "
           "status to see which fields this model actually reports, and do not "
           "retry the same sid or try another name for it",
    42901: "rate limited; retrying with backoff, otherwise ask the user to wait",
    10009: "device not found; re-list devices and confirm the id",
    10011: "device is offline; report it instead of retrying",
    10098: "device is in local control mode; remote control is blocked",
    10099: "remote authorization is off on the device; the user must enable it "
           "in the FOTILE app before remote control works",
    100022: "the user has not authorized this app for the device",
    99999: "server-side error; retry once, then report it",
}


class FotileAPI:
    """Client for the FOTILE open cloud device channel."""

    def __init__(self,
                 api_key: Optional[str] = None,
                 api_base: Optional[str] = None,
                 corp_id: Optional[str] = None,
                 api_path: Optional[str] = None,
                 timeout: int = DEFAULT_TIMEOUT):
        if api_key:
            self.api_key, self.key_source = api_key, "argument"
        else:
            self.api_key, self.key_source = resolve_api_key()
        self.api_base = (api_base
                         or os.getenv("FOTILE_API_BASE", DEFAULT_API_BASE)).rstrip("/")
        # Empty corp id is valid for the AI channel (the server fills it in).
        self.corp_id = corp_id if corp_id is not None else os.getenv("FOTILE_CORP_ID", "")
        # Path is configurable so the same client can target the personal-key
        # channel (default) or a direct cloud-to-cloud deployment.
        self.api_path = api_path or os.getenv("FOTILE_API_PATH", API_PATH)
        self.timeout = timeout
        if not self.api_key:
            raise FotileAPIError(MISSING_KEY_MESSAGE)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _post_with_retry(self, url: str, body: Dict[str, Any],
                         namespace: str) -> _Response:
        """
        POST with bounded retry on rate limiting (HTTP 429 / code 42901).

        Retries twice with exponential backoff (1s, 2s). Anything else is
        returned immediately so the caller can surface the real error.
        """
        last_exc: Optional[Exception] = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = _http_post(url, self._headers(), body, self.timeout)
            except _NETWORK_ERRORS as exc:
                last_exc = exc
                if attempt < MAX_RETRIES:
                    time.sleep(1.0 * (2 ** attempt))
                    continue
                raise FotileAPIError(
                    f"Network error calling {namespace}: {exc}") from exc

            if not self._is_rate_limited(resp):
                return resp

            if attempt < MAX_RETRIES:
                time.sleep(1.0 * (2 ** attempt))
                continue
            return resp  # let the caller raise with the server's message
        # Unreachable, but keeps type checkers happy.
        raise FotileAPIError(
            f"Network error calling {namespace}: {last_exc}")

    @staticmethod
    def _is_rate_limited(resp: _Response) -> bool:
        if resp.status_code == 429:
            return True
        try:
            payload = (resp.json() or {}).get("payload") or {}
        except ValueError:
            return False
        return payload.get("code") == 42901

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _post(self, namespace: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = {
            "header": {
                "namespace": namespace,
                # Left empty on purpose: the personal-key channel overwrites
                # both fields with its own channel id. Sending an empty string
                # here is valid and avoids leaking any enterprise id.
                "thirdPartyId": self.corp_id,
                "granteeId": self.corp_id,
                "messageId": uuid.uuid4().hex,
                "timestamp": int(time.time() * 1000),
            },
            "payload": payload,
        }
        url = self.api_base + self.api_path
        resp = self._post_with_retry(url, body, namespace)

        # Never log the Authorization header.
        try:
            data = resp.json()
        except ValueError as exc:
            raise FotileAPIError(
                f"Non-JSON response from {namespace} (HTTP {resp.status_code})",
                http_status=resp.status_code) from exc

        if not isinstance(data, dict):
            raise FotileAPIError(
                f"Unexpected response shape from {namespace}",
                http_status=resp.status_code)

        result_payload = data.get("payload")
        if not isinstance(result_payload, dict):
            # The server always wraps results in {"header": {...}, "payload": {...}}.
            # A flat body means the request never reached the business handler
            # (bad gateway route, auth proxy, or an upstream error page).
            raise FotileAPIError(
                data.get("description")
                or data.get("error")
                or f"Unexpected response body from {namespace}",
                code=data.get("code"),
                http_status=resp.status_code)

        code = result_payload.get("code")
        # The business description lives in `description`; `msg` is kept as a
        # fallback for older deployments.
        message = (result_payload.get("description")
                   or result_payload.get("msg"))

        if resp.status_code != 200:
            raise FotileAPIError(
                message or f"HTTP {resp.status_code} error",
                code=code, http_status=resp.status_code)

        # Success is code == 0. `None` is tolerated because some deployments
        # omit `code` on success; treating it as failure would raise on a
        # perfectly good response.
        if code is not None and code != 0:
            raise FotileAPIError(
                message or f"{namespace} failed",
                code=code, http_status=resp.status_code)
        if code is None and not any(
                k in result_payload for k in ("devices", "deviceList", "command")):
            # No code and none of the expected fields: refuse to report success.
            raise FotileAPIError(
                message or f"{namespace} returned an unrecognized payload",
                http_status=resp.status_code)
        return result_payload

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def discover_devices(self) -> Dict[str, Any]:
        """
        Return every device reachable by this key, plus pagination metadata.

        An account can hold hundreds of devices. The server silently returns
        only the first 50 unless the client sends page/pageSize, so this method
        always sends them and honours total/hasMore. Results are de-duplicated
        by device id because the server's paged SQL has no ORDER BY.

        The C-end AI channel is deliberately NOT filtered by family: every
        device bound (or shared) to the key's user is in scope.

        :returns: dict with keys
                  devices    - list of device dicts, de-duplicated by id
                  total      - server-side count, or None if not reported
                  complete   - False if anything could not be retrieved
                  pages      - number of discovery requests actually issued
                  duplicates - repeated device ids seen across pages
                  missing    - total - len(devices), when total is known
                  malformed  - entries dropped because they had no device id
        """
        merged: Dict[str, Dict[str, Any]] = {}
        order: List[str] = []
        total: Optional[int] = None
        duplicates = 0
        malformed = 0
        pages = 0
        complete = True

        for page in range(1, DISCOVERY_MAX_PAGES + 1):
            payload = self._post(
                NS_DISCOVERY,
                {"page": page, "pageSize": DISCOVERY_PAGE_SIZE})
            pages += 1
            server_total = payload.get("total")
            if isinstance(server_total, int):
                total = server_total if total is None else max(total, server_total)
            batch = payload.get("devices") or payload.get("deviceList") or []
            for device in batch:
                did = device.get("thirdPartyDevId")
                if did is None:
                    malformed += 1
                    continue
                key = str(did)
                if key in merged:
                    duplicates += 1
                    continue
                merged[key] = device
                order.append(key)
            if payload.get("hasMore") is not True:
                break
        else:
            # Ran out of page budget while the server still said hasMore.
            complete = False

        devices = [merged[k] for k in order]
        missing: Optional[int] = None
        if total is not None and len(devices) < total:
            # `total` is a raw DB count. Devices whose product model is broken
            # are skipped during server-side conversion and never appear in
            # any page, so paging cannot recover them. Report the gap instead
            # of silently claiming the list is complete.
            missing = total - len(devices)
            complete = False

        return {
            "devices": devices,
            "total": total,
            "complete": complete,
            "pages": pages,
            "duplicates": duplicates,
            "missing": missing,
            "malformed": malformed,
        }

    def list_devices(self) -> List[Dict[str, Any]]:
        """Return ALL devices bound to the current user (DeviceDiscovery)."""
        return self.discover_devices()["devices"]

    def get_status(self, device_id_list: List[str | int],
                   batch_size: int = SNAPSHOT_BATCH_SIZE) -> List[Dict[str, Any]]:
        """
        Return current snapshots for one or more devices (DeviceSnapshot).

        Large accounts need many ids; split them into bounded batches so a
        single request never grows unbounded. Duplicate ids are removed while
        preserving order.
        """
        seen = set()
        ids: List[str] = []
        for device_id in device_id_list:
            key = str(device_id)
            if key not in seen:
                seen.add(key)
                ids.append(key)
        if batch_size < 1:
            raise FotileAPIError("batch_size must be >= 1")
        out: List[Dict[str, Any]] = []
        for i in range(0, len(ids), batch_size):
            payload = self._post(
                NS_SNAPSHOT, {"thirdPartyDevIds": ids[i:i + batch_size]})
            out.extend(payload.get("devices") or payload.get("deviceList") or [])
        return out

    def control(self, prod_id: str, device_id: str | int,
                sid: str, command: Dict[str, Any],
                confirm: bool = False) -> Dict[str, Any]:
        """
        Send a control command to a device (DeviceCommand).

        :param prod_id:   Product id (prodId) from list_devices().
        :param device_id: Third-party device id (thirdPartyDevId).
        :param sid:       Controllable function identifier, e.g. "PowerSwitch".
        :param command:   Function payload, e.g. {"PowerSwitch": 0}.
        :param confirm:   Must be True for high-risk functions (gas ignition,
                          child-lock / door-lock release, unattended heating).
        :returns:         The command result payload.
        """
        timestamp = int(time.time() * 1000)
        cmd: Dict[str, Any] = {
            "timestamp": timestamp,
            "thirdPartyDevId": str(device_id),
            "prodId": prod_id,
            "sid": sid,
            "data": command,
        }
        if confirm:
            cmd["confirm"] = True
        return self._post(NS_COMMAND, {"command": cmd})


# ---------------------------------------------------------------------- #
# CLI
# ---------------------------------------------------------------------- #
def _print(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_login(key: Optional[str]) -> int:
    """
    Store a personal AI Key after verifying it actually works.

    Reading the key interactively hides the input, so a shoulder-surfer or a
    terminal recording will not capture it. Passing the key as an argument is
    supported for agents that receive it from the user in chat.

    The key is validated against the server *before* being written, so a typo
    never leaves a broken key behind.
    """
    if not key:
        print("请粘贴你的方太 AI Key（ft-cn- 开头，输入时不显示），然后回车：")
        try:
            import getpass
            key = getpass.getpass("AI Key: ")
        except (ImportError, EOFError):
            # getpass is unavailable in some embedded terminals.
            key = input("AI Key: ")
    key = (key or "").strip()
    if not key:
        print("未输入 Key，已取消。", file=sys.stderr)
        return 1
    if not key.startswith(KEY_PREFIX):
        print(f"这看起来不是方太 AI Key（应以 {KEY_PREFIX} 开头，实际是 {mask_key(key)}）。",
              file=sys.stderr)
        return 1

    # Verify before persisting: a wrong key must not overwrite a working one.
    print("正在验证 Key …")
    try:
        api = FotileAPI(api_key=key)
        devices = api.list_devices()
    except FotileAPIError as exc:
        print(f"验证失败，Key 未保存。{exc}", file=sys.stderr)
        return 1

    path = save_api_key(key)
    print(f"验证通过，已保存到 {path}")
    print("该文件仅本机账号与系统管理员可读（Windows 为 NTFS 权限，"
          "macOS/Linux 为 600）。")
    print(f"当前账号下可见设备：{len(devices)} 台")
    print("提示：这条 Key 可随时在「方太知味」小程序同一页面撤销；"
          "撤销后所有使用它的 Agent 会立即失效。")
    return 0


def cmd_whoami() -> int:
    """
    Report the current state as JSON, so an agent can branch on it reliably
    instead of parsing prose.

    The `state` field is the contract:
      NO_KEY       no key found anywhere
      KEY_INVALID  key present but rejected (invalid / revoked / expired)
      NO_DEVICE    key works, account has no bound devices
      READY        key works and devices are visible
      UNREACHABLE  network or server problem; cannot tell
    """
    key, source = resolve_api_key()
    if not key:
        _print({
            "state": "NO_KEY",
            "key": None,
            "source": None,
            "onboarding": MISSING_KEY_MESSAGE,
        })
        return 1
    info: Dict[str, Any] = {
        "key": mask_key(key),
        "source": source,
        "base": os.getenv("FOTILE_API_BASE", DEFAULT_API_BASE),
        "path": os.getenv("FOTILE_API_PATH", API_PATH),
    }
    try:
        api = FotileAPI(api_key=key)
        discovery = api.discover_devices()
        devices = discovery["devices"]
        info["valid"] = True
        info["deviceCount"] = len(devices)
        info["deviceTotal"] = discovery["total"]
        info["deviceListComplete"] = discovery["complete"]
        info["state"] = "READY" if devices else "NO_DEVICE"
    except FotileAPIError as exc:
        info["valid"] = False
        info["error"] = str(exc)
        info["code"] = exc.code
        if exc.code is None:
            # Transport failure: the key may be fine, we simply could not ask.
            info["state"] = "UNREACHABLE"
        else:
            info["state"] = "KEY_INVALID"
    _print(info)
    return 0 if info["state"] in ("READY", "NO_DEVICE") else 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fotile_api",
        description="FOTILE open cloud device control client.")
    sub = parser.add_subparsers(dest="action", required=True)

    p_login = sub.add_parser("login", help="Store and verify your personal AI Key")
    p_login.add_argument("key", nargs="?", default=None,
                         help="The key. Omit to be prompted (input hidden).")

    sub.add_parser("whoami", help="Show which key is in use and whether it works")
    p_dev = sub.add_parser("devices", help="List ALL bound devices")
    p_dev.add_argument(
        "--meta", action="store_true",
        help="Also print pagination metadata (total, completeness, pages)")

    p_status = sub.add_parser("status", help="Query device status")
    p_status.add_argument("device_ids", nargs="+", help="One or more device ids")

    p_ctrl = sub.add_parser("control", help="Send a control command")
    p_ctrl.add_argument("prod_id", help="Product id (prodId)")
    p_ctrl.add_argument("device_id", help="Device id (thirdPartyDevId)")
    p_ctrl.add_argument("sid", help="Function identifier, e.g. PowerSwitch")
    p_ctrl.add_argument("command", help='JSON payload, e.g. \'{"PowerSwitch": 0}\'')
    p_ctrl.add_argument("--confirm", action="store_true",
                        help="Required for high-risk functions")

    args = parser.parse_args(argv)

    # Login and whoami manage the key itself, so they run before the client is
    # constructed (which would fail when no key exists yet).
    if args.action == "login":
        return cmd_login(args.key)
    if args.action == "whoami":
        return cmd_whoami()

    try:
        api = FotileAPI()
        if args.action == "devices":
            discovery = api.discover_devices()
            if args.meta:
                _print(discovery)
            else:
                _print(discovery["devices"])
                if not discovery["complete"]:
                    print(
                        "Warning: device list may be incomplete "
                        f"(server total={discovery['total']}, "
                        f"returned={len(discovery['devices'])}, "
                        f"missing={discovery['missing']}, "
                        f"pages={discovery['pages']}).",
                        file=sys.stderr)
        elif args.action == "status":
            _print(api.get_status(args.device_ids))
        elif args.action == "control":
            try:
                command = json.loads(args.command)
            except json.JSONDecodeError as exc:
                raise FotileAPIError(f"command must be valid JSON: {exc}") from exc
            _print(api.control(args.prod_id, args.device_id, args.sid,
                               command, confirm=args.confirm))
    except FotileAPIError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
