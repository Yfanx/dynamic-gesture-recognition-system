# 答辩应急运行手册

## 先检查后端

```powershell
cd backend
uv sync
uv run python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

浏览器访问：

```text
http://127.0.0.1:8000/api/model
```

如果 `ready` 是 `false`，说明官方模型文件或 MMAction2 环境还没接好。

## 再检查前端

```powershell
cd frontend
pnpm.cmd install
pnpm.cmd run dev
```

打开：

```text
http://127.0.0.1:5173
```

## 官方模型接入检查

后端 `.env` 至少要包含：

```env
MMACTION_CONFIG=assets/models/trained-jester-tsm-r50/tsm_r50_jester_rgb.finetune_v1.py
MMACTION_CHECKPOINT=assets/models/trained-jester-tsm-r50/best_acc_top1_epoch_8.pth
MMACTION_DEVICE=cpu
```

如果有 CUDA：

```env
MMACTION_DEVICE=cuda:0
```

## 答辩话术要点

- 系统采用前后端分离架构，Vue 负责交互展示，FastAPI 负责模型推理服务。
- 模型层接入 MMAction2 官方视频识别模型，不自行伪造模型结构。
- 数据集标签采用 Jester27 动态手势类别。
- 当前恢复的训练 best 模型 Top-1 为 96.29%，Top-5 为 99.80%。
- 前端上传视频后，后端返回 Top-K 类别及置信度，用于展示动态手势识别结果。
