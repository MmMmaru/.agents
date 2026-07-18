# variables.py Reference
Source: `src/ansys/aedt/core/application/variables.py`

## 关键类/函数
- `VariableManager`: 变量管理入口。
- `set_variable(...)`, `delete_variable(name)`, `delete_unused_variables()`。
- `__getitem__/__setitem__`: 读写变量快捷入口。
- `design_variables`, `project_variables`, `independent_variables`。
- `Variable`: 单变量对象（`expression`, `evaluated_value`, `units`, `si_value`）。

## 参数说明
- `set_variable` 关键参数：`name`, `expression/value`, `read_only`, `hidden`, `sweep`。
- 项目变量名通常以 `$` 开头。
- 表达式可引用已有变量（如 `"w/2"`）。

## 常见调用模式
```python
vm = app.variable_manager
vm.set_variable("w", "12mm")
vm.set_variable("f0", "10GHz")
vm.set_variable("lambda0", "c0/f0")
print(vm["lambda0"].evaluated_value)
```

## 注意事项
- 变量单位不一致会引发表达式隐式转换问题。
- 删除变量前要确认未被 setup/边界/后处理引用。

## 失败时怎么修
- 变量创建失败：检查变量名是否合法、表达式是否可解析。
- 求解报变量错误：用 `is_used` 和表达式回溯定位依赖链。
