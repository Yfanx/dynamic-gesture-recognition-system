# Dynamic Gesture Recognition System

Vue + FastAPI dynamic hand gesture recognition demo for graduation defense.

The project is rebuilt around MMAction2 video recognition. The default local model is the recovered Jester TSM R50 fine-tuned checkpoint, and the original official MMAction2 checkpoint is kept under `assets/models/` as a fallback/reference.

## Project Layout

```text
dynamic-gesture-recognition-system/
  backend/          FastAPI API service and MMAction2 inference adapter
  frontend/         Vue + Vite web UI
  assets/models/   Official model config/checkpoint files
  assets/samples/  Local demo videos
  docs/            Module notes and defense usage guide
```

## Backend

```powershell
cd backend
uv sync
Copy-Item .env.example .env
uv run python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

For official MMAction2 inference, install MMAction2 in the same Python environment and configure:

```env
MMACTION_CONFIG=assets/models/trained-jester-tsm-r50/tsm_r50_jester_video_infer.py
MMACTION_CHECKPOINT=assets/models/trained-jester-tsm-r50/best_acc_top1_epoch_8.pth
MMACTION_DEVICE=cpu
```

Use `cuda:0` when CUDA and PyTorch GPU are available.

## Frontend

```powershell
cd frontend
pnpm.cmd install
pnpm.cmd run dev
```

Open the Vite URL and upload a gesture video. The UI calls `http://127.0.0.1:8000/api/predict`.

## Model Assets

This repo does not vendor MMAction2 or large checkpoint files. The backend intentionally uses the official MMAction2 APIs when available:

- `mmaction.apis.init_recognizer`
- `mmaction.apis.inference_recognizer`

Recovered assets:

- Fine-tuned best checkpoint: `assets/models/trained-jester-tsm-r50/best_acc_top1_epoch_8.pth`
- Fine-tuned evaluation: Top-1 `96.29%`, Top-5 `99.80%`, mean class accuracy `95.89%`
- Official checkpoint: `assets/models/tsm_r50_1x1x8_50e_jester_rgb-c799267e.pth`
- Official config copy: `assets/models/tsm_r50_1x1x8_50e_jester_rgb.py`

If config/checkpoint are missing, `/api/model` and `/api/predict` report that the model is not configured.
