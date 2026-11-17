# 远程授权 (Remote Auth) 物模型参考

> 跨品类通用，所有设备都适用。这两个字段决定「能不能远程控制」，下发控制前必须先看。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：在用户明确要求时远程开启授权。

❌ **不支持**：远程关闭授权。`RemoteAuth` 只能远程开启，关闭要在设备端或方太 App 操作。

## 主要物模型字段

| 标识符 | 物模型字段 | 定义 | 读写权限 |
|--------|-----------|------|---------|
| `RemoteAuth` | 远程授权 | 0-关闭、1-开启 | RW |
| `LocalControlOnly` | 是否本地操作 | 0-关闭、1-开启（1 表示设备本地控制中） | R |

## 控制功能说明

> 注意：控制指令的 sid 是 `RemoteAuthSwitch`，**data 键是 `RemoteAuth`** —— 不是同名字段直接下发。

| 序号 | 功能名称 | 可控制功能标识符(sid) | param | 备注 |
|---|---|---|---|---|
| 1 | 开启远程授权 | `RemoteAuthSwitch` | **`RemoteAuth`** | 仅支持远程开启，不允许远程关闭 |

## 控制示例

### 开启远程授权

```json
{"sid":"RemoteAuthSwitch","data":{"RemoteAuth":1}}
```

## 控制前的判断顺序

1. 读状态，取 `RemoteAuth` 与 `LocalControlOnly`。
2. `RemoteAuth=0` → 返回 **10099**（device not remote auth）。先引导用户开启授权，或代发上面的 `RemoteAuthSwitch`。
3. `LocalControlOnly=1` → 用户在设备上开了本地控制，返回 **10098**。只能让用户去设备端退出，远程无法解除。

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 错误码含义见 [`SKILL.md`](../SKILL.md) 的 Errors 一节
