# 油烟机 (Range Hood) 物模型参考

> ⚠️ **强档噪声大，升降属机械动作**：调档前确认用户在旁；升降（`CtlUpDown`）运行中不要反向操作。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：开关机、灯光、档位、强吸、智能巡航、每日换气、延时关机、手势、锁屏、升降、制冷模块、联动设置。

❌ **不支持**：拆洗档（`FanLevel`=7）仅部分型号支持，下发前先看设备上报的枚举范围。

## 主要物模型字段

| 标识符 | 物模型字段 | 定义 | 读写权限 |
|--------|-----------|------|---------|
| `PowerSwitch` | 开关机/总电源 | 1/0 | RW |
| `RangeHoodPower` | 烟机分电源 | 1/0 | RW |
| `FanLevel` | 烟机档位 | 0-停止 1-弱档、2-自动档、3-强档、4-智感净味/智能巡航/增压净烟 5-每日换气 6-爆炒 7-拆洗 | RW |
| `StrongModeStatus` | 强吸模式 | 0-未启用 1-左强吸、2-右强吸 | RW |
| `Light` | 灯 | 1/0 | RW |
| `CoolingPower` | 制冷分电源 | 1/0 | RW |
| `CoolingMode` | 制冷模式 | 1-送风、2-制冷、3-除湿 | RW |
| `CoolingAirflow` | 制冷风速 | 1-低、2-中、3-高 | RW |
| `CoolingSwing` | 启用摆风 | 1/0 | RW |
| `CoolingTemperature` | 制冷温度 | 16-32 | RW |
| `LinkedCookingEnable` | 烹饪联动功能状态 | -1:未配置(仅状态上报) 1:已启用 0:已禁用 | RW |
| `LinkedStoveEnable` | 烟灶联动功能状态 | -1:未配置(仅状态上报) 1:已启用 0:已禁用 | RW |
| `LinkedCookingLightOn` | 烹饪联动-烟机灯 | 1/0 | RW |
| `LinkedCookingFanLevel` | 烹饪联动-烟机挡位 | 1-弱、2-自动、3-强档、4-增压净烟/智感净烟 | RW |
| `RangeLinkageStove` | 烟灶联动状态 | 仅上报 0-未配对、1-联动配对中(时间很短) 2-联动已配对(灶具开启中)、3-联动已配对(灶具未开启) | R |
| `LinkSteamOven` | 烟亨联动状态 | 0-未配对 1-联动配对中(时间很短) 2-联动已配对(灶具开启中)、3-联动已配对(灶具未开启) | R |
| `LinkedCoolingEnable` | 制冷联动功能状态 | -1:未配置(仅状态上报) 1:已启用 0:已禁用 | RW |
| `LinkedCoolingDelayMinutes` | 制冷联动-延迟关闭时间 | 秒数 | RW |
| `EnableClockDisplayDuringPowerOff` | 关机后显示时间 | - | RW |
| `TotalRunningTime` | 烟机运行总时长 | - | R |
| `IntelligentCruiseSwitch` | 智能巡航 | 1/0 | RW |
| `VentilationSwitch` | 每日换气 | 1/0 | RW |
| `AirQuality` | 空气质量 | 0-优秀、1-良好、2-较差、3-很差、99-检测中 | R |
| `EnableDelayPowerOff` | 是否启用延时关机 | 1/0 | RW |
| `Delay` | 延时关机(手动触发) | 0/1，在控制指令中1表示手动触发延时关机，0表示直接关机 0/1，在状态里面，表示延迟是否在运行 | RW |
| `DelayTime` | 延时关机时间 | 0~99（分钟） | RW |
| `DelayCountDown` | 延时关机倒计时 | 0~99（分钟） | R |
| `GestureSwitch` | 手势感应 | 1/0 | RW |
| `LockScreen` | 锁屏 | 1/0 | RW |
| `WorkState` | 工作状态 | 0-无(待机) 1-弱档、2-增压净烟/自动挡/智感净烟 3-强档、4-换气中、5-延迟关机中、6-爆炒 7-自选风量 8-智感净味烟/智感换气 9-拆洗 | R |
| `CtlUpDown` | 升降控制 | 1上升；2下降：3暂停 | RW |
| `UpDownLock` | 升降锁定 | 1/0 | RW |
| `ErrorNum` | 故障码 | 0:无异常、/ | R |
| `UpDownPosition` | 升降位置 | 0~100 | R |
| `OffStateScreen` | 关机亮屏 | 1/0 | RW |
| `LightScope` | 灯光亮度 | 0-99 | RW |

## 控制功能说明

> `param` 加粗 = **与 sid 不同名**，`data` 要用 param 里的名字；用错会静默失败。

| 序号 | 功能名称 | 可控制功能标识符(sid) | param | 备注 |
|---|---|---|---|---|
| 1 | 开关机/总电源 | `PowerSwitch` | `PowerSwitch` | 1/0 |
| 2 | 烟机分电源 | `RangeHoodPower` | `RangeHoodPower` | 1/0 |
| 3 | 烟机档位 | `FanLevel` | `FanLevel` | - |
| 4 | 强吸模式 | `StrongModeStatus` | `StrongModeStatus` | 0-未启用 1-左强吸; 2-右强吸 |
| 5 | 灯 | `Light` | `Light` | 1/0 |
| 6 | 制冷分电源 | `CoolingPower` | `CoolingPower` | 1/0 |
| 7 | 制冷模式 | `CoolingMode` | `CoolingMode` | 1-送风; 2-制冷; 3-除湿 |
| 8 | 制冷风速 | `CoolingAirflow` | `CoolingAirflow` | 1-低; 2-中; 3-高 |
| 9 | 启用摆风 | `CoolingSwing` | `CoolingSwing` | 1/0 |
| 10 | 制冷温度 | `CoolingTemperature` | `CoolingTemperature` | 16-32 |
| 11 | 烹饪联动功能状态 | `LinkedCookingEnable` | `LinkedCookingEnable` | -1:未配置(仅状态上报) 1:已启用 0:已禁用 |
| 12 | 烟灶联动功能状态 | `LinkedStoveEnable` | `LinkedStoveEnable` | -1:未配置(仅状态上报) 1:已启用 0:已禁用 |
| 13 | 烹饪联动-烟机灯 | `LinkedCookingLightOn` | `LinkedCookingLightOn` | 1/0 |
| 14 | 烹饪联动-烟机挡位 | `LinkedCookingFanLevel` | `LinkedCookingFanLevel` | 1-弱; 2-自动; 3-强档 |
| 15 | 制冷联动功能状态 | `LinkedCoolingEnable` | `LinkedCoolingEnable` | -1:未配置(仅状态上报) 1:已启用 0:已禁用 |
| 16 | 制冷联动-延迟关闭时间 | `LinkedCoolingDelayMinutes` | `LinkedCoolingDelayMinutes` | 分钟 |
| 17 | 关机后显示时间 | `EnableClockDisplayDuringPowerOff` | `EnableClockDisplayDuringPowerOff` | - |
| 18 | 烟机运行总时长 | `TotalRunningTime` | `TotalRunningTime` | - |
| 19 | 智能巡航 | `IntelligentCruiseSwitch` | `IntelligentCruiseSwitch` | 1/0 |
| 20 | 每日换气 | `VentilationSwitch` | `VentilationSwitch` | 1/0 |
| 21 | 是否启用延时关机 | `EnableDelayPowerOff` | `EnableDelayPowerOff` | 1/0（启用后默认值10分钟） |
| 22 | 延时关机(手动触发) | `Delay` | `Delay` | 0/1，在控制指令中1表示手动触发延时关机，0表示直接关机 0/1，在状态里面，表示延迟是否在运行 |
| 23 | 延时关机时间 | `DelayTime` | `DelayTime` | 0~99（分钟） |
| 24 | 手势感应 | `GestureSwitch` | `GestureSwitch` | 1/0 |
| 25 | 锁屏 | `LockScreen` | `LockScreen` | 1/0 |
| 26 | 升降控制 | `CtlUpDown` | `CtlUpDown` | 1上升；2下降：3暂停 |
| 27 | 升降锁定 | `UpDownLock` | `UpDownLock` | 1/0 |
| 28 | 关机亮屏设置 | `OffStateSwitch` | **`OffStateScreen`** | 1/0 |

## 控制示例

> data 参数来源物模型可写字段，凡列出的字段都要传，未用的填默认值。

### 开灯 / 关灯

固定 sid=`Light`

```json
{"sid":"Light","data":{"Light":1}}
```

```json
{"sid":"Light","data":{"Light":0}}
```

### 开关机

固定 sid=`PowerSwitch`

```json
{"sid":"PowerSwitch","data":{"PowerSwitch":1}}
```

### 调节档位

固定 sid=`FanLevel`。0-停止、1-弱档、2-自动档、3-强档、4-智感净味/智能巡航、5-每日换气、6-爆炒、7-拆洗

```json
{"sid":"FanLevel","data":{"FanLevel":3}}
```

### 强吸模式

固定 sid=`StrongModeStatus`。0-未启用、1-左强吸、2-右强吸

```json
{"sid":"StrongModeStatus","data":{"StrongModeStatus":1}}
```

### 开启智能巡航

固定 sid=`IntelligentCruiseSwitch`

```json
{"sid":"IntelligentCruiseSwitch","data":{"IntelligentCruiseSwitch":1}}
```

### 延时关机

先启用再触发：`EnableDelayPowerOff`=1 → `DelayTime` 设分钟 → `Delay`=1 触发

```json
{"sid":"EnableDelayPowerOff","data":{"EnableDelayPowerOff":1}}
```

```json
{"sid":"DelayTime","data":{"DelayTime":5}}
```

```json
{"sid":"Delay","data":{"Delay":1}}
```

### 升降控制

固定 sid=`CtlUpDown`。1-上升、2-下降、3-暂停

```json
{"sid":"CtlUpDown","data":{"CtlUpDown":2}}
```

### 制冷模块

```json
{"sid":"CoolingPower","data":{"CoolingPower":1}}
```

```json
{"sid":"CoolingMode","data":{"CoolingMode":2}}
```

```json
{"sid":"CoolingTemperature","data":{"CoolingTemperature":26}}
```

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 远程授权见 [`remote-auth.md`](remote-auth.md)
