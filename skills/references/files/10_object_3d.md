# object_3d.py Reference
Source: `src/ansys/aedt/core/modeler/cad/object_3d.py`

## 关键类/函数
- `Object3d`: 单个几何对象操作入口。
- 属性访问：`faces`, `edges`, `vertices`, `bounding_box`, `volume`, `material_name`。
- 几何编辑：`move`, `rotate`, `mirror`, `unite`, `subtract`, `intersect`, `split`。
- 选择辅助：`top_face_z`, `largest_face`, `longest_edge`。

## 参数说明
- 变换接口常用参数：`axis`, `angle`, `vector`。
- 布尔运算参数：`assignment`（对象名或对象列表）。
- `subtract(..., keep_originals)` 控制是否保留被减对象。

## 常见调用模式
```python
patch = app.modeler["Patch"]
gnd = app.modeler["GND"]
patch.move([0, 0, 1.6])
gnd.unite([patch])
```

## 注意事项
- 布尔运算后对象名称和拓扑会变化。
- 不要长期缓存 face/edge id，建模变更后可能失效。

## 失败时怎么修
- `assignment` 无效：改为使用对象名字符串列表。
- 运算后对象丢失：检查 `keep_originals` 或先 `clone()` 备份。
- 属性读取异常：确认对象仍为 model object（未删除/未 suppress）。
