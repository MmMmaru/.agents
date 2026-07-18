# hfss_boundary.py Reference
Source: `src/ansys/aedt/core/modules/boundary/hfss_boundary.py`

## 关键类/函数
- `FieldSetup`: 场采样设置基类。
- `FarFieldSetup`: 无限远场设置对象。
- `NearFieldSetup`: 近场设置对象。
- `create()`, `update()`, `delete()`: 生命周期接口。

## 参数说明
- `FarFieldSetup` 关键参数：`definition`, `theta_start/stop/step`, `phi_start/stop/step`。
- 坐标/极化参数：`use_local_coordinate_system`, `local_coordinate_system`, `polarization`, `slant_angle`。
- 自定义辐射面：`use_custom_radiation_surface`, `custom_radiation_surface`。

## 常见调用模式
```python
ff = app.insert_infinite_sphere(name="FF1")
ff.theta_start = -90
ff.theta_stop = 90
ff.phi_step = 2
ff.update()
```

## 注意事项
- 角度单位默认 `deg`，脚本里应统一。
- 定义方式（Theta/Phi vs Az/El）要和后处理表达式一致。

## 失败时怎么修
- 更新失败：检查字段名是否属于当前 `definition`。
- 远场为空：确认存在辐射边界且 setup 已求解。
- 自定义辐射面无效：确认目标 surface 名称存在且可用于辐射。
