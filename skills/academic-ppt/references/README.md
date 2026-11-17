# 参考样例：APMC 2026 口头报告（20 页）

文件：`APMC2026_Oral_example.pptx`，取自 2026-11-09 的交付版本，原件在项目的 `docs/paper/PPT/APMC2026_Oral_Rongsheng_Xu_V2.pptx`。

**当前配色规范已更新**：此文件是历史样例，只参考内容组织、字号层级、分组和备注。新建及重设计采用 `SKILL.md` 中的纯黑白规范，所有编排文字（包括副标题、来源和页码）使用纯黑，不继承历史样例的蓝白配色、灰色小字或红绿强调。论文原图与实物照片默认保留原色。

- **页面与字号**：16:9（13⅓ × 7½ 英寸）。字号表：标题 Segoe UI Black 36 pt，副标题 26 pt，分栏标题 20 pt，正文 18 pt（Times New Roman），引用 14 pt 斜体。
- **制作方式**：路线 B（Edit Native round-trip）。从原版 PPT 导入，由生成脚本逐页改写，用户在 PowerPoint 里多轮手改，最后用 COM 只移植改动页。
- **讲稿**：每页的演讲者备注就是英文讲稿。中英对照讲稿在项目里另存为 `docs/paper/PPT/APMC2026_Oral_Rongsheng_Xu_V2_讲稿.md`。

## 逐页看点

| 页 | 标题 | 体现的规则 |
|---|---|---|
| 1、20 | 封面 / 致谢 | 保持原样：原 logo、原位置、原文字，不加动画 |
| 2、8、13、18 | Overview | 目录页复用同一版式，只改高亮项 |
| 3 | Aperiodic Array Applications | 三栏应用卡（实物照片 + ✓ 一行收益 + 引用），下方一栏“周期 vs 非周期”对比与结论卡；实物照片都来自开放许可来源，引用行写明照片来源 |
| 4 | Development of Aperiodic Arrays | 四栏发展脉络用箭头串联（箭头在所有面板之后绘制），每栏写做法 / ✓ / ✗ 三行，年份只出现在引用里；页底一条趋势横幅 |
| 5 | Mutual Coupling Challenge | 左右对比：周期阵列邻域相同 → 一个 AEP；非周期阵列邻域各异 → N 个 AEP；和前两页的逻辑衔接 |
| 6 | Rotated CP Aperiodic Arrays | 按“作用”而不是按年份组织：产生圆极化 → 方向图综合 → 极化控制 |
| 7 | Reported ML-Assisted Surrogate Works | 四篇代表工作并列，页底写本文目标 |
| 9–11 | Surrogate Model | 结构图 + 编号要点卡；论文原图裁掉图号、图注后复用；公式用原生 Office Math |
| 12 | Element Design & Dataset | 单元结构图 + 尺寸标注（虚线框、尺寸线、地板位置小图）+ 数据集规模 |
| 14–16 | Model Evaluation | 仿真 vs 预测图阵（列标签在上、行标签在左），色标放在图阵下方，数值卡给出误差 |
| 17 | 64-Element Beam Scanning | 用户重排的版式：左侧阵列模型图 + 两行条件；右侧 Co-Polarization / Axial Ratio 两张 MATLAB 格式扫描图（轴比只画 3 dB 波束内），下方一个文本框写误差，误差的统计范围和图上的范围一致 |
| 19 | Conclusion and Outlook | 左侧“缩略图 + 贡献 + 关键数字”三行，右侧展望 |

## 使用方式

- **只作参考**：参考它的版式、信息密度、字号层级和引用写法。不要把内容或数据搬到别的项目里。
- **看分组结构**：python-pptx 打开后递归遍历组合，可以看到每个分栏是一个 `v2-*` 组，对应 SVG 里一个顶层 `<g>`。
- **数字口径**：页面上的数字来自论文终稿或注明的重新计算，口径写在讲稿附录 C。
