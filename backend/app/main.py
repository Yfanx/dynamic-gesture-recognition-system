from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.inference.mmaction2_predictor import MMAction2Predictor
from app.labels import JESTER27_LABELS
from app.schemas import ModelStatus, PredictionResponse

settings = get_settings()
predictor = MMAction2Predictor(
    config_path=settings.resolve_path(settings.mmaction_config),
    checkpoint_path=settings.resolve_path(settings.mmaction_checkpoint),
    device=settings.mmaction_device,
)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/labels")
def labels() -> dict[str, list[str]]:
    return {"labels": JESTER27_LABELS}


@app.get("/api/model", response_model=ModelStatus)
def model_status() -> ModelStatus:
    return predictor.status()


@app.post("/api/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...), top_k: int = 5) -> PredictionResponse:
    suffix = Path(file.filename or "gesture.mp4").suffix or ".mp4"
    top_k = min(max(top_k, 1), 10)

    with NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp_path = Path(temp.name)
        temp.write(await file.read())

    try:
        predictions = predictor.predict(temp_path, top_k=top_k)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        temp_path.unlink(missing_ok=True)

    return PredictionResponse(
        filename=file.filename or temp_path.name,
        model=predictor.status(),
        predictions=predictions,
    )
