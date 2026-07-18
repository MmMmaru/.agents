# post_hfss.py Reference
Source: `src/ansys/aedt/core/visualization/post/post_hfss.py`

## 关键类/函数
- `PostProcessorHFSS`: HFSS 后处理入口。
- `get_far_field_data(...)`: 获取远场数据对象。
- `create_fieldplot_layers(...)`, `create_fieldplot_layers_nets(...)`: 分层场图。
- `set_tuning_offset(setup, offsets)`: 调整求解偏移。
- SBR 可视化：`create_sbr_*_ray_tracing(...)`。

## 参数说明
- `get_far_field_data` 关键参数：`setup_sweep_name`, `sphere_name`, `variations`, `expression`。
- 场图接口常用参数：层/网络过滤、标量量名、单位、plot name。

## 常见调用模式
```python
ff = app.post.get_far_field_data(setup_sweep_name="Setup1 : Sweep1", sphere_name="Infinite Sphere1")
sol = app.post.get_solution_data(expressions="dB(S(1,1))", setup_sweep_name="Setup1 : Sweep1")
```

## 注意事项
- `setup_sweep_name` 格式通常是 `"Setup : Sweep"`。
- 表达式必须属于对应求解器上下文。

## 失败时怎么修
- 返回空数据：确认该 setup/sweep 已求解。
- 报表达式错误：先在 AEDT 报告窗口验证表达式名称。
