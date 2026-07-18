# boundary common.py Reference
Source: `src/ansys/aedt/core/modules/boundary/common.py`

## 关键类/函数
- `BoundaryObject`: 通用边界对象。
- `BoundaryProps`: 边界属性字典封装。
- `create()`, `update()`, `update_assignment()`, `delete()`。

## 参数说明
- `BoundaryObject(app, name, props, boundarytype, auto_update=True)`。
- `props` 为边界参数字典；`auto_update` 控制属性改动是否即时提交。

## 常见调用模式
```python
b = app.assign_perfect_e(["sheet1"], name="PE1")
b.props["InfGroundPlane"] = False
b.update()
```

## 注意事项
- 直接改 `props` 后通常需要 `update()`。
- 边界类型和目标几何类型必须匹配（sheet/face/object）。

## 失败时怎么修
- `create/update` 返回失败：打印 `b.props` 检查字段拼写。
- `update_assignment` 失败：确认 assignment 仍存在。
