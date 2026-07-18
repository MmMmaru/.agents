# analysis_3d.py Reference
Source: `src/ansys/aedt/core/application/analysis_3d.py`

## 关键类/函数
- `FieldAnalysis3D(...)`: 3D 设计求解入口。
- `modeler`, `mesh`, `post`: 三大高频子系统访问器。
- `assign_material(assignment, material)`: 批量赋材。
- `import_3d_cad(...)`, `export_3d_model(...)`: CAD 导入导出。
- `get_all_sources()`, `get_all_source_modes()`: 激励源查询。

## 参数说明
- `assign_material` 的 `assignment` 可为对象名列表。
- `import_3d_cad` 重点参数：输入路径、单位、是否 heal/simplify。
- `cleanup_solution(...)` 可按 setup/sweep 清理旧结果。

## 常见调用模式
```python
m = app.modeler
box = m.create_box([0,0,0], [10,10,1], name="Patch")
app.assign_material([box.name], "copper")
app.mesh.assign_initial_mesh_from_slider(4)
```

## 注意事项
- 材料名称需存在于当前材料库。
- 导入 CAD 后对象命名可能变化，后续脚本需重新查询对象名。

## 失败时怎么修
- 赋材失败：先用 `app.materials` 检查材料是否存在。
- 导入失败：确认 CAD 路径、格式和单位映射。
- mesh 调用失败：确认当前设计确实是 3D 求解器。
