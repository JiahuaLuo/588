# EE588 AWG 演讲 PPT 图片放置指南

> 对应文件：`EE588_AWG_Presentation.tex`（v2，15页）  
> 所有图片路径均以 `.tex` 文件所在目录为根目录

---

## 总览

| 页码 | 幻灯片标题 | 需要图片 | 图片文件 |
|------|-----------|---------|---------|
| 1    | 标题页 | 否 | — |
| 2    | Motivation I：数据中心带宽挑战 | 否（含 TikZ 示意图） | — |
| 3    | Motivation II：为什么选硅基 AWG？ | 否 | — |
| 4    | AWG 工作原理 | 否（含 TikZ 结构图） | — |
| 5    | 三层仿真策略 | 否 | — |
| **6**  | **Wave 导 MODE 分析** | **是** | `results/figures/neff_vs_width.png` |
| **7**  | **AWG 初始设计参数** | **是** | `results/figures/simplified_awg_geometry_layout.png` |
| **8**  | **简化频谱模型** | **是** | `results/figures/awg_transmission_spectra.png` |
| 9    | FDTD 验证设置与评级标准 | 否 | — |
| **10** | **Baseline FDTD 结果** | **是** | `results/figures/awg_high_fidelity_transmission.png` |
| **11** | **优化过程（第1–3轮）** | **是** | `results/figures/awg_hf_optimization_scan.png` |
| **12** | **关键改进：N=24 阵列臂** | **是** | `results/figures/awg_improved_design_channels.png` |
| 13   | Stretch Goals | 否 | — |
| 14   | 完整结果汇总 | 否 | — |
| 15   | 结论与展望 | 否 | — |

---

## 逐页详细说明

---

### 第 2 页 — Motivation I

**无需插图**。左列是文字要点，右列有一个用 LaTeX TikZ 代码画的简单分光示意图（一根光纤输入 → AWG 方框 → 4路输出箭头），已内置在 `.tex` 文件里，无需额外操作。

---

### 第 3 页 — Motivation II

**无需插图**。左列文字，右列是一个 ITU-T 通道计划的小表格，已内置。

---

### 第 6 页 — 波导 MODE 分析

**图片位置：右列（右侧 53% 宽度区域）**

```
文件：results/figures/neff_vs_width.png
位置：右侧列，\includegraphics[width=\linewidth]{...}
大小：自动铺满右列宽度（约 8 cm × 5 cm 的显示效果）
内容说明：双纵轴折线图，X轴是波导宽度（400–600 nm），
          左Y轴是 n_eff（2.2–2.6），右Y轴是 n_group（3.9–4.3）
注意：500 nm 那个数据点应有高亮标注（图中应有金色/加粗标记）
```

左列放的是数据表格（5行宽度数据），图片在右列作为视觉支撑。

---

### 第 7 页 — AWG 初始设计参数

**图片位置：右列（右侧 53% 宽度区域）**

```
文件：results/figures/simplified_awg_geometry_layout.png
位置：右侧列，\includegraphics[width=\linewidth]{...}
大小：自动铺满右列宽度
内容说明：简化版 AWG 俯视图，显示 1 根输入波导、两个 FPR（星形耦合器）、
          16 根阵列臂（长度递增）、4 根输出波导
注意：图中应能看到阵列臂的蜿蜒结构和两端的扇形 FPR 区域
```

左列放的是参数推导表（约 9 行），图片在右列补充结构直觉。

---

### 第 8 页 — 简化频谱模型

**图片位置：右列（右侧 53% 宽度区域）**

```
文件：results/figures/awg_transmission_spectra.png
位置：右侧列，\includegraphics[width=\linewidth]{...}
大小：自动铺满右列宽度
内容说明：4条叠加的传输谱曲线，X轴是波长（1544–1556 nm），
          Y轴是透射率（线性或 dB）。4个峰值分别对准
          1547.6 / 1549.2 / 1550.8 / 1552.4 nm
注意：图中4条曲线颜色不同，图例标注 ch1–ch4
```

左列放的是公式和预测指标小表格。

---

### 第 10 页 — Baseline FDTD 结果

**图片位置：右列（右侧 53% 宽度区域）**

```
文件：results/figures/awg_high_fidelity_transmission.png
位置：右侧列，\includegraphics[width=\linewidth]{...}
大小：自动铺满右列宽度
内容说明：4个子图（每个波长一个），每个子图是 4 根柱子（out_1–out_4 端口），
          高度表示该端口收到的功率。随着波长增加，最高柱子从 out_3 移动到 out_4
注意：最高柱子（主输出）应该有颜色高亮或标注
```

左列放的是结果数据表格（4行 × 4列）和关键发现文字框。

---

### 第 11 页 — 优化过程（第1–3轮）

**图片位置：左列（左侧 49% 宽度区域）**

```
文件：results/figures/awg_hf_optimization_scan.png
位置：左侧列，\includegraphics[width=\linewidth]{...}
大小：自动铺满左列宽度
内容说明：柱状图，X轴是 9 个扫描配置（optscan_baseline, a, b, ..., h），
          Y轴是 1550.8 nm 处的 dominant fraction，
          不同颜色区分质量等级（general/passing/poor）
注意：optscan_c 那根柱子最高（0.466），应标注 "general" 等级
```

右列放的是 4 轮优化的进展汇总表格（4行）和文字总结。

---

### 第 12 页 — 关键改进：N=24 阵列臂【新页面】

**图片位置：右列（右侧 53% 宽度区域）**

```
文件：results/figures/awg_improved_design_channels.png
位置：右侧列，\includegraphics[width=\linewidth]{...}
大小：自动铺满右列宽度
内容说明：4列子图（impr_A / impr_B / impr_C / impr_D），
          每列子图内是分组柱状图，X轴是4个波长，
          4根柱子对应 out_1–out_4 的功率
          impr_C 那列可看到 out_3 在多个波长下一致最高
注意：这是新生成的图，在演讲中会首次展示。
      impr_C 那列是本次最优结果，可以用箭头或标注框圈出
```

左列放的是物理解释（为什么 N 更多有效）、实验配置表格（4行）和逐通道结果小表（4行 × 4列）。

---

### 第 14 页 — 完整结果汇总

**无图片**。整页是一个汇总大表格（5行，含 Baseline + R1–R4），外加两列简洁文字要点。第4轮（N=24）那行用金色底色高亮。不需要额外插图。

---

## 快速核对清单

编译前请确认以下图片文件全部存在：

```bash
ls results/figures/neff_vs_width.png
ls results/figures/simplified_awg_geometry_layout.png
ls results/figures/awg_transmission_spectra.png
ls results/figures/awg_high_fidelity_transmission.png
ls results/figures/awg_hf_optimization_scan.png
ls results/figures/awg_improved_design_channels.png   # 新生成的图
```

如果某张图缺失，对应的 `\includegraphics` 命令会报 LaTeX 警告但不会中断编译——缺失位置会显示为空白框加图片路径文字。

---

## 编译命令

```bash
cd /path/to/tidy3d_awg_project
pdflatex EE588_AWG_Presentation.tex
pdflatex EE588_AWG_Presentation.tex   # 第二次运行更新页码/引用
```

输出文件：`EE588_AWG_Presentation.pdf`

---

## 引用来源说明（Slide 2 和 Slide 3）

| 编号 | 幻灯片 | 引用内容 |
|------|--------|---------|
| [1] | 第2页 | Cisco Annual Internet Report 2018–2023, White Paper, 2022 |
| [2] | 第2页 | D. A. B. Miller, "Rationale and challenges for optical interconnects," *Proc. IEEE*, vol. 88, pp. 728–749, 2000 |
| [3] | 第3页 | M. K. Smit, "New focusing and dispersive planar component based on an optical phased array," *Electronics Letters*, vol. 24, pp. 385–386, 1988 |
| [4] | 第3页 | M. K. Smit & C. van Dam, "PHASAR-based WDM-devices: Principles, design and applications," *IEEE JSTQE*, vol. 2, pp. 236–250, 1996 |
| [5] | 第3页 | L. Chrostowski & M. Hochberg, *Silicon Photonics Design*, Cambridge University Press, 2015 |
| [6] | 第3页 | ITU-T G.694.1, "Spectral grids for WDM applications: DWDM frequency grid," 2012 |
