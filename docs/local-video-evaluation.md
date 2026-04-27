# 本地测试视频推理结果

测试路径：`D:\Yfanx\Videos`

推理环境：云端 MMAction2 1.2.0、PyTorch 2.8.0、CUDA 可用。

模型：`jester_tsm_r50_finetune_v1_final/best_acc_top1_epoch_8.pth`

## 结论

10 个自录测试视频 Top-1 全部命中，模型用于答辩演示是合理的。

`Zooming Out With Two Fingers` 虽然预测正确，但置信度只有 31.5%，说明这个动作和 `Shaking Hand`、`Zooming Out With Full Hand` 的视觉边界较接近。答辩演示时建议优先使用置信度更高的滑动、上下左右、Thumb Up/Down、Stop Sign 视频。

## 明细

| 视频文件 | 期望动作 | Top-1 | 置信度 | 是否命中 |
| --- | --- | --- | ---: | --- |
| Sliding Two Fingers Down.mp4 | Sliding Two Fingers Down | Sliding Two Fingers Down | 90.6% | 是 |
| Stop Sign.mp4 | Stop Sign | Stop Sign | 83.4% | 是 |
| Swiping Down.mp4 | Swiping Down | Swiping Down | 98.0% | 是 |
| Swiping Left.mp4 | Swiping Left | Swiping Left | 97.8% | 是 |
| Swiping Right.mp4 | Swiping Right | Swiping Right | 98.9% | 是 |
| Swiping Up.mp4 | Swiping Up | Swiping Up | 99.7% | 是 |
| Thumb Down.mp4 | Thumb Down | Thumb Down | 100.0% | 是 |
| Thumb Up.mp4 | Thumb Up | Thumb Up | 99.8% | 是 |
| Zooming Out With Two Fingers.mp4 | Zooming Out With Two Fingers | Zooming Out With Two Fingers | 31.5% | 是 |
| Zooming in With Two Fingers.mp4 | Zooming In With Two Fingers | Zooming In With Two Fingers | 62.7% | 是 |
