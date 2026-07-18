# farfield_visualization.py Reference
Source: `src/ansys/aedt/core/visualization/advanced/farfield_visualization.py`

## 关键类/函数
- `FfdSolutionData(...)`: far-field 数据分析对象。
- `combine_farfield(phi_scan=0.0, theta_scan=0.0)`: 波束合成。
- `get_accepted_power()`, `radiated_power`, `s_parameters`。
- `plot_contour(...)`, `plot_cut(...)`, `plot_3d(...)`: 可视化。
- `get_far_field_mesh(...)`: 获取网格化辐射数据。

## 参数说明
- 扫描参数：`phi_scan`, `theta_scan`。
- 绘图参数：`quantity`（如 `RealizedGain`）、`quantity_format`（`dB10`/`abs`）。
- 阵列权重参数：`phase`, `magnitude`, `taper`。

## 常见调用模式
```python
ffd = exp.farfield_data
ffd.frequency = 10e9
ffd.phase = [0] * len(ffd.all_element_names)
ffd.plot_cut(quantity="RealizedGain", primary_sweep="Theta")
```

## 注意事项
- 频率必须在可用 `frequencies` 中。
- 阵列元素权重长度需与端口/单元数量一致。

## 失败时怎么修
- 绘图失败：先检查 `ffd.farfield_data` 是否为空。
- 功率结果异常：检查端口归一化和激励相位。
