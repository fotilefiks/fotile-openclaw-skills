# 净食机 (Food Purifier) 物模型参考

> ⚠️ **排水会中断当前净化**：`SetAutoDrain` 一旦开启，正在跑的程序会被取消且不续跑。
>
> ⚠️ **开机状态下排水可能被拒**，需先关机。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：开关机、启动净化模式、暂停/继续/取消、排水、气泡设置。

❌ **不支持**：水位、水质等传感器字段（物模型未定义）。

## 主要物模型字段

| 标识符 | 物模型字段 | 定义 | 读写权限 |
|--------|-----------|------|---------|
| `PowerSwitch` | 开关状态 | 0-关、1-开 | RW |
| `WorkState` | 工作状态 | 0-关机中 1-待机中 2-清洁中 3-浸泡中 4-暂养中 5-暂停 6-工作完成 | R |
| `WorkMode` | 工作模式 | 0-无 1-果蔬净洗 - 轻 2-果蔬净洗 - 中 3-果蔬净洗- 高 4-果蔬净洗 - 叶菜类 5-果蔬净洗 - 根茎类 6-果蔬净洗 - 浆果类 7-果蔬净洗 - 深层洗 8-海鲜肉类 - 轻 9-海鲜肉类 - 中 10-海鲜肉类 - 强 11-海鲜肉类 - 小龙虾 12-海鲜肉类 - 肉类 1… | RW |
| `SetWorkTime` | 工作时间 | 15/30/60/90/120/150/180/210/240 | RW |
| `RemainingTime` | 剩余时间 | 取值范围:0~65339（单位min） | R |
| `AutoDrain` | 排水中 | 0-关、1-开 | - |
| `OperateWork` | 程序控制 | 1-取消工作 2-继续/立刻开始 3-暂停 | RW |
| `AddBubble` | 设置- 是否添加气泡 | 0-关、1-开 | RW |
| `ErrorNum` | 故障代码 | 0-正常、1-请将槽体推到位 | R |

## 控制功能说明

> `param` 加粗 = **与 sid 不同名**，`data` 要用 param 里的名字；用错会静默失败。

| 序号 | 功能名称 | 可控制功能标识符(sid) | param | 备注 |
|---|---|---|---|---|
| 1 | 开关机 | `PowerSwitch` | `PowerSwitch` | - |
| 2 | 开启工作模式 | `StartWorkMode` | **`WorkMode` `SetWorkTime`** | WorkMode必传；部分模式SetWorkTime可不传 |
| 3 | 控制程序 | `OperateWork` | `OperateWork` | 工作中可以取消、暂停、继续 |
| 4 | 开关-排水 | `SetAutoDrain` | **`AutoDrain`** | 设备开机不可用，开机会导致排水取消 |
| 5 | 设置长效保洁 | `SetBubble` | **`AddBubble`** | - |

## 控制示例

> data 参数来源物模型可写字段，凡列出的字段都要传，未用的填默认值。

### 开关机

固定 sid=`PowerSwitch`

```json
{"sid":"PowerSwitch","data":{"PowerSwitch":1}}
```

### 开启净化模式

sid=`StartWorkMode`，data 键是 `WorkMode` 与 `SetWorkTime`

```json
{"sid":"StartWorkMode","data":{"WorkMode":1,"SetWorkTime":0}}
```

### 暂停 / 继续 / 取消

固定 sid=`OperateWork`

```json
{"sid":"OperateWork","data":{"OperateWork":3}}
```

### 排水

sid=`SetAutoDrain`，**data 键是 `AutoDrain`**

```json
{"sid":"SetAutoDrain","data":{"AutoDrain":1}}
```

### 气泡设置

sid=`SetBubble`，**data 键是 `AddBubble`**

```json
{"sid":"SetBubble","data":{"AddBubble":1}}
```

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 远程授权见 [`remote-auth.md`](remote-auth.md)
- 智慧水槽（如 S1/S1L）走同一套物模型，控制方式一致
