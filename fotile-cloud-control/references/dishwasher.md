# 洗碗机 (Dishwasher) 物模型参考

> ⚠️ **运行中开门会喷水**：下发前确认 `DoorLock` 已锁；清洗/烘干途中取消（`OperateWork`=1）会中断程序且不可续。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：开关机、启动清洗模式、暂停/继续/取消、预约、漂洗剂与软化盐挡位、保洁存储、附加模式。

❌ **不支持**：敲击开门（`KnockOpening`）会真的弹开门，非用户明确要求不要下发。

## 主要物模型字段

| 标识符 | 物模型字段 | 定义 | 读写权限 |
|--------|-----------|------|---------|
| `PowerSwitch` | 开关机 | 0/1 | RW |
| `WorkState` | 工作状态 | 0-关机 1-待机 2-清洗中 3-暂停中 4-烘干中 5-存储中 6-预约中 7-程序结束 | R |
| `OperateWork` | 程序控制 | 1-取消 2-继续/立刻开始 3-暂停 | W |
| `WorkMode` | 清洗模式 | 0-无 1-日常洗 2-速净洗 3-超净洗 4-晶亮洗 5-自清洁 6-节能洗 7-智能洗 8-母婴洗 9-静音洗 10-煲仔锅 11-蒸汽消杀 12-洗烘存 13-暖碟 14-独立烘干 15-预冲洗 16-蒸汽清洁 17-餐前烫碗 18-超快洗 19-果蔬清洗 轻 20-果蔬清洗 中 21-果蔬清… | RW |
| `LowerQuickWash` | 下层速洗 | 0/1（关闭/开启） | RW |
| `SteamSterilization` | 蒸汽除菌 | 0/1（关闭/开启） | RW |
| `StrengthenDrying` | 加强烘干 | 0/1（关闭/开启） | RW |
| `StrengthenRinsing` | 加强漂洗 | 0/1（关闭/开启） | RW |
| `CleaningStorage` | 保洁存储 | 0/1（关闭/开启） | RW |
| `StoreTotalTime` | 保洁存储时长 | 0-99（天) | RW |
| `AppointmentHour` | 预约小时 | 0-47(小时，超过23则为明天) | RW |
| `AppointmentMinute` | 预约分钟 | 0 | RW |
| `CleanRemainTime` | 清洗剩余时间 | 0-600（分钟） | R |
| `StoreRemainTime` | 保洁存储剩余时间 | 0-240（小时） | R |
| `DetergentLevel` | 漂洗剂挡位 | 0-6，int，步长为1 | RW |
| `SoftensaltLevel` | 软化盐挡位 | 0-7，int，步长为1 | RW |
| `DoorLock` | 门锁状态 | 0/1（关闭/开启） | R |
| `Reminder` | 系统提示 | 0-无、1-缺盐、2-缺漂洗剂、3-缺盐_缺漂洗剂、4-缺洗碗液、5-缺盐_缺洗碗液、6-缺漂洗剂_缺洗碗液、7-缺盐_缺漂洗剂_缺洗碗液 | R |
| `ErrorNum` | 故障代码 | 0-无故障 224-电机通讯故障、225-门锁故障、226-水流量小、227-排水不畅、228-加热盘不工作、229-温度传感器短路或开路、230-门锁电机故障、231-隔板电机故障、232-干烧保护、236-通信异常、241-漏水报警、243-溢水报警、244-高温报警、245-电机过压欠压、24… | R |
| `PowKeyMode` | 电源键开机设置 | 0-长按开关机 1-短按开关机 | - |
| `KnockGears` | 敲击开门力度 | 1-8档，int，步长为1 | RW |
| `KnockTime` | 敲击开门反应时间 | 1-3档，步长为1 | RW |
| `BreathEffect` | 剩余时间显示方式设置 | 0-敲一下门板显示 1-一直显示（呼吸灯闪烁） 2-剩余一小时后显示 3-一直显示（呼吸灯常亮） | RW |
| `ConvBowlPlace` | 便捷摆碗设置 | 0-开门后碗架不推出 1-开门后碗架推出一半 2-开门后碗架全部推出（默认） | RW |
| `UpperQuickWash` | 上层速吸 | 0/1（关闭/开启） | RW |
| `LightLoadMode` | 轻载模式 | 0/1（关闭/开启） | RW |
| `AutoOffTime` | 自动关机时间设置 | 0-99（min），步长为1 | RW |
| `AirDryMode` | 透气烘干 | 0/1（关闭/开启） | RW |
| `AutoDrain` | 排水中 | 0/1（关闭/开启） | RW |

## 控制功能说明

> `param` 加粗 = **与 sid 不同名**，`data` 要用 param 里的名字；用错会静默失败。

| 序号 | 功能名称 | 可控制功能标识符(sid) | param | 备注 |
|---|---|---|---|---|
| 1 | 开关机 | `PowerSwitch` | `PowerSwitch` | - |
| 2 | 开启清洗模式 | `StartWorkMode` | **`WorkMode` `WorkState` `LowerQuickWash` `UpperQuickWash` `SteamSterilization` `StrengthenDrying` `StrengthenRinsing` `CleaningStorage` `StoreTotalTime`** | param参数字段均必传，初始值为0 洗碗机清洗分为主功能和附加功能 例如开启主模型日常洗，附加模式为下层速洗功能，指令为： |
| 3 | 控制程序 | `OperateWork` | `OperateWork` | 清洗中/烘干中/存储中（WorkState=2/4/5时），可以暂停和取消； 例如：暂停指令为： |
| 4 | 预约清洗模式 | `AppointmentWorkMode` | **`WorkMode` `LowerQuickWash` `UpperQuickWash` `SteamSterilization` `StrengthenDrying` `StrengthenRinsing` `CleaningStorage` `StoreTotalTime` `AppointmentHour` `AppointmentMinute`** | param参数字段均必传，初始值为0. 设备在预约状态 要取消预约才能再发预约指令 我看现在一直在发请求 例如： 预约今天晚上8.30开启日常洗附加模式为下层速洗 |
| 5 | 设置漂洗剂挡位 | `SetDetergentLevel` | **`DetergentLevel`** | - |
| 6 | 设置软化盐挡位 | `SetSoftensaltLevel` | **`SoftensaltLevel`** | - |
| 7 | 开关机按键设置 | `PowKeyMode` | `PowKeyMode` | - |
| 8 | 设置保洁存储时间 | `SetStoreRemainTime` | **`LowerQuickWash`** | 下层速洗 |
| 9 | 敲击开门设置 | `KnockOpening` | **`KnockGears`** | 敲击开门力度 |
| 10 | 剩余时间显示方式设置 | `BreathEffect` | `BreathEffect` | - |
| 11 | 便捷摆碗设置 | `ConvBowlPlace` | `ConvBowlPlace` | - |
| 12 | 自动关机时间设置 | `AutoOffTime` | `AutoOffTime` | - |
| 13 | 透气烘干 | `AirDryMode` | `AirDryMode` | - |
| 14 | 排水中 | `AutoDrain` | `AutoDrain` | 设备关闭才可以进行操作 |

## 控制示例

> data 参数来源物模型可写字段，凡列出的字段都要传，未用的填默认值。

### 开启日常洗（含下层速洗）

固定 sid=`StartWorkMode`，param 列出的字段全部要传

```json
{"sid":"StartWorkMode","data":{"WorkMode":1,"LowerQuickWash":1,"SteamSterilization":0,"StrengthenDrying":0,"StrengthenRinsing":0,"CleaningStorage":0,"StoreTotalTime":0}}
```

### 暂停 / 继续 / 取消

固定 sid=`OperateWork`。1-取消、2-继续/立刻开始、3-暂停

```json
{"sid":"OperateWork","data":{"OperateWork":3}}
```

```json
{"sid":"OperateWork","data":{"OperateWork":2}}
```

```json
{"sid":"OperateWork","data":{"OperateWork":1}}
```

### 预约清洗

固定 sid=`AppointmentWorkMode`

```json
{"sid":"AppointmentWorkMode","data":{"WorkMode":1,"LowerQuickWash":1,"AppointmentHour":20,"AppointmentMinute":30,"StrengthenDrying":0,"CleaningStorage":0,"StrengthenRinsing":0,"SteamSterilization":0,"StoreTotalTime":0}}
```

### 设置漂洗剂挡位

sid=`SetDetergentLevel`，data 键是 `DetergentLevel`

```json
{"sid":"SetDetergentLevel","data":{"DetergentLevel":3}}
```

### 设置软化盐挡位

```json
{"sid":"SetSoftensaltLevel","data":{"SoftensaltLevel":4}}
```

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 远程授权见 [`remote-auth.md`](remote-auth.md)
