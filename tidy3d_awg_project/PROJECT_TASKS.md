# Tidy3D AWG 课程项目任务清单

## 项目总目标

在三周课程周期内，使用 Tidy3D 完成一个 C-band 4-channel AWG / wavelength demultiplexer 的设计与仿真流程。项目目标包括：

- [x] 完成 silicon strip waveguide 的基础 MODE 分析，获得后续器件设计所需的基础参数
- [ ] 建立简化版 4-channel AWG / demultiplexer 的设计参数与仿真流程
- [ ] 分析 transmission spectrum、insertion loss、crosstalk、channel spacing 等关键性能指标
- [ ] 完成项目报告与结果总结

## 当前已完成事项

- [x] 完成 `tidy3d_awg_project` 项目目录初始化
- [x] 完成 Python / conda 环境配置
- [x] 成功运行第一个 Tidy3D MODE 仿真
- [x] 建立 silicon strip waveguide 的基础截面模型
- [x] 设置 core material: silicon, `n = 3.48`
- [x] 设置 cladding material: SiO2, `n = 1.44`
- [x] 设置 waveguide width = `0.50 um`
- [x] 设置 waveguide height = `0.22 um`
- [x] 完成 wavelength sweep: `[1.50, 1.525, 1.55, 1.575, 1.60] um`
- [x] 得到 `1.55 um` 处 fundamental mode 的 `n_eff ≈ 2.4446`
- [x] 验证该 MODE 仿真 credit 消耗很低，约 `0.006 FlexCredit`
- [x] 完成 waveguide width sweep: `[0.40, 0.45, 0.50, 0.55, 0.60] um`
- [x] 提取各个 width 在 `1.55 um` 的 fundamental mode `n_eff`
- [x] 成功提取各个 width 对应的 `n_group`
- [x] 生成 `waveguide_width_sweep_results.csv`
- [x] 生成 `neff_vs_width.png`
- [x] 确认 `n_eff` 随 width 增加而增大，`n_group` 在当前扫描范围内随 width 增加而减小

## 当前进度位置

- [x] 已完成项目的第一个里程碑：基础 straight silicon waveguide 的 MODE 仿真
- [x] 已获得 AWG 初始设计可用的第一组 waveguide effective index 数据
- [x] 已完成 width sweep / group index 提取
- [x] 已具备 AWG 初始参数估算所需的基础 waveguide 数据
- [ ] 尚未进入 AWG star coupler、arrayed waveguide length design、完整 demultiplexer 仿真阶段

当前项目进度可视为：已经完成从“环境搭建”到“基础波导 MODE 验证”以及“低成本参数扫描与结果整理”的阶段，下一步应进入“AWG 初始设计参数估算”阶段。

## Week 1 计划

- [x] 搭建 Tidy3D 运行环境
- [x] 建立 500 nm × 220 nm silicon strip waveguide 截面模型
- [x] 运行基础 MODE 仿真并确认存在 TE-like fundamental guided mode
- [x] 提取 `1.55 um` 附近的 `effective index`
- [x] 对 waveguide width 做低成本 MODE sweep：`[0.40, 0.45, 0.50, 0.55, 0.60] um`
- [x] 如数据提取方便，补充 `group index` 结果
- [x] 将 width sweep 结果整理成 CSV 与图像，作为后续 AWG 初始设计输入
- [x] 初步估计适合 C-band 4-channel demux 的 waveguide 参数范围

## Week 2 计划

- [x] 根据 `n_eff` / `n_group` 结果建立 AWG 初始设计参数
- [x] 确定 channel spacing、中心波长、目标 free spectral range (FSR)
- [x] 估算 arrayed waveguide 的 path length difference
- [x] 搭建简化版 4-channel AWG / wavelength demultiplexer 几何结构的第一版参数草图
- [x] 优先使用低成本方法检查几何与参数合理性
- [ ] 在必要范围内进行器件级仿真验证
- [ ] 记录不同设计参数对输出通道位置与谱线分离的影响

## Week 3 计划

- [ ] 运行简化版 4-channel demultiplexer 的最终仿真
- [ ] 提取 transmission spectrum
- [ ] 计算或整理 insertion loss
- [ ] 计算或整理 crosstalk
- [ ] 检查 channel spacing 是否满足设计目标
- [ ] 对结果做图表化展示与误差分析
- [ ] 完成课程项目报告与最终汇报材料

## 未来要做的事情

- [x] 根据 width sweep 结果选定第一版 AWG 设计用的 waveguide width
- [x] 确定 4-channel demux 的中心波长与 channel spacing
- [x] 估算 free spectral range (FSR) 与 arrayed waveguide path length difference
- [ ] 从单根 straight waveguide 过渡到简化器件级 demultiplexer 模型
- [ ] 最后完成 transmission spectrum、insertion loss、crosstalk、channel spacing 的系统分析

## 本轮 width sweep 结果摘要

- [x] `width = 0.40 um` 时，`n_eff ≈ 2.2275`，`n_group ≈ 4.2449`
- [x] `width = 0.45 um` 时，`n_eff ≈ 2.3527`，`n_group ≈ 4.1444`
- [x] `width = 0.50 um` 时，`n_eff ≈ 2.4446`，`n_group ≈ 4.0512`
- [x] `width = 0.55 um` 时，`n_eff ≈ 2.5131`，`n_group ≈ 3.9749`
- [x] `width = 0.60 um` 时，`n_eff ≈ 2.5657`，`n_group ≈ 3.9142`
- [x] 在当前扫描范围内，`0.50 um` 是一个合理的基准尺寸，因为它与已有 baseline 仿真一致，且折射率参数位于中间区间，适合作为第一版 AWG 设计起点

## Week 2 当前产出

- [x] 选定第一版 AWG 设计采用的 waveguide width：`0.50 um`
- [x] 建议 4-channel C-band 目标参数：`center wavelength = 1550 nm`
- [x] 建议 channel spacing：`1.6 nm`（约 `200 GHz`）
- [x] 建议 channel centers：`1547.6, 1549.2, 1550.8, 1552.4 nm`
- [x] 建议 target FSR：`19.2 nm`
- [x] 选定第一版 diffraction order：`m = 81`
- [x] 估算 arrayed waveguide path length difference：`ΔL ≈ 30.99 um`
- [x] 生成 `awg_initial_parameters.csv`
- [x] 生成 `awg_channel_plan.csv`
- [x] 生成 `awg_arrayed_waveguide_lengths.csv`
- [x] 生成 `AWG_INITIAL_DESIGN.md`
- [x] 生成 `awg_initial_design.ipynb`
- [x] 生成 `simplified_awg_geometry.ipynb`
- [x] 整理 `1-input / 4-output / 16-arm` 的第一版几何参数
- [x] 生成 `simplified_awg_geometry_ports.csv`
- [x] 生成 `simplified_awg_geometry_arms.csv`
- [x] 生成简化几何布局预览图 `simplified_awg_geometry_layout.png`

## Credit 消耗说明

### 会消耗 Tidy3D credit 的任务

- [x] 已完成的基础 MODE 仿真（低 credit 消耗）
- [x] 已完成的 waveguide width MODE sweep（低 credit 消耗）
- [ ] 后续如进行 group index 相关 MODE 扫描（低到中等 credit 消耗，取决于扫描数量）
- [ ] AWG / demultiplexer 的 FDTD 或器件级云端仿真（相对更高 credit 消耗）

### 不会消耗 Tidy3D credit 的任务

- [x] 本地整理仿真结果
- [x] 本地撰写项目计划与进度报告
- [x] 本地 CSV 后处理
- [x] 本地绘制 `n_eff vs waveguide width` 图
- [ ] 本地计算 insertion loss、crosstalk、channel spacing
- [ ] 本地撰写最终报告与汇报材料

## 下一步优先任务

- [ ] 基于 `simplified_awg_geometry.ipynb` 决定是否需要调整 FPR length、array pitch、output pitch
- [ ] 为 simplified AWG 选择第一版器件仿真策略：继续低成本近似，或进入小规模云端验证
- [ ] 为后续 transmission spectrum 提取预留输出端口定义和命名规范
- [ ] 在保证 credit 可控的前提下，准备第一版 simplified demultiplexer 仿真
