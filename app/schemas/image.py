from pydantic import BaseModel


class ImageResponse(BaseModel):
    id: int
    filename: str
    original_name: str
    order_index: int
    ocr_text: str

    class Config:
        from_attributes = True


class ReorderRequest(BaseModel):
    image_ids: list[int]
