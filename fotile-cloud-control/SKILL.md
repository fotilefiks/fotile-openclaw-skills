---
name: fotile-cloud-control
description: >-
  Query and control FOTILE (方太) smart kitchen appliances through the FOTILE
  open cloud using natural language. Use when the user asks to inspect or
  operate their FOTILE range hood, integrated stove/steamer/oven, dishwasher,
  refrigerator, gas stove, water purifier/heater, sterilizer (disinfection
  cabinet), water heater, or food purifier — for example turning a device on
  or off, setting fan speed, temperature, cooking/working mode, duration, or
  checking current status and whether a device is online. Needs a personal
  FOTILE AI key, which the user obtains once from the FOTILE mini-program; if
  no key is configured yet, guide them through getting one (see "Startup
  playbook").
metadata:
  openclaw:
    version: "0.2.0"
    # The key is NOT required at install time: it lives in ~/.fotile/api_key
    # after `login`. Declaring it here would make some harnesses refuse to load
    # the skill, which would hide the very onboarding text new users need.
    requires:
      pip: ["requests>=2.28.0"]
---

# FOTILE Cloud Control

Control the user's own FOTILE kitchen appliances over the cloud. One personal
AI Key authorizes access only to devices bound to that user's FOTILE account.
No local network, device secret, or firmware change is required.

## When to use

Use this skill when the user wants to view or operate their FOTILE smart
kitchen devices, e.g.:

- "我绑定了哪些方太设备？" / "List my FOTILE devices."
- "蒸烤箱现在多少度？" / "What is my oven doing right now?"
- "把洗碗机关掉" / "Turn off the dishwasher."
- "油烟机调到三档" / "Set the range hood to level 3."
- "消毒柜启动自动模式" / "Start the sterilizer in auto mode."

Do NOT use this skill for: device unbinding/removal, Wi-Fi provisioning,
firmware (OTA) upgrades, or account management. Those must be completed by the
user in the FOTILE App.

## Startup playbook

**Run this once at the start of any conversation where the user wants to use
their appliances.** Determine the state first, then respond with the matching
opening line. Do not dump technical detail on the user — most are not
developers.

### Step 1 — determine the state

```bash
python scripts/fotile_api.py whoami
```

`whoami` always prints JSON with a `state` field. Branch on it; do not parse
prose or guess:

| `state` | Meaning | Go to |
|---|---|---|
| `NO_KEY` | no key configured anywhere | Scenario A |
| `KEY_INVALID` | key rejected: invalid / revoked / expired | Scenario B |
| `NO_DEVICE` | key works, but the account has no bound devices | Scenario C |
| `READY` | key works and `deviceCount` > 0 | Scenario D |
| `UNREACHABLE` | network or server problem — the key may still be fine | Tell the user you cannot reach FOTILE's service right now and ask them to try again later. Do **not** tell them to re-issue the key. |

The `NO_KEY` response also carries an `onboarding` string with the exact
instructions — you may relay it verbatim instead of composing your own.

---

### Scenario A — no key yet (first-time user)

This is the most important moment in the whole skill. The user has never heard
of an "AI key". **Do not** say "配置失败" or "请设置环境变量". Sell the value
first, then give an exact path to the key.

Opening line:

> 我可以帮你用一句话控制你名下的方太设备——查状态、开关机、调档位、设温度都行。
>
> 开始前需要一枚「AI Key」，拿一次就能长期用：
> 1. 打开微信，进「方太知味」小程序，用你的方太账号登录
> 2. 进入 **【待确认：获取 AI Key 的菜单路径】**
> 3. 点「获取 AI Key」，复制那串 `ft-cn-` 开头的字符
>
> 复制好直接发我，我帮你配置；不想贴在对话里的话，也可以自己运行
> `python scripts/fotile_api.py login`（输入时不显示）。

Then stop and wait. Do not run any other command until the user responds.

**When they hand you the key**, store it:

```bash
python scripts/fotile_api.py login <key>
```

Then reply in one line + the two disclosures:

> 配置好了，你名下能看到 **N 台**设备。想先试试的话，可以说「看看我有哪些设备」。
>
> 说明一下：这枚 Key 存在你本机（只有你的账号能读），同时也会留在这段对话记录里。
> 如果介意，可以到小程序同一页面撤销后重新领一枚——撤销后所有用它的助手会立刻失效。

Never skip those two disclosures. They are the difference between an informed
choice and a surprise later.

---

### Scenario B — key exists but is rejected

Codes `40101` (invalid), `40103` (revoked), `40104` (expired).

Opening line:

> 你之前配的 Key 现在用不了了（可能已撤销或过期）。
> 麻烦到「方太知味」小程序再领一枚发我，我帮你换掉——旧的不用管，它已经失效了。

Do not retry with the same key, and do not silently fall back to another
device. The `login` command overwrites the old key, so no cleanup is needed.

---

### Scenario C — key is fine, but no devices

`valid: true` with `deviceCount: 0`. Usually means the key belongs to an
account with no bound appliances, or binding happened under a different account.

Opening line:

> Key 配置没问题，但我这边看不到任何已绑定的设备。
> 可能是还没在 App 里添加设备，或者绑定时用的不是同一个方太账号。
> 你可以在「方太知味」小程序里看一下设备列表——如果那边有设备而这边是空的，告诉我，我帮你查。

Do not invent devices or guess device ids.

---

### Scenario D — ready to use

Keep it short: confirm access, show what is possible, state the boundary.

> 你的方太设备已连上（**N 台**）。可以直接说：
> - 「看看我有哪些设备」
> - 「油烟机调到三档」
> - 「蒸烤箱现在多少度」

Then mention the boundary once, only if relevant:

> 我只能操作你自己账号下的设备；解绑、重新配网、OTA 升级这些需要你在小程序里操作。

Do not repeat the boundary in every turn — once per conversation is enough.

---

### Where the key is looked up

First match wins:

| Order | Source | Use case |
|---|---|---|
| 1 | `FOTILE_API_KEY` environment variable | CI, developers |
| 2 | `./.fotile_key` | per-project, gitignored |
| 3 | `~/.fotile/api_key` | normal case, written by `login` |

Optional settings:
- `FOTILE_API_BASE` — defaults to `https://api-test.fotile.com`
  (**staging, internal testing only**). Set it to the production host when
  one is provisioned, e.g. `FOTILE_API_BASE=https://api.fotile.com`.
- `FOTILE_API_PATH` — defaults to `/open-cloud/v1/ai/api`. Only change it for a
  direct cloud-to-cloud deployment.
- `FOTILE_CORP_ID` — **not needed**. The personal-key channel overwrites
  `thirdPartyId` / `granteeId` server-side with its own channel id.

## Device categories and thing models

Before controlling a device, identify its category from the device list and
read the matching thing-model reference. Each reference lists every readable
status field plus every control command, with enum values and ranges.

**Fully documented — safe to control:**

1. Range Hood 油烟机 — [references/range-hood.md](references/range-hood.md)
2. Stove-Steamer-Oven 灶蒸烤箱 — [references/stove-steamer-oven.md](references/stove-steamer-oven.md)
3. Steam-Oven-Microwave 蒸烤微 — [references/steam-oven-microwave.md](references/steam-oven-microwave.md)
4. Dishwasher 洗碗机 — [references/dishwasher.md](references/dishwasher.md)
5. Refrigerator 冰箱 — [references/refrigerator.md](references/refrigerator.md)
6. Sterilizer 消毒柜 — [references/sterilizer.md](references/sterilizer.md)
7. Water Purifier 净水机 — [references/water-purifier.md](references/water-purifier.md)
8. Water Purifier & Heater 净热一体机 — [references/water-purifier-heater.md](references/water-purifier-heater.md)
9. Food Purifier 净食机 — [references/food-purifier.md](references/food-purifier.md)

**Read-only — status only, never send commands:**

10. Gas Stove 灶具 — [references/stove.md](references/stove.md) · only `LeftStoveState` / `RightStoveState`

**No published thing model:**

11. Gas Water Heater 燃气热水器 — [references/water-heater.md](references/water-heater.md)

Cross-category fields (remote auth) live in
[references/remote-auth.md](references/remote-auth.md).

### The `sid` vs `param` trap

A control command has two names: the `sid` you put in the command body, and the
`param` key you put inside `data`. **They are often different.** For example the
refrigerator uses `sid=SetRefrigerationTemp` with `data={"RefrigerationTemp": 8}`.

Each reference marks divergent pairs in bold. Using `sid` as the data key in those
cases fails silently — the device ignores the command and the API may still
return success. Always copy the `param` column.

### The references describe the *standard* model, not every device

A device's reported field set is the authority. The references explain what a
field *means*; they do not guarantee the device reports all of them.

- **Field in the device but not in the reference** — older or special models use
  private fields (e.g. one 灶蒸烤 model reports `Buzzer`, `Blast`, `CavityState`).
  Report the raw value if the user asks, but **do not invent a meaning** and never
  send it as a control command.
- **Field in the reference but not in the device** — that model simply lacks the
  function. Don't claim it exists.
- **Similar names are different fields**: `GestureSwitch` (a setting) vs
  `GestureState` (a live reading); `FlushSwitch` (command) vs `FlushCommand`
  (status). Check which one the device actually reports.

### If a category has no published model

Gas Stove and Gas Water Heater fall in this bucket. When a user asks to control
a category that has no control functions defined, say plainly that it is not
supported and explain that guessing parameters on a kitchen appliance is unsafe.
Gas appliances in particular must never be commanded without a verified model.

Read/write permission legend used in the references:

- **R** — read-only: obtain via status query only, never write.
- **W** — write-only: used in control commands.
- **RW** — read/write: can be queried and controlled.

## Workflow

Follow these steps in order for every control request:

1. **List devices.** Run `python scripts/fotile_api.py devices` (or call
   `FotileAPI().list_devices()`) to get the bound devices, with each device's
   `thirdPartyDevId`, `prodId`, category, online state, and room/name.
2. **Resolve the target device.**
   - If multiple devices match the user's wording (e.g. two range hoods), do
     not guess. List the candidates with their room/name and ask the user to
     choose one.
   - If the target device is offline, report that and do not send a command.
3. **Read the thing model.** Open the category reference and locate the target
   function (`sid`). Confirm it is writable (**W** or **RW**).
4. **Validate the value before sending.**
   - For enums, use only a documented enum value.
   - For numbers, respect `min`, `max`, and `step` (and any scale/unit notes).
   - Never write a read-only (**R**) field. If a value is invalid or out of
     range, ask the user for a valid value rather than clamping silently.
5. **Confirm high-risk actions.** Gas-stove ignition/flame, releasing a child
     lock or door lock, or starting an unattended heating/cooking program
     require an explicit user confirmation for the exact device and setting.
     Only then call `control(..., confirm=True)`.
6. **Send the command.**

   ```bash
   python scripts/fotile_api.py control <prodId> <deviceId> <sid> '{"<sid>": <value>}'
   ```

7. **Verify by reading back.** After a successful command, wait about 1–2
   seconds and query the device status (`... status <deviceId>`). Confirm the
   reported state matches the requested state before telling the user it
   succeeded. If it does not, report the discrepancy and the returned error.

## Command shape

All controls use a single JSON object keyed by the function identifier:

```json
{
  "prodId": "9d956a565f4727625e2f43ab6e0814b7",
  "deviceId": "1156622673",
  "sid": "FanLevel",
  "command": {"FanLevel": 3}
}
```

## Status queries

```bash
# one device
python scripts/fotile_api.py status 1145153645
# multiple devices
python scripts/fotile_api.py status 1145153645 1145153646
```

## Library usage

```python
from fotile_api import FotileAPI

api = FotileAPI()  # reads FOTILE_API_KEY (and optional FOTILE_API_BASE / FOTILE_CORP_ID)

devices = api.list_devices()
status = api.get_status(["1145153645"])
api.control(prod_id="9d956a565f4727625e2f43ab6e0814b7",
            device_id="1156622673", sid="FanLevel", command={"FanLevel": 3})
```

## Errors

The client raises `FotileAPIError` with the business `code`, HTTP status and a
plain-language `hint`. Branch on the code:

| Code | Meaning | What to do |
|---|---|---|
| 40100 / 40101 | missing / invalid key | ask the user for a new key |
| 40103 / 40104 | key revoked / expired | ask the user to issue a new one |
| 40302 | device not bound to this user | re-list devices, confirm the id |
| 40301 | operation not allowed on this channel | explain it is unsupported; do not retry |
| 40305 | this model has no standardized protocol | control is unavailable for this appliance — offer a status read instead |
| 40306 | this function is not mapped for this model | the model is controllable, but not with this sid — read status to see what it supports |
| 42901 | rate limited | the client already retried; ask the user to wait |
| 10011 | device offline | report only; do not queue blind commands |
| 10098 / 10099 | local control / remote auth off | the user must enable it in the FOTILE App |
| 10009 | device not found | re-list and confirm |
| 99999 | server error | retry once, then report |

If a value is rejected as read-only or out of range, correct it from the thing
model before retrying — do not silently clamp.

**On 40305, stop and switch approach.** The code describes the model, not the
request: the appliance is online and bound to the user, but its function set was
never mapped to the standard protocol, so the server has no reliable way to
translate a command into device fields. Retrying, trying a different `sid`, or
falling back to vendor field names will not help — at best the command is
silently dropped, at worst the appliance misreads it. Instead:

1. Read the status (`status <deviceId>`). A filtered, readable subset of fields
   is still returned, so you can usually answer questions about the appliance.
2. Tell the user this model cannot be controlled through the AI channel yet and
   that the FOTILE app (幸福家) or the 「方太知味」 mini-program still works for it.
3. Do not repeat the attempt later in the session unless the user asks again.

**On 40306, the model is fine — the function isn't.** This is the narrower case:
the appliance has a standard protocol, but the specific `sid` you sent is not
covered by that model's protocol mapping. Same category, different model, differs
a lot — one dishwasher may map 3 of the 14 documented commands, another maps all.
So:

1. Do **not** retry the same `sid`, and do not hunt for a synonym.
2. Read the status and look at which fields actually come back — that is the
   honest picture of what this model reports.
3. Tell the user plainly: 「这台设备的这个功能还没有接入 AI 控制」，and offer the
   functions that do work, or point them to the FOTILE app.
4. If the user insists the function exists, it is still correct to say the AI
   channel cannot reach it — the physical machine may well support it.

## Limits and safety

- The key grants access only to the user's own bound devices.
- **Handle the key carefully, but do not refuse to accept it.** The user may
  legitimately hand you the key in chat; store it with `login` and disclose
  the two facts listed in "First run". After storing it:
  - never echo the full key back — refer to it by its prefix
    (`ft-cn-abcd****`);
  - never write it into a tracked file, a commit, or a shell history line;
  - never repeat it in a later message just because the user asks casually.
- Never enable: device removal/unbinding, network provisioning, OTA, or
  account operations.
- Gas ignition, lock release, and unattended heating require explicit
  confirmation (`confirm=true`) in addition to scope authorization.
- Prefer one status read that confirms the change over assuming a successful
  response means the appliance actually changed state.

## Sources

- FOTILE personal-key channel: `POST /open-cloud/v1/ai/api` with
  `Authorization: Bearer <FOTILE_API_KEY>`, namespaces `DeviceDiscovery`,
  `DeviceSnapshot`, `DeviceCommand`.
- Category thing models: the `references/` directory of this skill.
