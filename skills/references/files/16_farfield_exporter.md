# farfield_exporter.py Reference
Source: `src/ansys/aedt/core/visualization/post/farfield_exporter.py`

## 关键类/函数
- `FfdSolutionDataExporter(...)`: far-field 导出器。
- `export_farfield()`: 导出 `.ffd` + 元数据。
- `farfield_data`: 返回 `FfdSolutionData` 结构。
- `metadata_file`: 导出的 metadata 路径。

## 参数说明
- 初始化关键参数：`app`, `sphere_name`, `setup_name`, `frequencies`, `variations`, `overwrite`。
- 频点参数可为单频或频点列表。

## 常见调用模式
```python
exp = app.get_antenna_data(setup="Setup1", sphere="Infinite Sphere1")
exp.export_farfield()
print(exp.metadata_file)
```

## 注意事项
- 远场导出依赖已存在的 far-field setup 和求解结果。
- 频点不在已求解 sweep 内会导致导出缺失。

## 失败时怎么修
- 导出失败：确认 `sphere_name`、`setup_name` 拼写和存在性。
- 文件不完整：检查输出目录写权限与磁盘空间。
