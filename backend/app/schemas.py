from pydantic import BaseModel


class PredictionItem(BaseModel):
    label: str
    score: float


class ModelStatus(BaseModel):
    ready: bool
    engine: str
    config_path: str
    checkpoint_path: str
    device: str
    message: str


class PredictionResponse(BaseModel):
    filename: str
    model: ModelStatus
    predictions: list[PredictionItem]
