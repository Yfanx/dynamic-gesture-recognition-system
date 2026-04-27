# 识别参数说明

本页参数来自恢复的训练产物：

- `assets/models/trained-jester-tsm-r50/metadata.json`
- `assets/models/trained-jester-tsm-r50/evaluation.json`
- `assets/models/trained-jester-tsm-r50/tsm_r50_jester_video_infer.py`

## 页面展示参数

| 参数 | 页面值 | 准确含义 | 数据来源 |
| --- | --- | --- | --- |
| 类别范围 | Jester 27 类 | 模型输出层包含 27 个动态手势类别，对应 Jester 数据集的 27 类动作。 | `metadata.json` 的 `num_classes = 27` |
| 视频模式 | RGB 时序识别 | 输入是普通 RGB 视频帧序列，不是骨骼点、光流或深度图。 | 推理配置使用 `VideoDataset`、`DecordDecode`、`FormatShape(input_format='NCHW')` |
| 特征维度 | 2048 | TSM R50 使用 ResNet-50 作为主干网络，分类头前的特征通道维度为 2048。 | TSM R50 模型结构 |
| 序列长度 | 8 | 每段视频采样 8 个片段/帧用于时序建模。 | 推理配置 `SampleFrames(num_clips=8, clip_len=1)` |
| 参考准确率 | 96.29% | 在验证集上的 Top-1 Accuracy，即最高概率类别等于真实类别的比例。 | `evaluation.json` 的 `acc/top1 = 0.9629404206` |
| 宏平均 F1 | 95.88% | 对 27 个类别分别计算 F1 后取平均，能反映各类别整体均衡表现。 | 由 `evaluation.json` 混淆矩阵计算得到 `0.9588425333` |

## 答辩表述建议

可以这样说明：

“本系统使用 TSM R50 进行 RGB 视频时序分类。模型面向 Jester 27 类动态手势，每次从视频中采样 8 个时序片段输入网络；ResNet-50 主干在分类头前输出 2048 维特征。恢复后的最佳模型在验证集上的 Top-1 准确率为 96.29%，宏平均 F1 为 95.88%，说明模型不仅整体准确率较高，各类别的识别表现也比较均衡。”

## 补充指标

- Top-5 Accuracy：99.80%
- Mean Class Accuracy：95.89%
- 验证集样本数：14787
