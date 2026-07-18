# solve_sweeps.py Reference
Source: `src/ansys/aedt/core/modules/solve_sweeps.py`

## 关键类/函数
- `SweepHFSS`: HFSS 频扫对象。
- `add_subrange(...)`: 添加分段 sweep。
- `create()`, `update()`: 提交 sweep。
- `is_solved()`, `frequencies()`, `basis_frequencies()`。

## 参数说明
- `SweepHFSS(setup, name, sweep_type="Interpolating", props=None)`。
- `add_subrange` 关键参数：`range_type`, `start`, `end`, `step` 或 `count`。

## 常见调用模式
```python
sw = setup.add_sweep(name="Sweep1", sweep_type="Interpolating")
sw.add_subrange(range_type="LinearCount", start=8, end=12, count=201, unit="GHz")
sw.update()
```

## 注意事项
- 同 setup 下 sweep 名称不可重复。
- 多 subrange 时注意频段连续性，避免报告采样断裂。

## 失败时怎么修
- `update` 失败：检查 `props` 中范围字段是否冲突。
- `frequencies()` 为空：先确认 setup 已求解。
