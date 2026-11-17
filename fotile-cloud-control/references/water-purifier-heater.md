# 净热一体机 (Water Purifier & Heater) 物模型参考

> ⚠️ **涉及热水**：出水温度高。调整出水时长限制前先确认用户意图。
>
> ⚠️ 本机型只覆盖净水与加热水路，不含燃气燃烧控制。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：开关冲洗、设置自动冲洗间隔、设置冷/热水单次最长出水时间。

❌ **不支持**：设定出水温度（物模型未定义温度设定字段）。

## 主要物模型字段

| 标识符 | 物模型字段 | 定义 | 读写权限 |
|--------|-----------|------|---------|
| `WorkState` | 净水水路状态 | 1-待机中、2-冲洗中、3-净水中 | R |
| `FlushCommand` | 冲洗模式 | 0-关、1-开 | RW |
| `FlushingDuration` | 冲洗持续时间 | 取值范围:0~65535（单位min） | R |
| `FlushingTotalTime` | 冲洗总时间 | 取值范围:0~65535（单位min） | R |
| `AutoWashInterval` | 自动冲洗时间间隔 | 取值范围:1~24（单位h，步长为1） | RW |
| `MaxNormalWaterOutTime` | 常温水单次最长出水时间 | 取值范围:0~30（单位min，步长为1）无限制出水为0 | RW |
| `MaxHotWaterOutTime` | 预留热水单次最长出水时间 | 取值范围:1~30（单位min，步长为1） | RW |
| `FilterOneTime` | 滤芯1_PCF_寿命时间-百分比 | 取值范围:0~100 | R |
| `FilterTwoTime` | 滤芯2_MNF_寿命时间-百分比 | 取值范围:0~100 | R |
| `ErrorNum` | 故障代码 | 0-正常、1-传感器故障、2-加热故障、3-通讯故障 | R |

## 控制功能说明

> `param` 加粗 = **与 sid 不同名**，`data` 要用 param 里的名字；用错会静默失败。

| 序号 | 功能名称 | 可控制功能标识符(sid) | param | 备注 |
|---|---|---|---|---|
| 1 | 打开/关闭冲洗模式 | `FlushCommand` | `FlushCommand` | - |
| 2 | 设置自动冲洗时间间隔 | `AutoWashInterval` | `AutoWashInterval` | - |
| 3 | 设置常温水单次最长出水时间 | `MaxNormalWaterOutTime` | `MaxNormalWaterOutTime` | - |
| 4 | 设置预留热水单次最长出水时间 | `MaxHotWaterOutTime` | `MaxHotWaterOutTime` | - |

## 控制示例

> data 参数来源物模型可写字段，凡列出的字段都要传，未用的填默认值。

### 开关冲洗

固定 sid=`FlushCommand`

```json
{"sid":"FlushCommand","data":{"FlushCommand":1}}
```

### 设置自动冲洗间隔

单位小时，1~24

```json
{"sid":"AutoWashInterval","data":{"AutoWashInterval":12}}
```

### 设置常温水单次最长出水时间

单位分钟，0 表示不限制

```json
{"sid":"MaxNormalWaterOutTime","data":{"MaxNormalWaterOutTime":30}}
```

### 设置预留热水单次最长出水时间

单位分钟，1~30

```json
{"sid":"MaxHotWaterOutTime","data":{"MaxHotWaterOutTime":15}}
```

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 远程授权见 [`remote-auth.md`](remote-auth.md)
