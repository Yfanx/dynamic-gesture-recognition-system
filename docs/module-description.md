# 模块说明

## 目标

本项目用于毕业答辩演示动态手势识别：前端上传手势视频，后端调用官方 MMAction2 视频识别模型，返回 Jester27 手势类别 Top-K 结果。

## 前端 `frontend/`

- `src/App.vue`：主页面，包含视频上传、视频预览、模型状态、识别结果展示。
- `src/style.css`：界面样式，适合答辩时直接演示。
- `vite.config.js`：开发服务器配置，并把 `/api` 代理到 FastAPI 后端。

## 后端 `backend/`

- `app/main.py`：FastAPI 入口，提供健康检查、标签列表、模型状态、视频识别接口。
- `app/inference/mmaction2_predictor.py`：MMAction2 官方推理适配器，优先使用 `init_recognizer` 和 `inference_recognizer`。
- `app/labels.py`：Jester27 的 27 个类别标签。
- `app/config.py`：读取 `.env` 配置，解析模型 config/checkpoint 路径。

## 模型资产 `assets/models/`

放置官方模型配置和权重，例如：

- `tsm_r50_1x1x8_50e_jester_rgb.py`
- `tsm_r50_1x1x8_50e_jester_rgb.pth`

答辩前需要确认 `backend/.env` 指向真实存在的官方 config 和 checkpoint。

## 演示流程

1. 启动后端：`python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
2. 启动前端：`npm run dev`
3. 打开前端页面，确认右上角显示“官方模型已配置”。
4. 上传手势视频，展示 Top-5 识别结果。
