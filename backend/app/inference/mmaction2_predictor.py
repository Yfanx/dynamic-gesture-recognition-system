from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
import sys
from typing import Any

import numpy as np

from app.labels import JESTER27_LABELS
from app.schemas import ModelStatus, PredictionItem


@dataclass
class MMAction2Predictor:
    config_path: Path
    checkpoint_path: Path
    device: str = "cpu"

    _model: Any | None = None
    _load_error: str | None = None

    def status(self) -> ModelStatus:
        self._ensure_vendor_path()
        if not self.config_path.exists() or not self.checkpoint_path.exists():
            return ModelStatus(
                ready=False,
                engine="MMAction2 official API",
                config_path=str(self.config_path),
                checkpoint_path=str(self.checkpoint_path),
                device=self.device,
                message="模型配置或权重文件缺失，请检查 assets/models 和 backend/.env。",
            )

        if find_spec("mmaction") is None:
            return ModelStatus(
                ready=False,
                engine="MMAction2 official API",
                config_path=str(self.config_path),
                checkpoint_path=str(self.checkpoint_path),
                device=self.device,
                message="当前 Python 环境未安装 MMAction2，模型文件已恢复，但暂不能执行真实推理。",
            )

        if self._load_error:
            return ModelStatus(
                ready=False,
                engine="MMAction2 official API",
                config_path=str(self.config_path),
                checkpoint_path=str(self.checkpoint_path),
                device=self.device,
                message=self._load_error,
            )

        if self._model is None:
            return ModelStatus(
                ready=True,
                engine="MMAction2 official API",
                config_path=str(self.config_path),
                checkpoint_path=str(self.checkpoint_path),
                device=self.device,
                message="模型文件与 MMAction2 环境已就绪，首次识别时加载模型。",
            )

        return ModelStatus(
            ready=True,
            engine="MMAction2 official API",
            config_path=str(self.config_path),
            checkpoint_path=str(self.checkpoint_path),
            device=self.device,
            message="MMAction2 模型已加载。",
        )

    def predict(self, video_path: Path, top_k: int = 5) -> list[PredictionItem]:
        self._ensure_vendor_path()
        self._ensure_model()
        if self._model is None:
            raise RuntimeError(self.status().message)

        from mmaction.apis import inference_recognizer

        result = inference_recognizer(self._model, str(video_path))
        scores = self._extract_scores(result)
        order = np.argsort(scores)[::-1][:top_k]
        return [
            PredictionItem(label=self._label_for(int(index)), score=float(scores[index]))
            for index in order
        ]

    def _ensure_model(self) -> None:
        self._ensure_vendor_path()
        if self._model is not None or self._load_error is not None:
            return

        if not self.config_path.exists() or not self.checkpoint_path.exists():
            return

        try:
            import torch
            from mmaction.apis import init_recognizer

            original_load = torch.load

            def trusted_load(*args: Any, **kwargs: Any) -> Any:
                kwargs.setdefault("weights_only", False)
                return original_load(*args, **kwargs)

            try:
                torch.load = trusted_load
                self._model = init_recognizer(
                    str(self.config_path),
                    str(self.checkpoint_path),
                    device=self.device,
                )
            finally:
                torch.load = original_load
        except Exception as exc:  # pragma: no cover - depends on local MMAction2 install
            self._load_error = f"MMAction2 模型加载失败：{exc}"

    def _extract_scores(self, result: Any) -> np.ndarray:
        pred_score = getattr(getattr(result, "pred_score", None), "cpu", lambda: None)()
        if pred_score is not None:
            return pred_score.numpy()

        if hasattr(result, "pred_score"):
            value = result.pred_score
            if hasattr(value, "detach"):
                return value.detach().cpu().numpy()
            return np.asarray(value, dtype=float)

        if isinstance(result, tuple) and len(result) >= 2:
            return np.asarray(result[1], dtype=float)

        if isinstance(result, list):
            scores = np.zeros(len(JESTER27_LABELS), dtype=float)
            for index, score in result:
                scores[int(index)] = float(score)
            return scores

        raise RuntimeError(f"Unsupported MMAction2 inference result type: {type(result)!r}")

    def _label_for(self, index: int) -> str:
        if 0 <= index < len(JESTER27_LABELS):
            return JESTER27_LABELS[index]
        return f"Class {index}"

    def _ensure_vendor_path(self) -> None:
        project_root = self.config_path.parents[3]
        vendor_path = project_root / "third_party" / "mmaction2"
        if vendor_path.exists():
            vendor = str(vendor_path)
            if vendor not in sys.path:
                sys.path.insert(0, vendor)
