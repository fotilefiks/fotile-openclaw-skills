# 净水机 (Water Purifier) 物模型参考

> ⚠️ **涉及饮用水**：冲洗与滤芯操作影响出水安全，改动前向用户说明影响。
>
> ⚠️ 部分设备上报 `MAXNormalWaterOutTime`（全大写 MAX），与物模型定义的 `MaxNormalWaterOutTime` 写法不同，按设备实际上报的字段名下发。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：开关冲洗、设置自动冲洗间隔、冷/热水出水时长、制冰、软水再生、连续用水保护、息屏、语音、咖啡机参数。

❌ **不支持**：直接设定出水温度（物模型只允许设置出水时长）。

## 主要物模型字段

| 标识符 | 物模型字段 | 定义 | 读写权限 |
|--------|-----------|------|---------|
| `WorkState` | 净水水路状态 | 1-待机中、2-冲洗中、3-净水中、4-制冰中 5-冲洗完成 6-上电冲洗 | R |
| `FlushCommand` | 冲洗模式 | 0-关、1-开 | W |
| `FlushingDuration` | 冲洗持续时间 | 取值范围:0~65535（单位秒） | R |
| `FlushingTotalTime` | 冲洗总时间 | 取值范围:0~65535（单位秒） | R |
| `FlushingRemainingTime` | 冲洗剩余时间 | 取值范围:0~65535（单位秒） | - |
| `AutoWashInterval` | 自动冲洗时间间隔 | 取值范围:1~24（单位h，步长为1） | RW |
| `MaxNormalWaterOutTime` | 常温水单次最长出水时间 | 取值范围:0~30（单位min，步长为1）无限制出水为0 | RW |
| `MaxHotWaterOutTime` | 热水单次最长出水时间 | 取值范围:1~30（单位min，步长为1） | RW |
| `FilterOneTime` | 滤芯1_PCF_寿命时间-百分比 | 取值范围:0~100 | R |
| `FilterTwoTime` | 滤芯2_MNF_寿命时间-百分比 | 取值范围:0~100 | R |
| `FilterStatus` | 滤芯即将到期情况 | 0-无滤芯即将到期、1-滤芯1-PCC_即将到期、2-滤芯2-MNF_即将到期、3-滤芯1-PCC_滤芯2-MNF_即将到期 | R |
| `FilterExpired` | 滤芯到期情况 | 0-无滤芯到期、1-滤芯1_PCC_已到期、2-滤芯2_MNF_已到期、3-滤芯1_PCC_滤芯2_MNF_已到期 | R |
| `ErrorNum` | 故障代码/异常信息 | 0-正常、1-传感器故障、2-加热故障、3-通讯故障、4-制冰槽故障、5-储水箱温度传感器故障、6-散热水箱温度传感器故障、7-漏水故障 | R |
| `CoolingEnable` | 制冰 | 0-关、1-开 | RW |
| `IceMakMode` | 制冰模式-设置 | 0-大冰模式，1-小冰模式 | RW |
| `IceMakDura` | 单次制冰最长时间 -设置 | 1~30h/ 无限制 | RW |
| `CupFullStop` | 杯满即停-设置 | 0-关、1-开 | RW |
| `RestScreenState` | 息屏模式-设备 | 0-全屏微亮 1-仅出水键微亮 2-全灭状态 | RW |
| `VoiceEnable` | 语音播报-设置 | 0-关、1-开 | RW |
| `WCTSta` | 污水盒状态 | 0-正常 1-不在位 2-已满 | - |
| `IceBox` | 制冰盒 | 0-待机（冰未满）、1-制冰中、2-冰满、3-压缩机保护（无法制冰） | - |
| `RegenModeSwitch` | 软水再生模式 | 0-关、1-开 | RW |
| `InWaterHardness` | 进水硬度 | 取值范围：2-1000（单位mg/L） | RW |
| `SaltComsumeMode` | 耗盐模式 | 0-标准模式 1-强力模式 2-节盐模式 | RW |
| `AutoRegenDayInterval` | 自动再生间隔天数-设置 | 取值范围：15-60（单位天） | RW |
| `AutoRegenStartTime` | 自动再生开始时间-设置 | 取值范围：0-1799（单位min，步长为1） | RW |
| `LongWaterProtect` | 连续用水保护 | 0-关、1-开 | RW |
| `LongWaterTime` | 连续用水时间 | 取值范围：30-120（单位min，步长为5） | RW |

## 控制功能说明

> `param` 加粗 = **与 sid 不同名**，`data` 要用 param 里的名字；用错会静默失败。

| 序号 | 功能名称 | 可控制功能标识符(sid) | param | 备注 |
|---|---|---|---|---|
| 1 | 打开/关闭冲洗模式 | `FlushSwitch` | **`FlushCommand`** | - |
| 2 | 设置自动冲洗时间间隔 | `AutoWashInterval` | `AutoWashInterval` | - |
| 3 | 设置常温水单次最长出水时间 | `MaxNormalWaterOutTime` | `MaxNormalWaterOutTime` | - |
| 4 | 设置热水单次最长出水时间 | `MaxHotWaterOutTime` | `MaxHotWaterOutTime` | - |
| 5 | 制冰 | `CoolingSwitch` | **`CoolingEnable`** | - |
| 6 | 制冰模式-设置 | `IceMakModeSet` | **`IceMakMode`** | - |
| 7 | 单次制冰最长时间 -设置 | `MaxIceTimesSet` | **`IceMakDura`** | - |
| 8 | 杯满即停-设置 | `CupFullSwitchSet` | **`CupFullStop`** | - |
| 9 | 息屏模式-设备 | `RestScreenModeSet` | **`RestScreenState`** | - |
| 10 | 语音播报-设置 | `VoiceSwitch` | **`VoiceEnable`** | - |
| 11 | 设置咖啡温度 | `SetCoffeeTemperatureLevel` | **`CoffeeTemperatureLevel`** | 1-标准；2-高温；3-极高温 |
| 12 | 设置咖啡机待机时长 | `SetCoffeeStandbyTime` | **`CoffeeStandbyTime`** | 单位：分钟 |
| 13 | 软水再生模式 | `RegenModeSwitch` | `RegenModeSwitch` | - |
| 14 | 进水硬度 | `InWaterHardness` | `InWaterHardness` | 单位：mg/L |
| 15 | 耗盐模式 | `SaltComsumeMode` | `SaltComsumeMode` | 0-标准模式 1-强力模式 2-节盐模式 |
| 16 | 自动再生间隔天数-设置 | `AutoRegenDayInterval` | `AutoRegenDayInterval` | 单位：天 |
| 17 | 自动再生开始时间-设置 | `AutoRegenStartTime` | `AutoRegenStartTime` | 单位：分钟 |
| 18 | 连续用水保护 | `LongWaterProtect` | `LongWaterProtect` | - |
| 19 | 连续用水时间 | `LongWaterTime` | `LongWaterTime` | 单位：分钟 |

## 控制示例

> data 参数来源物模型可写字段，凡列出的字段都要传，未用的填默认值。

### 开关冲洗

sid=`FlushSwitch`，**data 键是 `FlushCommand`**

```json
{"sid":"FlushSwitch","data":{"FlushCommand":1}}
```

### 设置自动冲洗间隔

单位小时，1~24

```json
{"sid":"AutoWashInterval","data":{"AutoWashInterval":8}}
```

### 设置常温水单次最长出水时间

```json
{"sid":"MaxNormalWaterOutTime","data":{"MaxNormalWaterOutTime":30}}
```

### 开/关制冰

sid=`CoolingSwitch`，**data 键是 `CoolingEnable`**

```json
{"sid":"CoolingSwitch","data":{"CoolingEnable":1}}
```

### 设置制冰模式

sid=`IceMakModeSet`，**data 键是 `IceMakMode`**。0-大冰、1-小冰

```json
{"sid":"IceMakModeSet","data":{"IceMakMode":1}}
```

### 连续用水保护

```json
{"sid":"LongWaterProtect","data":{"LongWaterProtect":1}}
```

```json
{"sid":"LongWaterTime","data":{"LongWaterTime":60}}
```

### 语音播报

sid=`VoiceSwitch`，**data 键是 `VoiceEnable`**

```json
{"sid":"VoiceSwitch","data":{"VoiceEnable":1}}
```

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 远程授权见 [`remote-auth.md`](remote-auth.md)
