# AWG 初始设计参数建议

## 设计目的

本文件用于把当前已完成的 straight waveguide MODE 结果，转化为一版适合课程项目推进的 4-channel C-band AWG / demultiplexer 初始参数。

## 推荐的第一版目标参数

- Waveguide width: `0.50 um`
- Waveguide height: `0.22 um`
- Core / cladding: silicon / SiO2
- `n_eff @ 1550 nm ≈ 2.4446`
- `n_group @ 1550 nm ≈ 4.0512`
- Channel count: `4`
- Center wavelength: `1550 nm`
- Channel spacing: `1.6 nm`
- Suggested channel centers: `1547.6, 1549.2, 1550.8, 1552.4 nm`

## 为什么先选 0.50 um

- 它与前面的 baseline MODE 结果一致，便于和已有结果直接对照
- 它的 `n_eff` 与 `n_group` 位于本轮 width sweep 的中间区间，不是过窄也不是过宽
- 对于课程项目的第一版 AWG 参数估算来说，这样的基准点更稳妥，也更方便后续解释设计选择

## 建议的 AWG 初始参数

- Target free spectral range (FSR): `19.2 nm`
- Chosen diffraction order: `m = 81`
- Actual FSR from `lambda0 / m`: `≈ 19.1358 nm`
- Path length difference `ΔL = m * lambda0 / n_group`: `≈ 30.99 um`
- Suggested arrayed waveguide count: `16`
- Suggested input count: `1`
- Suggested output count: `4`

## 几何起点建议

以下几项是为“简化版课程项目建模”准备的第一版 heuristic 参数，还不是最终优化结果：

- Suggested FPR / slab length: `50 um`
- Suggested array pitch at slab interface: `1.5 um`
- Suggested output pitch: `2.0 um`
- Minimum bend radius: `10 um`

这些值的作用是帮助你先搭一版结构，再用低成本检查几何是否合理，而不是一开始就追求最终最优器件。

## 设计解释

4 个通道的中心波长跨度为 `4.8 nm`。为了避免相邻 diffraction order 过近带来的混叠风险，这里先把目标 FSR 设为约 `19.2 nm`，也就是约为通道中心跨度的 4 倍。由此得到 `m = 81`，再结合当前 `n_group ≈ 4.0512`，得到第一版 arrayed waveguide 的 path length difference `ΔL ≈ 30.99 um`。

这一版参数的优点是：

- 计算关系清楚，适合写进课程报告
- 数值量级温和，适合作为 simplified AWG 的第一版设计起点
- 便于后续根据 transmission spectrum 再做二次调整

## 相关文件

- [awg_initial_parameters.csv](/Users/luojiahua/Library/CloudStorage/OneDrive-UW/Slides/Slides/EE588/project/tidy3d_awg_project/results/tables/awg_initial_parameters.csv)
- [awg_channel_plan.csv](/Users/luojiahua/Library/CloudStorage/OneDrive-UW/Slides/Slides/EE588/project/tidy3d_awg_project/results/tables/awg_channel_plan.csv)
- [awg_arrayed_waveguide_lengths.csv](/Users/luojiahua/Library/CloudStorage/OneDrive-UW/Slides/Slides/EE588/project/tidy3d_awg_project/results/tables/awg_arrayed_waveguide_lengths.csv)
