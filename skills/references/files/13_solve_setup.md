# solve_setup.py Reference
Source: `src/ansys/aedt/core/modules/solve_setup.py`

## 关键类/函数
- `SetupHFSS`: HFSS setup 主类。
- `create()`, `update()`, `analyze()`, `delete()`。
- `create_frequency_sweep(...)`, `create_linear_step_sweep(...)`, `create_single_point_sweep(...)`。
- `get_sweep(name)`, `get_sweep_names()`, `delete_sweep(name)`。
- 自适应接口：`enable_adaptive_setup_single/broadband/multifrequency(...)`。

## 参数说明
- Setup 常用参数：`Frequency`, `MaximumPasses`, `MaxDeltaS`, `BasisOrder`。
- Sweep 常用参数：`unit`, `start_frequency`, `stop_frequency`, `step_size`/`num_of_freq_points`, `sweep_type`。
- 多频自适应参数：`frequencies`, `max_delta_s`。

## 常见调用模式
```python
setup = app.create_setup(name="Setup1", setup_type="HFSSDriven", Frequency="10GHz")
setup.enable_adaptive_setup_single(freq="10GHz", max_passes=12)
setup.create_frequency_sweep(unit="GHz", start_frequency=8, stop_frequency=12, num_of_freq_points=201)
```

## 注意事项
- 先 `setup.create()`/`update()`，再增删 sweep 更稳妥。
- `sweep_type` 与求解时间、精度直接相关（Interpolating 更快，Discrete 更稳）。

## 失败时怎么修
- sweep 创建失败：检查 setup 是否为 HFSS setup。
- analyze 失败：检查 license/HPC 配置和模型闭合性。
- 结果不收敛：提高 `MaximumPasses`、降低 `MaxDeltaS`。
