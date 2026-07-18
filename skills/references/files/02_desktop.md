# desktop.py Reference
Source: `src/ansys/aedt/core/desktop.py`

## 关键类/函数
- `Desktop(...)`: AEDT 进程/会话入口。
- `load_project(project_file, design_name=None)`: 打开工程。
- `active_project(...)` / `active_design(...)`: 获取或切换活动对象。
- `save_project(...)`: 保存工程。
- `analyze_all(project=None, design=None)`: 整体求解。
- `release_desktop(close_projects=True, close_on_exit=True)`: 释放会话。

## 参数说明
- `version`: 例如 `"2026.1"` / `261`。
- `non_graphical`: 批处理建议 `True`。
- `new_desktop`: 是否新起一个 AEDT 线程。
- `aedt_process_id`: 复用已有进程时使用。
- `machine`, `port`: gRPC 远程连接参数。

## 常见调用模式
```python
from ansys.aedt.core import Desktop
with Desktop(version="2026.1", non_graphical=True, new_desktop=True) as d:
    d.load_project(r"E:/work/demo.aedt")
    d.save_project()
```

## 注意事项
- `new_desktop=False` 时可能附着到已有进程，状态不可控。
- 远程模式要求目标端先启动 gRPC 服务。
- 不正确释放 Desktop 会留下锁文件/僵尸进程。

## 失败时怎么修
- 启动失败：确认 AEDT 版本已安装且 `version` 可解析。
- 连接失败：检查 `machine/port` 与防火墙。
- 项目锁定：关闭占用进程或使用上层 `remove_lock` 机制重试。
