# design_xploration.py Reference
Source: `src/ansys/aedt/core/modules/design_xploration.py`

## 关键类/函数
- `ParametricSetups`: 参数扫描集合管理。
- `OptimizationSetups`: 优化集合管理。
- `SetupParam`: 单个参数扫描 setup。
- `SetupOpti`: 单个优化 setup。
- `add_variation(...)`, `add_goal(...)`, `analyze(...)`, `export_to_csv(...)`。

## 参数说明
- `ParametricSetups.add(...)` 关键参数：`variable`, `start`, `stop`, `step`/`count`。
- `SetupOpti.add_goal` 关键参数：目标表达式、优化目标（min/max/value）、上下文 setup。
- `sync_variables(variables, sync_n)` 可同步多变量步进。

## 常见调用模式
```python
p = app.parametrics.add(variable="w", start_point=10, end_point=20, step=1, variation_type="LinearStep")
p.add_variation("l", 8, 14, 1, "LinearStep")
p.analyze()
```

## 注意事项
- 扫描变量必须是可调设计变量。
- 大范围多变量扫描会指数级增加求解量。

## 失败时怎么修
- 添加扫描失败：确认变量存在且不是只读/后处理变量。
- analyze 无任务：检查 setup 绑定和 variation 定义是否完整。
- 导出 CSV 为空：确认 parametric run 实际完成。
