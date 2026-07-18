# design.py Reference
Source: `src/ansys/aedt/core/application/design.py`

## 关键类/函数
- `Design(...)`: 项目与设计抽象基类。
- `insert_design(name=None, solution_type=None)`: 新建设计。
- `create_new_project(name)`, `close_project(...)`: 工程管理。
- `__getitem__/__setitem__`: 变量读写快捷入口。
- `boundaries`, `boundaries_by_type`, `ports`: 拿边界与端口信息。
- `variable_manager`: 获取 `VariableManager`。

## 参数说明
- 初始化关键参数：`project`, `design`, `solution_type`, `version`。
- 变量写入值支持字符串单位表达式（如 `"10mm"`, `"f0*0.5"`）。
- `insert_design` 的 `solution_type` 必须匹配产品类型。

## 常见调用模式
```python
app = Hfss(project="demo.aedt", design="HFSSDesign1")
app["w"] = "12mm"
app["f0"] = "10GHz"
print(app.boundaries_by_type)
```

## 注意事项
- 变量名区分项目变量(`$var`)与设计变量(`var`)。
- 设计名重名时，插入与切换行为不同。

## 失败时怎么修
- 变量写入失败：检查表达式语法与单位。
- 设计切换异常：先检查 `design_list` 是否包含目标设计。
- 边界列表为空：确认设计类型正确且边界已创建。
