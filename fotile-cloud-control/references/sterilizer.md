# 消毒柜 (Sterilizer) 物模型参考

> ⚠️ **高温消毒**：启动后腔体升温，不耐高温的塑料/木质餐具不要放。无人看管的程序需用户明确确认。
>
> ⚠️ **开门类设置**（`KnockOpening`）涉及机械弹门，非用户明确要求不要改。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：开关机、启动消毒/烘干模式、暂停/继续/取消、长效保洁、新风、氛围灯、状态提示灯。

❌ **不支持**：上下层独立操控（`UpDoorPositionState` 等是只读状态）。

## 主要物模型字段

| 标识符 | 物模型字段 | 定义 | 读写权限 |
|--------|-----------|------|---------|
| `PowerSwitch` | 开关状态 | 0-关、1-开 | RW |
| `WorkState` | 工作状态 | 0-待机中 1-消毒中 2-瞬消中 3-新风中 4-暖碟中 5-排气中 6-净存中 7-工作完成 | R |
| `WorkMode` | 工作模式 | 0-无 1-消毒 2-瞬消 3-新风 4-暖碟 5-智能 6-负离子烘干 7-快洁 8-杯碟护理 9-奶瓶除菌 | RW |
| `SetWorkTime` | 设置工作时间 | 取值范围:60、90（单位min） | RW |
| `RemainingTime` | 剩余时间 | 取值范围:0~65339（单位min） | R |
| `OperateWork` | 程序控制 | 0-暂停、1-运行、2-取消 | RW |
| `KeepCleanSet` | 设置-长效保洁 | 0-关、1-开 | RW |
| `FreshAirSet` | 设置-新风 | 0-关、1-开 | RW |
| `AmbientLightSet` | 设置-氛围灯 | 0-关、1-开 | RW |
| `StateLightSet` | 设置-工作状态提示灯 | 0-关、1-开 | RW |
| `LongCleanState` | 长效保洁运行状态 | 0-未运行、1-运行 | R |
| `UpDoorPositionState` | 上柜门位置状态 | 0-关 1-开 | R |
| `DownDoorPositionState` | 下柜门位置状态 | 0-关 1-开 | R |
| `WeekNoDisinfect` | 超过7天未消毒提醒 | 0-不提醒、1-超过7天未消毒提醒 | R |
| `ErrorNum` | 故障代码 | 0-正常、1-滤芯认证故障、2-通信故障 | R |
| `KnockOpening` | 设置-敲一敲(开门) | 0-关、1-开 | RW |

## 控制功能说明

> `param` 加粗 = **与 sid 不同名**，`data` 要用 param 里的名字；用错会静默失败。

| 序号 | 功能名称 | 可控制功能标识符(sid) | param | 备注 |
|---|---|---|---|---|
| 1 | 开关机 | `PowerSwitch` | `PowerSwitch` | - |
| 2 | 开启工作模式 | `StartWorkMode` | **`WorkMode` `SetWorkTime`** | WorkMode必传；部分模式SetWorkTime可不传 |
| 3 | 控制程序 | `OperateWork` | `OperateWork` | 工作中可以取消 |
| 4 | 设置长效保洁 | `KeepCleanSet` | `KeepCleanSet` | 关机时可以设置，待机中不能设置 |
| 5 | 设置-新风 | `FreshAirSet` | `FreshAirSet` | - |
| 6 | 设置-氛围灯 | `AmbientLightSet` | `AmbientLightSet` | - |
| 7 | 设置-工作状态提示灯 | `StateLightSet` | `StateLightSet` | - |
| 8 | 设置-敲一敲(开门) | `KnockOpening` | `KnockOpening` | - |

## 控制示例

> data 参数来源物模型可写字段，凡列出的字段都要传，未用的填默认值。

### 开关机

固定 sid=`PowerSwitch`

```json
{"sid":"PowerSwitch","data":{"PowerSwitch":1}}
```

### 开启消毒 60 分钟

sid=`StartWorkMode`，data 里同时给 `WorkMode` 和 `SetWorkTime`

```json
{"sid":"StartWorkMode","data":{"WorkMode":1,"SetWorkTime":60}}
```

### 开启瞬消

部分模式 `SetWorkTime` 可不传

```json
{"sid":"StartWorkMode","data":{"WorkMode":2}}
```

### 暂停 / 继续 / 取消

固定 sid=`OperateWork`

```json
{"sid":"OperateWork","data":{"OperateWork":0}}
```

```json
{"sid":"OperateWork","data":{"OperateWork":1}}
```

```json
{"sid":"OperateWork","data":{"OperateWork":2}}
```

### 长效保洁

```json
{"sid":"KeepCleanSet","data":{"KeepCleanSet":1}}
```

### 新风 / 氛围灯 / 状态提示灯

```json
{"sid":"FreshAirSet","data":{"FreshAirSet":1}}
```

```json
{"sid":"AmbientLightSet","data":{"AmbientLightSet":1}}
```

```json
{"sid":"StateLightSet","data":{"StateLightSet":1}}
```

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 远程授权见 [`remote-auth.md`](remote-auth.md)
