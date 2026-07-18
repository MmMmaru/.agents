# primitives_2d.py Reference
Source: `src/ansys/aedt/core/modeler/cad/primitives_2d.py`

## 关键类/函数
- `Primitives2D`: 2D 基元建模类。
- `create_circle`, `create_ellipse`, `create_rectangle`, `create_regular_polygon`。
- `create_region(...)`: 2D 求解区域创建。
- `plane2d`: 当前 2D 工作平面。

## 参数说明
- 通用参数：`origin`, `radius`/`sizes`, `name`, `material`。
- `create_region` 关键参数：padding、正负方向扩展、是否覆盖已有区域。

## 常见调用模式
```python
m = app.modeler
m.create_rectangle(origin=[0,0,0], sizes=[20,10], name="Profile")
m.create_circle(origin=[5,5,0], radius=1, name="FeedHole")
```

## 注意事项
- 2D 对象通常为 sheet；与 3D 实体的边界/网格接口不同。
- 工作平面错误会让几何落在非预期位置。

## 失败时怎么修
- 几何不显示：检查 `plane2d` 与坐标值。
- `create_region` 失败：删除旧 Region 或更换 region 名称再试。
