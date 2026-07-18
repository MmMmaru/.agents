# analysis.py Reference
Source: `src/ansys/aedt/core/application/analysis.py`

## 关键类/函数
- `Analysis(...)`: 求解能力基类。
- `analyze(...)` / `analyze_setup(name)`: 启动求解。
- `get_setup(name)` / `setups`: setup 访问入口。
- `setup_sweeps_names`, `existing_analysis_sweeps`: sweep 查询。
- `create_output_variable(...)` / `get_output_variable(...)`: 输出变量。
- `export_results(...)`, `export_convergence(...)`: 结果导出。

## 参数说明
- `analyze_setup(name)` 的 `name` 必须是已存在 setup。
- `create_output_variable` 关键参数：表达式、解算上下文、单位。
- `export_results` 常用参数：输出目录、报告格式。

## 常见调用模式
```python
setup = app.get_setup("Setup1")
app.analyze_setup("Setup1")
print(app.existing_analysis_sweeps)
app.create_output_variable("bw", "max(freq)-min(freq)")
```

## 注意事项
- 输出变量依赖可解析的表达式与上下文 sweep。
- setup 名称与 sweep 名称拼写错误最常见。

## 失败时怎么修
- 报 `setup not found`：先打印 `app.setup_names`。
- 报表达式无效：先在 AEDT report 中验证表达式可计算。
- 导出空文件：确认求解结束且对应结果存在。
