# hfss.py Reference
Source: `src/ansys/aedt/core/hfss.py`

## 关键类/函数
- `Hfss(...)`: HFSS 主入口，负责会话、项目、设计绑定。
- `create_setup(name, setup_type, **kwargs)`: 创建求解设置。
- `create_linear_count_sweep(...)` / `create_linear_step_sweep(...)` / `create_single_point_sweep(...)`: 频扫配置。
- `wave_port(...)` / `lumped_port(...)` / `circuit_port(...)`: 端口激励。
- `assign_radiation_boundary_to_objects(...)` / `assign_radiation_boundary_to_faces(...)`: 开域边界。
- `assign_perfect_e(...)` / `assign_perfect_h(...)`: 理想导体边界。
- `create_open_region(...)`: 自动开区域。
- `insert_infinite_sphere(...)` / `insert_near_field_*`: 远场/近场设置。
- `create_scattering(...)` / `create_qfactor_report(...)`: 常见报告入口。
- `validate_full_design(...)`: 设计检查。

## 参数说明
- 会话参数：`version`, `non_graphical`, `new_desktop`, `student_version`, `machine`, `port`。
- 设计参数：`project`, `design`, `solution_type`, `setup`。
- Setup 关键参数：`setup_type`, `Frequency`, `MaximumPasses`, `MaxDeltaS`。
- Sweep 关键参数：`unit`, `start_frequency`, `stop_frequency`, `num_of_freq_points` 或 `step_size`, `sweep_type`, `save_fields`。
- 端口/边界参数：`assignment`, `reference`, `integration_line`, `name`。
- 远场参数：`definition`, `theta/phi` 范围与步进，自定义辐射面与坐标系。

## 常见调用模式
```python
from ansys.aedt.core import Hfss
hfss = Hfss(project="demo.aedt", design="Antenna", solution_type="Modal", non_graphical=True)

setup = hfss.create_setup(name="Setup1", setup_type="HFSSDriven", Frequency="10GHz")
hfss.create_linear_count_sweep(setup="Setup1", unit="GHz", start_frequency=8, stop_frequency=12, num_of_freq_points=201)

hfss.assign_radiation_boundary_to_objects("Region")
hfss.wave_port(assignment="port_sheet", reference="gnd_sheet")
hfss.analyze_setup("Setup1")
```

## 注意事项
- `solution_type` 会影响端口与边界可用方法（Terminal/Modal 规则不同）。
- Sweep 名称在同一个 setup 下必须唯一。
- 端口积分线方向错误会导致 S 参数异常。
- 远场球通常要求模型存在有效辐射边界与已求解结果。

## 失败时怎么修
- 报 `active design/project` 为空：先显式传入 `project` 与 `design`，或先 `Desktop().load_project(...)`。
- 报边界创建失败：检查 `assignment` 对象是否存在、是否是正确几何类型（face/sheet/object）。
- 报 sweep/setup 不匹配：确认 `setup="Setup1"` 名称存在且已更新。
- 结果为空：先 `analyze_setup`，再创建报告或导出 far-field。
