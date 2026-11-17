# 灶蒸烤箱 (Stove Steamer Oven) 物模型参考

> ⚠️ **含燃气灶与高温烹饪**：点火、腔体加热、无人看管的烹饪程序必须先取得用户明确确认。
>
> ⚠️ **`LeftStoveState` / `RightStoveState` 是只读**，控制灶具要用 `LStove*`（智能灶）或 `RStove*`（温控灶）动作指令，不是写状态字段。
>
> ⚠️ 灶具动作类指令影响明火，未与用户逐条确认前不要下发。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：开关机、灯光、启动烹饪模式、设置时间/温度/湿度、快速预热、增压排气、清新换气、暂停/继续/取消。

灶具部分（`LStove*` 智能灶 / `RStove*` 温控灶）仅在用户明确要求并确认真实设备后执行。

❌ **不支持**：直接设置 `LeftStoveState` / `RightStoveState`（只读状态，不是控制入口）。

## 主要物模型字段

| 标识符 | 物模型字段 | 定义 | 读写权限 |
|--------|-----------|------|---------|
| `PowerSwitch` | 开关机 | 1/0 | RW |
| `WorkMode` | 工作模式 | 1000-4000(模式参考总表，点击查看) | RW |
| `Light` | 灯 | 1/0 | RW |
| `SetWorkTime` | 目标工作时间 | 1~599（min） | RW |
| `RemainingTime` | 时间剩余 | 1~599（min） | R |
| `SetWorkTemperature` | 目标温度 | 1~240℃ | RW |
| `CurrentTemperature` | 当前温度 | 1~240℃ | R |
| `SetDownTemperature` | 下层温度 | 1~240℃ | RW |
| `SetAppointmentTime` | 预约开始时间 | 30~3161148（min） | RW |
| `Humidity` | 湿度 | 1~3档 | RW |
| `WorkState` | 工作状态 | 0:无 1:暂停中、2:预热中、3:烹饪中、4:烘烤中、5:烹饪完成、6:预约中、7:保温中 8:除垢中 9:发酵中 10:解冻中 11:烘干中 12:除味中 13:清洁中 14:排气中 15:加热中 | R |
| `QuickHeat` | 快速预热 | 1/0 | RW |
| `KitchenVentSteaming` | 增压排气 | 1/0 | RW |
| `StandaloneKitchenVent` | 独立增压排气 | 1/0 | W |
| `FreshExhaust` | 清新换气 | 1/0 | RW |
| `LeftStoveState` | 左灶状态 | 1/0 | R |
| `RightStoveState` | 右灶状态 | 1/0 | R |
| `WaterShortage` | 缺水提示 | 0-不缺水 1-缺水 | R |
| `DoorSwitch` | 门控状态 | 0-门关 1-门开 | R |
| `TankPlace` | 水箱位置 | 0-水箱已推到位 1-水箱未推到位 | R |
| `OperateWork` | 程序控制 | 1-取消工作 2-继续/立刻开始 3-暂停 4- 取消预约 5- 预约立即开始 | W |
| `AutoAddTime` | 补时状态 | 0-不补时 1-补时 | R |
| `OvertimeFlag` | 加时状态标识 | 0-不加时 1-加时 | R |
| `LockScreen` | 锁屏 | 1/0 | RW |
| `ErrorNum` | 故障码 | 0-无异常、1-蒸汽发器NTC短路_断路、2-控制板与显示板通讯异常、3-水泵短路_断路、4-辅助蒸汽发生器NTC短路_断路、5-腔体探头PT1000或NTC断路、6-腔体探头PT1000或NTC短路 | R |

## 控制功能说明

> `param` 加粗 = **与 sid 不同名**，`data` 要用 param 里的名字；用错会静默失败。

| 序号 | 功能名称 | 可控制功能标识符(sid) | param | 备注 |
|---|---|---|---|---|
| 1 | 开/关机 | `PowerSwitch` | `PowerSwitch` | - |
| 2 | 开关灯 | `Light` | `Light` | - |
| 3 | 设置工作时间 | `SetWorkTime` | `SetWorkTime` | 工作中(WorkState不为0)时有效 |
| 4 | 设置工作温度 | `SetWorkTemp` | **`SetWorkTemperature`** | 工作中(WorkState不为0)时有效 |
| 5 | 设置湿度 | `SetHumidity` | **`Humidity`** | 工作中(WorkState不为0)时有效 |
| 6 | 快速预热 | `QuickHeat` | `QuickHeat` | 烤模式下可用 |
| 7 | 增压排气 | `KitchenVentSteaming` | `KitchenVentSteaming` | - |
| 8 | 独立增压排气 | `StandaloneKitchenVent` | `StandaloneKitchenVent` | 只控制 上报用KitchenVentSteaming |
| 9 | 清新换气 | `FreshExhaust` | `FreshExhaust` | - |
| 10 | 开启模式 | `StartWorkMode` | **`WorkMode`** | 必传，初始值为0. |
| 11 | 控制操作 | `OperateWork` | `OperateWork` | 仅限在开启烹饪后有效 |
| 12 | 设置下温度 | `SetDownTemperature` | `SetDownTemperature` | 双温同烤/分控烤模式下可用，工作中有效 |
| 13 | 蒸烤自动补时开关 | `AutoAddTime` | `AutoAddTime` | 0=不补时,1=自动补时；早餐速蒸/蒸炖模式启动时自动开启 |
| 14 | 烹饪暂停 | `PauseWork` | `PauseWork` | 蒸烤烹饪中使用，进入暂停状态 |
| 15 | 烹饪继续 | `ResumeWork` | `ResumeWork` | 暂停状态下使用，恢复烹饪 |
| 16 | 开始加时 | `StartAddTime` | `StartAddTime` | 烹饪完成后进入加时状态，不带蜂鸣，需延时500ms后发加时启动 |
| 17 | 加时启动 | `AddTimeStart` | **`AddTime`** | 加时分钟数，必传 |
| 18 | 便捷程序/达人模式启动 | `StartSelfMode` | **`SelfModeID`** | 模式名称/达人模式ID字符串，必传 |
| 19 | 智能灶待机/取消 | `LStovePowerSwitch` | **`PowerSwitch`** | 0=关机取消,1=开机待机 |
| 20 | 智能灶设置档位 | `LStoveSetGear` | **`Gear`** | 1=小火,3=中火,5=中大火,7=大火；工作中修改参数使用 |
| 21 | 智能灶设置工作时间 | `LStoveSetTime` | **`SetTime`** | 定时分钟数，0表示不定时 |
| 22 | 智能灶启动手动烹饪 | `LStoveStartManual` | **`Gear`** | 火力档位:1/3/5/7，必传 |
| 23 | 智能灶一键小火 | `LStoveSmallFire` | `LStoveSmallFire` | 直接切换到1档小火，CookMode=28 |
| 24 | 智能灶启动烹饪模式 | `LStoveStartCookMode` | **`CookMode`** | 烹饪模式:1红烧/2热炒/3焖烧/4炖煮/5收汁/16揉面/17打发/18海鲜焖/19酱香卤/20慢煮粥/21老火汤/22水煮/23焯水，必传 |
| 25 | 智能灶进入收汁/保温 | `LStoveKeepWarm` | `LStoveKeepWarm` | 烹饪结束进入收汁托管/保温，CookMode=5 |
| 26 | 智能灶暂停 | `LStovePause` | `LStovePause` | L-SystemState=128暂停状态 |
| 27 | 智能灶继续工作 | `LStoveResume` | `LStoveResume` | 暂停后恢复烹饪，L-SystemState=2 |
| 28 | 智能灶童锁 | `LStoveChildLock` | **`LockState`** | 0=解锁,1=锁定 |
| 29 | 智能灶步骤切换 | `LStoveStepChange` | **`StepPosition`** | 目标步骤索引(从0开始)，下一步传currentStep+1 |
| 30 | 智能灶取消工作 | `LStoveCancel` | `LStoveCancel` | 重置回待机状态，清空调料参数 |
| 31 | 温控灶蒸模式启动 | `RStoveStartSteam` | **`Temperature`** | 设定温度(°C)，必传；前提有火且有锅 |
| 32 | 温控灶炸模式启动 | `RStoveStartFry` | **`Temperature`** | 设定温度(°C)，必传 |
| 33 | 温控灶焖炖模式启动 | `RStoveStartStew` | **`Temperature`** | 设定温度(°C)，必传 |
| 34 | 温控灶煎模式启动 | `RStoveStartFryPan` | **`Temperature`** | 设定温度(°C)，必传 |
| 35 | 温控灶定时关火 | `RStoveTimerOff` | **`SetTime`** | 定时分钟数，RightWorkMode=0不控温 |
| 36 | 温控灶修改参数 | `RStoveModifyParam` | **`WorkMode`** | 工作模式:0定时关火/1蒸/2炸/3炖煮/4煎烙，必传 |
| 37 | 温控灶关火 | `RStovePowerOff` | `RStovePowerOff` | CmdState=2(bit1)右灶关火 |
| 38 | 烹饪直播开关 | `LiveSwitch` | `LiveSwitch` | 0=关闭直播,1=开启直播 |
| 39 | 烹饪录制开关 | `LiveRecordSwitch` | `LiveRecordSwitch` | 0=停止录制,1=开始录制 |
| 40 | 一键关机/取消全部 | `StandbyAllCancel` | **`LampOn`** | 灯是否开启:true开/false关；分4步间隔发送:关灯→取消蒸烤→取消智能灶→关温控灶 |

## 控制示例

> data 参数来源物模型可写字段，凡列出的字段都要传，未用的填默认值。

### 开关机

固定 sid=`PowerSwitch`

```json
{"sid":"PowerSwitch","data":{"PowerSwitch":1}}
```

### 开启烹饪模式

sid=`StartWorkMode`，参数必传，未用的填默认值

```json
{"sid":"StartWorkMode","data":{"WorkMode":1101,"SetWorkTime":30,"SetWorkTemperature":150,"SetAppointmentTime":0,"Humidity":0,"SetDownTemperature":0}}
```

### 暂停 / 继续 / 取消

固定 sid=`OperateWork`

```json
{"sid":"OperateWork","data":{"OperateWork":3}}
```

```json
{"sid":"OperateWork","data":{"OperateWork":2}}
```

```json
{"sid":"OperateWork","data":{"OperateWork":1}}
```

### 开关灯

固定 sid=`Light`

```json
{"sid":"Light","data":{"Light":1}}
```

### 设置工作时间

```json
{"sid":"SetWorkTime","data":{"SetWorkTime":30}}
```

### 设置工作温度

```json
{"sid":"SetWorkTemp","data":{"SetWorkTemperature":180}}
```

### 设置湿度

```json
{"sid":"SetHumidity","data":{"Humidity":1}}
```

### 智能灶：开火待机

sid=`LStovePowerSwitch`，**data 键是 `PowerSwitch`**。0-关机取消、1-开机待机

```json
{"sid":"LStovePowerSwitch","data":{"PowerSwitch":1}}
```

### 智能灶：一键小火

固定 sid=`LStoveSmallFire`

```json
{"sid":"LStoveSmallFire","data":{}}
```

### 智能灶：暂停 / 继续 / 取消

```json
{"sid":"LStovePause","data":{}}
```

```json
{"sid":"LStoveResume","data":{}}
```

```json
{"sid":"LStoveCancel","data":{}}
```

### 温控灶：定时关火

sid=`RStoveTimerOff`，**data 键是 `SetTime`**（分钟）

```json
{"sid":"RStoveTimerOff","data":{"SetTime":30}}
```

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 远程授权见 [`remote-auth.md`](remote-auth.md)
