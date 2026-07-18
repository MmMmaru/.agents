# modeler_2d.py Reference
Source: `src/ansys/aedt/core/modeler/modeler_2d.py`

## 关键类/函数
- `Modeler2D`: 2D 设计建模入口。
- `calculate_radius_2D(assignment, inner=False)`: 计算截面半径。
- `radial_split_2D(radius, name)`: 按半径切分。
- `objects_in_bounding_box(...)`: 2D 对象过滤。

## 参数说明
- `assignment`: 对象名。
- `inner`: 选内半径或外半径。
- `bounding_box`: 仍使用 3D 形式边界数组，但按 2D 平面解释。

## 常见调用模式
```python
m2d = app.modeler
r = m2d.calculate_radius_2D("Stator", inner=True)
m2d.radial_split_2D(radius=r, name="Stator")
```

## 注意事项
- 仅适用于 2D/RMxprt 类场景，HFSS 3D 下不建议混用。

## 失败时怎么修
- 报对象不存在：检查当前设计是否正确且对象名大小写一致。
- 切分失败：确认对象几何确实可按径向拆分。
