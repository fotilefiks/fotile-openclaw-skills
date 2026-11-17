# 冰箱 (Refrigerator) 物模型参考

> ⚠️ **温度设错会导致食材变质**：冷藏 2~8℃、冷冻 -24~-16℃，超范围设备会拒收。改温度前确认用户意图。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：设置冷藏/冷冻温度、速冷速冻、保鲜模式、原鲜解冻、净味模式。

❌ **不支持**：制冰机、变温室等型号专属功能（物模型未定义）。

## 主要物模型字段

| 标识符 | 物模型字段 | 定义 | 读写权限 |
|--------|-----------|------|---------|
| `RefrigerationTemp` | 设置冷藏室温度 | 2~8（摄氏度） | RW |
| `FreezingTemp` | 设置冷冻室温度 | -24~-16（摄氏度） | RW |
| `RapidCoolingMode` | 加速制冷模式 | 0表示关闭，1表示冷藏室速冷，2表示冷冻室速冻，3表示二者同时开启 | RW |
| `FreshKeepingType` | 保鲜模式 | 0表示关闭，1表示氮气保鲜，2表示休眠保鲜，3表示二者同时开启 | RW |
| `FreezedRoom` | 原鲜解冻 | 1-微冻、2-还原解冻、3-冰鲜（既不解冻也不微冻，即原鲜解冻按键未开启状态） | RW |
| `UnfreezeTime` | 还原解冻倒计时 | 0-240（分钟） | R |
| `DeodorizationMode` | 净味模式 | 0表示关闭，1表示新风净味，2表示即时新风，3表示二者同时开启 | RW |
| `DoorClose` | 关门提醒 | 0-无 1-左冷藏开门大于4分钟、2-右冷藏开门大于4分钟、3-冷冻门1开门大于4分钟、4-冷冻门2开门大于4分钟 | R |
| `ErrorNum` | 设备故障 | 0-无 1-CE-显示板通讯故障、2-C1-多功能板通讯故障、3-C2-变频板通讯故障、4-BF-WiFi模块通讯故障 | R |

## 控制功能说明

> `param` 加粗 = **与 sid 不同名**，`data` 要用 param 里的名字；用错会静默失败。

| 序号 | 功能名称 | 可控制功能标识符(sid) | param | 备注 |
|---|---|---|---|---|
| 1 | 设置冷藏室温度 | `SetRefrigerationTemp` | **`RefrigerationTemp`** | - |
| 2 | 设置冷冻室温度 | `SetFreezingTemp` | **`FreezingTemp`** | - |
| 3 | 设置加速制冷模式 | `SetRapidCoolingMode` | **`RapidCoolingMode`** | 0表示关闭，1表示冷藏室速冷，2表示冷冻室速冻，3表示二者同时开启 |
| 4 | 设置保鲜类型 | `SetFreshKeepingType` | **`FreshKeepingType`** | 0表示关闭，1表示氮气保鲜，2表示休眠保鲜，3表示二者同时开启 |
| 5 | 原鲜解冻 | `SetFreezedRoom` | **`FreezedRoom`** | - |
| 6 | 设置净味模式 | `SetDeodorizationMode` | **`DeodorizationMode`** | 0表示关闭，1表示新风净味，2表示即时新风，3表示二者同时开启 |

## 控制示例

> data 参数来源物模型可写字段，凡列出的字段都要传，未用的填默认值。

### 设置冷藏室温度

sid=`SetRefrigerationTemp`，**data 键是 `RefrigerationTemp`**（去掉 Set 前缀）

```json
{"sid":"SetRefrigerationTemp","data":{"RefrigerationTemp":4}}
```

### 设置冷冻室温度

```json
{"sid":"SetFreezingTemp","data":{"FreezingTemp":-18}}
```

### 加速制冷

0-关闭、1-冷藏速冷、2-冷冻速冻、3-同时开启

```json
{"sid":"SetRapidCoolingMode","data":{"RapidCoolingMode":1}}
```

### 保鲜模式

0-关闭、1-氮气保鲜、2-休眠保鲜、3-同时开启

```json
{"sid":"SetFreshKeepingType","data":{"FreshKeepingType":1}}
```

### 原鲜解冻

1-微冻、2-还原解冻、3-冰鲜

```json
{"sid":"SetFreezedRoom","data":{"FreezedRoom":2}}
```

### 净味模式

0-关闭、1-新风净味、2-即时新风、3-同时开启

```json
{"sid":"SetDeodorizationMode","data":{"DeodorizationMode":1}}
```

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 远程授权见 [`remote-auth.md`](remote-auth.md)
