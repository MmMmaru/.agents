# modeler_3d.py Reference
Source: `src/ansys/aedt/core/modeler/modeler_3d.py`

## 关键类/函数
- `Modeler3D`: 3D 建模高层 API。
- `create_waveguide(...)`, `create_coaxial(...)`: 高频结构快捷建模。
- `create_3dcomponent(...)`, `replace_3dcomponent(...)`: 组件复用。
- `objects_in_bounding_box(...)`: 几何检索。
- `change_region_padding(...)`: 区域边界扩展。

## 参数说明
- 同轴/波导接口常用参数：中心线、半径或截面、长度、方向。
- `objects_in_bounding_box` 依赖 `[xmin, ymin, zmin, xmax, ymax, zmax]`。
- region padding 建议使用带单位字符串。

## 常见调用模式
```python
m = app.modeler
m.create_coaxial([0,0,0], axis=2, innerradius=0.5, outerradius=1.8, dielradius=1.5, length=20)
m.change_region_padding(["20mm"]*6)
```

## 注意事项
- 方向轴与单位统一错误会导致端口位置偏移。
- 组件替换会改变对象 ID，不要缓存旧 ID。

## 失败时怎么修
- 几何创建报错：检查参数数量和单位。
- 区域修改失败：确认存在 `Region` 对象或显式指定名称。
