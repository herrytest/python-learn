from datetime import datetime

from pydantic import BaseModel


class ImageOut(BaseModel):
    id: int
    filename: str
    file_path: str
    ocr_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OCRResponse(BaseModel):
    image_id: int
    ocr_text: str
