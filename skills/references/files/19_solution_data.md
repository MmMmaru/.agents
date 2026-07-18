# solution_data.py Reference
Source: `src/ansys/aedt/core/visualization/post/solution_data.py`

## 关键类/函数
- `SolutionData`: 报告数据容器。
- `expressions`, `primary_sweep_values`, `variation_values(...)`。
- `data_real(...)`, `get_expression_data(...)`: 数据读取。
- `plot(...)`, `plot_3d(...)`: 快速可视化。
- `export_data_to_csv(output, delimiter=";")`。

## 参数说明
- `active_variation`: 当前变量组合。
- `primary_sweep`: 主扫描轴（如 `Freq`）。
- `convert_to_SI`: 是否转换到 SI 单位。

## 常见调用模式
```python
sd = app.post.get_solution_data(expressions="dB(S(1,1))", setup_sweep_name="Setup1 : Sweep1")
freq = sd.primary_sweep_values
s11 = sd.data_real()
sd.export_data_to_csv(r"E:/tmp/s11.csv")
```

## 注意事项
- 多表达式/多变量时先设置 `active_variation`。
- `data_real()` 对复数表达式只返回实部。

## 失败时怎么修
- 数组长度不一致：检查 `primary_sweep` 与 expression 是否匹配。
- CSV 空数据：确认 `sd.expressions` 非空且结果已求解。
