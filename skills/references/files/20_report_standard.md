# report standard.py Reference
Source: `src/ansys/aedt/core/visualization/report/standard.py`

## 关键类/函数
- `Standard(...)`: 标准报告对象。
- `Spectral(...)`: 频谱报告对象。
- `create(name=None)`: 生成报告。
- 常用属性：`time_start`, `time_stop`, `thinning`, `max_frequency`, `window`。

## 参数说明
- `report_category`: 如 `Modal Solution Data`。
- `setup_name`: 如 `"Setup1 : Sweep1"`。
- `expressions`: 如 `"dB(S(1,1))"` 或列表。

## 常见调用模式
```python
rep = app.post.reports_by_category.standard(expressions=["dB(S(1,1))"], setup="Setup1 : Sweep1")
rep.create("S11_Report")
```

## 注意事项
- 报告类别要和求解器类型一致。
- 时域参数只在对应时域/瞬态场景生效。

## 失败时怎么修
- `create` 失败：检查 `setup_name` 与 category 是否匹配。
- 无曲线：确认 expressions 在该解下可计算。
