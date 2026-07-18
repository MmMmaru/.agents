# mesh.py Reference
Source: `src/ansys/aedt/core/modules/mesh.py`

## 关键类/函数
- `Mesh`: 网格设置入口。
- `assign_initial_mesh_from_slider(level)`。
- `assign_length_mesh(...)`, `assign_skin_depth(...)`, `assign_surface_mesh(...)`。
- `generate_mesh(name)`: 生成指定 setup 的网格。
- `meshoperations`, `meshoperation_names`: 查询已配置网格操作。

## 参数说明
- `assignment`: 对象/面列表。
- `level`: 全局网格粗细级别（数值越大通常越细）。
- skin depth 关键参数：导体、频率、层厚。

## 常见调用模式
```python
mesh = app.mesh
mesh.assign_initial_mesh_from_slider(4)
mesh.assign_length_mesh(["Patch"], maxlength="1mm", maxel=None)
mesh.generate_mesh("Setup1")
```

## 注意事项
- 过细网格会显著增加内存和求解时间。
- 局部网格优先于全局网格，顺序配置要清楚。

## 失败时怎么修
- 网格操作失败：检查 `assignment` 是否存在且类型匹配。
- 求解前网格报错：先删除冲突 mesh operation 再重建。
