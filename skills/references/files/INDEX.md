# PyAEDT API References Index

## 说明
- 目标：覆盖 `Readme.md` 的 7 步 HFSS 流程最小集。
- 规则：每份文档只保留 agent 高频需要的 API 信息。
- 固定结构：`关键类/函数`、`参数说明`、`常见调用模式`、`注意事项`、`失败时怎么修`。

## 文件清单
1. `01_hfss.md` - HFSS 主入口（设计、边界、激励、setup、远场）
2. `02_desktop.md` - AEDT 会话管理
3. `03_design.md` - 设计/项目与变量入口
4. `04_analysis.md` - 求解控制与导出
5. `05_analysis_3d.md` - 3D 子系统桥接（modeler/mesh/post）
6. `06_modeler_3d.md` - 3D 建模高层接口
7. `07_modeler_2d.md` - 2D 建模接口
8. `08_primitives_3d.md` - 3D 基元创建
9. `09_primitives_2d.md` - 2D 基元创建
10. `10_object_3d.md` - 单对象几何操作
11. `11_hfss_boundary.md` - 远近场 setup 对象
12. `12_boundary_common.md` - 通用边界对象
13. `13_solve_setup.md` - Setup 生命周期与 sweep 创建
14. `14_solve_sweeps.md` - Sweep 对象与分段扫频
15. `15_mesh.md` - 网格控制
16. `16_farfield_exporter.md` - 远场导出器
17. `17_farfield_visualization.md` - 远场数据分析与绘图
18. `18_post_hfss.md` - HFSS 后处理入口
19. `19_solution_data.md` - 报告数据容器
20. `20_report_standard.md` - 标准/频谱报告对象
21. `21_variables.md` - 变量系统
22. `22_design_xploration.md` - 参数扫描与优化

## 示例脚本
- `../scripts/cp_single_layer_patch_optimize.py` - 有界参数优化与候选选择示例
- `../scripts/patch20g_param_study.py` - 单参数扫频、逐 case 落盘与阻抗/S 参数提取示例
- `../scripts/patch20g_visual_qa.py` - 远端 HFSS 几何可视化 QA 示例
- `../scripts/patch20g_export_dataset.py` - 远端 HFSS 求解后 S 参数和远场数据导出示例

## 按流程映射
- 打开 design: `01, 02, 03, 04, 05`
- 创建 3D/2D 模型: `06, 07, 08, 09, 10`
- 设置边界、激励: `01, 11, 12`
- 设置仿真: `13, 14, 15`
- 设置远场: `01, 16, 17`
- 获取结果、图像: `18, 19, 20`
- 参数创建、调整: `21, 22`
