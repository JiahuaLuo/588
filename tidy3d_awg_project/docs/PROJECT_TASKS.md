# Tidy3D AWG 课程项目任务清单

## 项目总目标

在三周课程周期内，使用 Tidy3D 完成一个 C-band 4-channel AWG / wavelength demultiplexer 的设计与仿真流程。项目目标包括：

- [x] 完成 silicon strip waveguide 的基础 MODE 分析，获得后续器件设计所需的基础参数
- [x] 建立简化版 4-channel AWG / demultiplexer 的设计参数与仿真流程
- [x] 分析 transmission spectrum、insertion loss、crosstalk、channel spacing 等关键性能指标
- [x] 完成项目报告与结果总结

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
- [x] 生成 `results/tables/waveguide_width_sweep_results.csv`
- [x] 生成 `results/figures/neff_vs_width.png`
- [x] 确认 `n_eff` 随 width 增加而增大，`n_group` 在当前扫描范围内随 width 增加而减小

## 当前进度位置

- [x] 已完成项目的第一个里程碑：基础 straight silicon waveguide 的 MODE 仿真
- [x] 已获得 AWG 初始设计可用的第一组 waveguide effective index 数据
- [x] 已完成 width sweep / group index 提取
- [x] 已具备 AWG 初始参数估算所需的基础 waveguide 数据
- [x] 已完成 AWG star coupler / arrayed waveguide length 的初步参数设计与简化频谱分析
- [x] 已完成一轮低成本 2D Tidy3D FDTD 器件级验证（output FPR / phased-array aperture）
- [ ] 尚未完成高保真完整 demultiplexer 3D FDTD 仿真

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
- [x] 在必要范围内进行低成本器件级近似验证
- [x] 记录不同设计参数对输出通道位置与谱线分离的影响

## Week 3 计划

- [x] 运行简化版 4-channel demultiplexer 的最终频谱分析
- [x] 提取 transmission spectrum
- [x] 计算或整理 insertion loss
- [x] 计算或整理 crosstalk
- [x] 检查 channel spacing 是否满足设计目标
- [x] 对结果做图表化展示与误差分析
- [x] 完成课程项目报告与最终汇报材料

## 未来要做的事情

- [x] 根据 width sweep 结果选定第一版 AWG 设计用的 waveguide width
- [x] 确定 4-channel demux 的中心波长与 channel spacing
- [x] 估算 free spectral range (FSR) 与 arrayed waveguide path length difference
- [x] 从单根 straight waveguide 过渡到简化器件级 demultiplexer 模型
- [x] 最后完成 transmission spectrum、insertion loss、crosstalk、channel spacing 的系统分析

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
- [x] 生成 `results/tables/awg_initial_parameters.csv`
- [x] 生成 `results/tables/awg_channel_plan.csv`
- [x] 生成 `results/tables/awg_arrayed_waveguide_lengths.csv`
- [x] 生成 `docs/AWG_INITIAL_DESIGN.md`
- [x] 生成 `awg_initial_design.ipynb`
- [x] 生成 `simplified_awg_geometry.ipynb`
- [x] 整理 `1-input / 4-output / 16-arm` 的第一版几何参数
- [x] 生成 `results/tables/simplified_awg_geometry_ports.csv`
- [x] 生成 `results/tables/simplified_awg_geometry_arms.csv`
- [x] 生成简化几何布局预览图 `results/figures/simplified_awg_geometry_layout.png`

## Credit 消耗说明

### 会消耗 Tidy3D credit 的任务

- [x] 已完成的基础 MODE 仿真（低 credit 消耗）
- [x] 已完成的 waveguide width MODE sweep（低 credit 消耗）
- [ ] 后续如进行 group index 相关 MODE 扫描（低到中等 credit 消耗，取决于扫描数量）
- [x] AWG output FPR 的 2D FDTD 器件级云端仿真（已完成，低于 1 FlexCredit）
- [ ] 完整 AWG / demultiplexer 的 3D FDTD 或更高保真器件级云端仿真（相对更高 credit 消耗，如需继续提高结果保真度）

### 不会消耗 Tidy3D credit 的任务

- [x] 本地整理仿真结果
- [x] 本地撰写项目计划与进度报告
- [x] 本地 CSV 后处理
- [x] 本地绘制 `results/figures/neff_vs_width.png`
- [x] 本地计算 insertion loss、crosstalk、channel spacing
- [x] 本地撰写最终报告与汇报材料

## 下一步优先任务

- [x] 基于 `simplified_awg_geometry.ipynb` 决定是否需要调整 FPR length、array pitch、output pitch
- [x] 为 simplified AWG 选择第一版器件仿真策略：继续低成本近似，完成本地频谱分析
- [x] 为后续 transmission spectrum 提取预留输出端口定义和命名规范
- [x] 在保证 credit 可控的前提下，准备第一版 simplified demultiplexer 仿真

## 本周最终收尾结果

- [x] 新增 `scripts/awg_spectral_analysis.py`，基于已有 MODE 与 AWG 参数生成简化版 transmission spectrum
- [x] 生成 `results/tables/awg_simplified_spectrum.csv`
- [x] 生成 `results/tables/awg_channel_metrics.csv`
- [x] 生成 `results/figures/awg_transmission_spectra.png`
- [x] 生成 `results/figures/awg_channel_metrics.png`
- [x] 生成 `docs/AWG_FINAL_RESULTS.md`
- [x] 生成 `reports/EE588_AWG_Final_Project_Report.docx`

## 新增高仿真验证结果

- [x] 新增 `scripts/awg_high_fidelity_validation.py`
- [x] 完成 4 个目标波长的 2D Tidy3D FDTD output-FPR 验证
- [x] 生成 `results/tables/awg_high_fidelity_results.csv`
- [x] 生成 `docs/AWG_HIGH_FIDELITY_SUMMARY.md`
- [x] 生成 `results/figures/awg_high_fidelity_transmission.png`
- [x] 保存云端仿真结果至 `data/high_fidelity_awg/`
- [x] 确认 baseline 4-channel case 在高仿真中存在随 wavelength 变化的主输出迁移
- [x] 新增高仿真 routing quality rubric：`good / general / passing / poor`
- [x] 新增 `scripts/awg_hf_optimizer.py`
- [x] 生成 `results/tables/awg_hf_optimization_results.csv`
- [x] 生成 `docs/AWG_HF_OPTIMIZATION_SUMMARY.md`
- [x] 生成 `results/figures/awg_hf_optimization_scan.png`
- [x] 生成 `results/figures/awg_hf_optimization_verification.png`
- [x] 确认 `array pitch = 1.2 um / output pitch = 1.6 um / output offset = 0.6 um` 为本轮局部最优配置
- [x] 新增 `scripts/awg_hf_global_optimizer.py`
- [x] 生成 `results/tables/awg_hf_global_optimization_results.csv`
- [x] 生成 `docs/AWG_HF_GLOBAL_OPTIMIZATION_SUMMARY.md`
- [x] 生成 `results/figures/awg_hf_global_optimization_scan.png`
- [x] 生成 `results/figures/awg_hf_global_optimization_channels.png`
- [x] 确认 `array pitch = 1.15 um / output pitch = 1.60 um / output offset = 0.65 um` 为本轮全 4-channel 优先的全局最优配置

## Stretch Goals 进展

- [x] 8-channel：完成一轮 8-output layout 的器件级尝试，`1550 nm` 在该配置下主输出落在 `out_7`
- [x] 温度依赖：完成 `+40 K` 相位漂移测试，主输出从 baseline 的高编号端口回移到较低编号端口
- [x] 降低串扰 / 插损：完成一轮 `array pitch / output pitch / output offset` 调整尝试，中心波长主输出集中度由 `0.328` 提升到 `0.466`
- [ ] 8-channel 的完整多波长系统验证仍未完成
- [ ] 温度依赖的系统扫描和热稳定设计仍未完成
- [ ] 串扰和插损的全通带系统优化仍未完成

## 结果说明

- [x] 当前最终结果采用的是“基于已有 Tidy3D MODE 数据的本地简化 AWG 频谱模型”
- [x] 该结果适合课程项目的第一版最终提交与结果总结
- [x] 当前已补充一轮 2D Tidy3D FDTD 器件级验证，可作为高于 local model 的第二层证据
- [x] 当前已给出清晰的器件级质量分级标准：`good / general / passing / poor`
- [x] 当前 baseline 4-channel 高仿真整体处于 `passing` 水平
- [x] 当前优化后中心波长可达到 `general` 水平，但全 4-channel 尚未整体达到 `general`
- [x] 当前全局优化后，最佳 4-channel 平均表现仍处于 `passing` 水平，但均衡性优于原 baseline
- [ ] 该结果仍不是完整高保真 Tidy3D 3D FDTD 全器件仿真，如后续还有时间，可继续补充
