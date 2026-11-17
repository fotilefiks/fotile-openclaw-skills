# 蒸烤微 (Steam Oven Microwave) 物模型参考

> ⚠️ **含微波与高温加热**：启动前确认腔内无金属器皿（微波会打火）。
>
> ⚠️ **无人看管的加热程序需用户明确确认**：`StartWorkMode` 一下发就升温，先核对模式/温度/时长。

## 允许 / 不允许的操作

✅ **查询**：读「主要物模型字段」里的可读项（`R` / `RW`）。不同型号可能有裁剪，以设备实际上报的 `services` 为准。

✅ **控制**：开关机、灯光、启动模式、设置时间/温度/湿度、快速预热、增压排气、清新换气、暂停/继续/取消。

❌ **不支持**：微波功率单独设定（物模型未定义，微波档位由模式决定）。

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
| `FreshExhaust` | 清新换气 | 1/0 | RW |
| `LeftStoveState` | 左灶状态 | 1/0 | R |
| `RightStoveState` | 右灶状态 | 1/0 | R |
| `WaterShortage` | 缺水提示 | 0-不缺水 1-缺水 | R |
| `DoorSwitch` | 门控状态 | 0-门关 1-门开 | R |
| `TankPlace` | 水箱位置 | 0-水箱已推到位 1-水箱未推到位 | R |
| `OperateWork` | 程序控制 | 1-取消工作 2-继续/立刻开始 3-暂停 4- 取消预约 | W |
| `ErrorNum` | 故障码 | 0-无异常、1-蒸汽发器NTC短路_断路、2-控制板与显示板通讯异常、3-水泵短路_断路、4-辅助蒸汽发生器NTC短路_断路、5-腔体探头PT1000或NTC断路、6-腔体探头PT1000或NTC短路 | R |
| `Heat` | 火力 | 1:低 2:中低 3:中 4:中高 5:高 | - |
| `KnockGears` | 敲击档位 | 1~8档 | RW |

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
| 8 | 清新换气 | `FreshExhaust` | `FreshExhaust` | - |
| 9 | 开启模式 | `StartWorkMode` | **`WorkMode`** | 必传，初始值为0. |
| 10 | 设置火力 | `SetHeat` | **`Heat`** | 微波模式下可用 |
| 11 | 控制操作 | `OperateWork` | `OperateWork` | 仅限在开启烹饪后有效 |
| 12 | 敲击档位 | `KnockGears` | `KnockGears` | - |

## 控制示例

> data 参数来源物模型可写字段，凡列出的字段都要传，未用的填默认值。

### 开/关机

固定 sid=`PowerSwitch`

```json
{"sid":"PowerSwitch","data":{"PowerSwitch":1}}
```

### 开关灯

固定 sid=`Light`

```json
{"sid":"Light","data":{"Light":1}}
```

### 开启烹饪模式

sid=`StartWorkMode`，`WorkMode` 与时间/温度等必传字段都要给

```json
{"sid":"StartWorkMode","data":{"WorkMode":1101,"SetWorkTime":20,"SetWorkTemperature":100,"SetAppointmentTime":0,"Humidity":0,"SetDownTemperature":0}}
```

### 暂停 / 继续 / 取消

固定 sid=`OperateWork`。1-取消工作、2-继续/立刻开始、3-暂停

```json
{"sid":"OperateWork","data":{"OperateWork":3}}
```

```json
{"sid":"OperateWork","data":{"OperateWork":2}}
```

```json
{"sid":"OperateWork","data":{"OperateWork":1}}
```

### 设置工作时间

固定 sid=`SetWorkTime`，单位分钟

```json
{"sid":"SetWorkTime","data":{"SetWorkTime":30}}
```

### 设置工作温度

sid=`SetWorkTemp`，**data 键是 `SetWorkTemperature`**

```json
{"sid":"SetWorkTemp","data":{"SetWorkTemperature":180}}
```

### 设置湿度

sid=`SetHumidity`，**data 键是 `Humidity`**

```json
{"sid":"SetHumidity","data":{"Humidity":1}}
```

### 快速预热

固定 sid=`QuickHeat`

```json
{"sid":"QuickHeat","data":{"QuickHeat":1}}
```

## 模式附录（WorkMode 取值）

| 类别 | 模式名 | 属性值(WorkMode) |
|---|---|---|
| 蒸模式 | 普通蒸/健康蒸 | 1101 |
| 蒸模式 | 低温蒸 | 1102 |
| 蒸模式 | 高温蒸 | 1103 |
| 蒸模式 | 早餐速蒸 | 1104 |
| 蒸模式 | 维鲜蒸 | 1105 |
| 蒸模式 | 脱盐蒸 | 1106 |
| 蒸模式 | 低糖蒸 | 1107 |
| 蒸模式 | ω-3凝鲜蒸 | 1108 |
| 蒸模式 | 鲜嫩蒸 | 1109 |
| 蒸模式 | 蒸炖/甜品炖/营养煲汤/健康煲汤 | 1110 |
| 蒸模式 | 旺火蒸 | 1111 |
| 蒸模式 | 多层蒸 | 1112 |
| 蒸模式 | 脱脂蒸 | 1113 |
| 蒸模式 | 五谷杂粮 | 1114 |
| 蒸模式 | 河海鲜类 | 1115 |
| 蒸模式 | 肉类 | 1116 |
| 蒸模式 | 蔬菜类 | 1117 |
| 蒸模式 | 蛋类 | 1118 |
| 蒸模式 | 饭菜复热 | 1119 |
| 烤模式 | 上下火 | 2101 |
| 烤模式 | 全开烤 | 2102 |
| 烤模式 | 环风烤 | 2103 |
| 烤模式 | 双温同烤 | 2104 |
| 烤模式 | 加湿烤 | 2105 |
| 烤模式 | 脱脂烤 | 2106 |
| 烤模式 | 烧烤 | 2107 |
| 烤模式 | 脆脆烤/蒸汽脆烤 | 2108 |
| 烤模式 | 轻食酷烤 | 2109 |
| 烤模式 | 多汁嫩烤 | 2110 |
| 烤模式 | 空气炸 | 2111 |
| 烤模式 | 蔬果干 | 2112 |
| 烤模式 | 顶部加热 | 2113 |
| 烤模式 | 多层烤 | 2114 |
| 烤模式 | 鼓风烤 | 2115 |
| 烤模式 | 密集烤 | 2116 |
| 烤模式 | 节能烤 | 2117 |
| 烤模式 | 健康煲汤/营养煲汤 | 2118 |
| 烤模式 | 面包复烤 | 2119 |
| 烤模式 | 饼干复脆 | 2120 |
| 烤模式 | 无水焖 | 2121 |
| 烤模式 | 分控烤 | 2122 |
| 烤模式 | 底部烤 | 2123 |
| 烤模式 | 焖烤/焖炖 | 2124 |
| 烤模式 | 冻品烤 | 2125 |
| 烤模式 | 酥烤馅饼 | 2126 |
| 烤模式 | 香炸鸡块 | 2127 |
| 烤模式 | 脆烤薯条 | 2128 |
| 烤模式 | 焗烤 | 2129 |
| 烤模式 | 顶部烤 | 2130 |
| 辅助功能 | 发酵 | 3101 |
| 辅助功能 | 保温 | 3102 |
| 辅助功能 | 解冻 | 3103 |
| 辅助功能 | 烘干 | 3104 |
| 辅助功能 | 蒸汽清洁 | 3105 |
| 辅助功能 | 除垢 | 3106 |
| 辅助功能 | 催化自清洁 | 3107 |
| 辅助功能 | 除味 | 3108 |
| 辅助功能 | 加热速冻制品 | 3109 |
| 微功能 | 微波 | 4101 |
| 微功能 | 微蒸 | 4102 |
| 微功能 | 微炖 | 4103 |
| 微功能 | 微烤 | 4104 |
| 灵犀智烤 | 烤红薯 | 5101 |
| 灵犀智烤 | 烤肉串 | 5102 |
| 灵犀智烤 | 蛋挞 | 5103 |
| 灵犀智烤 | 曲奇饼干 | 5104 |
| 灵犀智烤 | 烤翅 | 5105 |
| 灵犀智烤 | 蔬果干 | 5106 |
| 灵犀智烤 | 戚风蛋糕 | 5107 |
| 灵犀智烤 | 广式月饼 | 5108 |
| 灵犀智烤 | 蛋黄酥 | 5109 |
| 灵犀智烤 | 小餐包 | 5110 |
| 灵犀智烤 | 吐司 | 5111 |
| 灵犀智烤 | 桃酥 | 5112 |
| 灵犀智烤 | 鱼干 | 5113 |
| 灵犀智烤 | 虾干 | 5114 |
| 灵犀智烤 | 烤肠 | 5115 |

## 相关

- 通用控制流程见 [`SKILL.md`](../SKILL.md) 的 Workflow 一节
- 远程授权见 [`remote-auth.md`](remote-auth.md)
