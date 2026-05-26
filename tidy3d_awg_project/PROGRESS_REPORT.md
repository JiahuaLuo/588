# Project Title

C-band 4-Channel AWG / Wavelength Demultiplexer Design Using Tidy3D

## Project Goal

本项目的目标是使用 Tidy3D 完成一个面向 C-band 的 4-channel AWG / demultiplexer 的基础设计与仿真。整体流程将从单根 silicon strip waveguide 的 MODE 分析开始，逐步过渡到简化版 AWG 器件级仿真，并最终对 transmission spectrum、insertion loss、crosstalk、channel spacing 等指标进行分析。

## Tool Choice

本项目选择 Tidy3D 作为主要仿真平台，原因如下：

- Tidy3D MODE 适合快速提取 waveguide 的 effective index、group index、TE-like mode 等基础参数
- Tidy3D FDTD 适合后续对 AWG / demultiplexer 进行器件级电磁仿真
- 对于课程项目而言，可以先利用低成本的 MODE 结果完成参数预设计，再谨慎进入 credit 消耗更高的 FDTD 阶段

## Work Completed So Far

目前已经完成以下工作：

- 已配置好 Python / conda 环境
- 已成功运行一个 Tidy3D MODE 仿真
- 已建立 silicon strip waveguide 的基础几何与材料模型
- 已完成一组波长扫描，用于检查 guided mode 的存在与有效折射率变化
- 已确认当前基础仿真的 FlexCredit 消耗非常低，适合作为项目初始阶段的方法
- 已完成 waveguide width sweep，并获得一组更系统的 `effective index` 与 `group index` 数据
- 已输出 CSV 结果文件与 `n_eff vs width` 图像，可直接用于后续 AWG 参数设计
- 已完成一版 4-channel C-band AWG 初始参数估算
- 已整理出 channel plan、FSR、AWG order 与 arrayed waveguide path length difference
- 已整理一版 simplified AWG geometry，用于后续器件建模前的低成本检查

## Current Simulation Setup

当前阶段已经完成两类 straight silicon strip waveguide 的 MODE 仿真设置：

- Core material: silicon, refractive index `n = 3.48`
- Cladding material: SiO2, refractive index `n = 1.44`
- Waveguide height: `0.22 um`
- Baseline waveguide width: `0.50 um`
- Baseline wavelength sweep: `1.50, 1.525, 1.55, 1.575, 1.60 um`
- Width sweep at fixed wavelength `1.55 um`: `0.40, 0.45, 0.50, 0.55, 0.60 um`
- 求解类型：Tidy3D MODE
- 目标：提取 TE-like mode 的 effective index / group index，并为 AWG 初始设计提供参数

## Current Results

当前已得到的核心结果如下：

- Baseline case:
- `500 nm × 220 nm` silicon strip waveguide
- `SiO2` cladding
- `wavelength = 1550 nm`
- fundamental mode effective index `n_eff ≈ 2.4446`

Width sweep results at `1550 nm`:

- `width = 0.40 um`: `n_eff ≈ 2.2275`, `n_group ≈ 4.2449`
- `width = 0.45 um`: `n_eff ≈ 2.3527`, `n_group ≈ 4.1444`
- `width = 0.50 um`: `n_eff ≈ 2.4446`, `n_group ≈ 4.0512`
- `width = 0.55 um`: `n_eff ≈ 2.5131`, `n_group ≈ 3.9749`
- `width = 0.60 um`: `n_eff ≈ 2.5657`, `n_group ≈ 3.9142`

First-pass AWG target parameters:

- Selected waveguide width: `0.50 um`
- Channel count: `4`
- Center wavelength: `1550 nm`
- Channel spacing: `1.6 nm` (about `200 GHz`)
- Suggested channel centers: `1547.6, 1549.2, 1550.8, 1552.4 nm`
- Target FSR: `19.2 nm`
- Chosen AWG order: `m = 81`
- Estimated path length difference: `ΔL ≈ 30.99 um`

First-pass simplified geometry parameters:

- `1 input / 4 outputs / 16 arrayed waveguides`
- Suggested `FPR length ≈ 50 um`
- Suggested `array pitch ≈ 1.5 um`
- Suggested `output pitch ≈ 2.0 um`
- Suggested `minimum bend radius ≈ 10 um`
- Geometry preview organized in `simplified_awg_geometry.ipynb`

## Interpretation of Results

从当前结果来看，`mode 0` 的 `n_eff` 最高，因此可以将其视为当前结构中的 fundamental guided mode。

这一结果说明该 waveguide 在当前几何与材料参数下，能够支持一个主要被限制在 core 附近的 guided mode。这对于后续的器件设计是一个重要前提，因为 AWG / wavelength demux 的建模通常需要先确定单模或准单模工作条件下的传播常数与折射率参数。

此外，这个 `n_eff` 结果可以直接作为后续 AWG / wavelength demux 初始设计参数的一部分，用于估算传播相位、有效光程差，以及后续 arrayed waveguide 的长度设计。

从 width sweep 的结果还可以看到，在当前扫描范围内，随着 waveguide width 增加，fundamental mode 的 `n_eff` 单调上升，而 `n_group` 呈下降趋势。这说明波导横向尺寸对传播常数和色散特性都有明显影响，因此在进入 AWG 设计前，先做这一轮低成本参数扫描是有价值的。

从工程角度看，`0.50 um` 这一组结果仍然是一个很合适的第一版设计起点。一方面，它与前面的 baseline 结果一致；另一方面，它的 `n_eff` 和 `n_group` 位于本轮扫描结果的中间区间，更适合作为后续 AWG / demultiplexer 初始参数的参考值。

在此基础上，当前已经可以提出一版适合课程项目推进的 4-channel C-band 目标参数。将 channel spacing 先设为 `1.6 nm`，相当于约 `200 GHz`，既足够体现多通道 demultiplexer 的特征，又不会让第一版设计过于拥挤。进一步选择 `FSR ≈ 19.2 nm`、`m = 81`、`ΔL ≈ 30.99 um`，可以得到一组量级合理、逻辑清晰、适合写入课程报告的 AWG 初始设计参数。

几何层面上，目前也已经完成了一版 simplified layout 的参数整理。这里采用的是“先给出可解释、可视化、便于继续修改的第一版参数草图”的思路，而不是直接声称已经完成严格器件优化。这样做更适合三周课程项目的节奏，因为它能让后续几何调整、端口命名和器件级仿真准备都有清楚的起点。

## Next Steps

下一步计划从“基础波导参数提取”转向“AWG 初始设计参数估算”：

- 已完成第一版 AWG 设计采用的 waveguide width 选择：`0.50 um`
- 已完成 4-channel demux 的中心波长与 channel spacing 设定
- 已完成 free spectral range (FSR) 与 path length difference 的初步估算
- 已完成 simplified AWG / demultiplexer 的第一版几何参数整理
- 下一步应检查是否需要微调 FPR length、array pitch、output pitch
- 然后决定是继续做低成本近似分析，还是进入简化版器件仿真

完成这一阶段后，就可以更有依据地进入简化版 AWG / demultiplexer 的结构设计与仿真。

## Final Week Update

本周已经把项目从“参数草图阶段”推进到了“可提交的最终结果包阶段”。考虑到课程时间和 Tidy3D credit 成本，本轮没有直接进行高成本完整 FDTD 器件仿真，而是基于已经完成的 MODE 数据、AWG 初始参数和阵列长度设计，补充完成了一个本地 simplified AWG spectrum analysis workflow。

这一轮新增的最终分析内容包括：

- 生成 `awg_simplified_spectrum.csv`
- 生成 `awg_channel_metrics.csv`
- 生成 `report_assets/awg_transmission_spectra.png`
- 生成 `report_assets/awg_channel_metrics.png`
- 生成 `AWG_FINAL_RESULTS.md`
- 生成 `EE588_AWG_Final_Project_Report.docx`

在该 simplified 分析中，4 个输出通道的峰值波长分别对准 `1547.6, 1549.2, 1550.8, 1552.4 nm`，与目标 channel plan 一致。平均相邻通道 spacing 为 `1.6 nm`，与设计目标一致。使用当前的低成本阵列因子近似模型，得到的平均 insertion loss 约为 `3.0 dB`，worst-case crosstalk 约为 `-13.7 dB`，平均 `3 dB` bandwidth 约为 `1.06 nm`。

这意味着目前项目已经具备一套完整且自洽的提交材料链条：

- 有 straight waveguide 的 MODE 基础结果
- 有 width sweep 与 `n_eff / n_group` 数据
- 有 AWG 初始参数与 simplified geometry
- 有 transmission spectrum、insertion loss、crosstalk、channel spacing 的最终整理结果
- 有最终项目报告文档

因此，从课程项目提交角度看，当前版本已经可以作为一套完整的 final submission。后续如果还有额外时间，最优先的增强方向仍然是补做一次或少量几次更高保真的 Tidy3D 器件级仿真，用于进一步验证 passband 形状、插损与串扰。

## Risks and Limitations

当前阶段仍存在以下风险与限制：

- 目前结果仅来自单根 straight waveguide 的 MODE 仿真，尚不能代表完整 AWG 器件性能
- 尽管已经获得 `effective index` 和 `group index`，但这些仍然只是单根波导层面的参数
- 后续进入 FDTD 或器件级仿真时，FlexCredit 消耗会明显高于当前 MODE 阶段
- 课程项目时间只有三周，因此需要优先采用低成本、可快速迭代的方法推进
- 如果后续结构过于复杂，可能需要先做简化版 AWG / demultiplexer，而不是一开始就追求完整高精度器件模型
