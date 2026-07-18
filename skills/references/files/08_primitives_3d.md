# primitives_3d.py Reference
Source: `src/ansys/aedt/core/modeler/cad/primitives_3d.py`

## 关键类/函数
- `Primitives3D`: 3D 基元建模核心。
- `create_box`, `create_cylinder`, `create_sphere`, `create_cone`。
- `create_rectangle`, `create_circle`, `create_ellipse`（在工作平面创建 sheet）。
- `create_equationbased_curve/surface`, `create_helix`（参数化几何）。
- `insert_3d_component(...)`: 插入现成 3D 组件。

## 参数说明
- 基元通用参数：`origin`, `sizes`/`radius`/`height`, `name`, `material`。
- 曲线/曲面常用参数：参数方程、变量范围、单位。
- 组件插入参数：组件路径、目标坐标系、缩放/旋转信息。

## 常见调用模式
```python
m = app.modeler
sub = m.create_box([0,0,0], [60,60,1.6], name="Sub", material="FR4_epoxy")
patch = m.create_rectangle(orientation=2, origin=[10,10,1.6], sizes=[20,12], name="Patch")
```

## 注意事项
- `material` 不存在时可能回退默认材料，需显式核对。
- 2D sheet 与 3D solid 的后续边界分配方式不同。

## 失败时怎么修
- 创建返回 `False/None`：检查参数单位与方向枚举。
- 插件组件失败：确认组件文件路径、版本兼容性与权限。
