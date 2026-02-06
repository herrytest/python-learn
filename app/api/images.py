from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.database import get_db
from app.models.image import Image
from app.models.user import User
from app.schemas.image import ImageOut, OCRResponse
from app.services.ocr_service import extract_text_from_image

router = APIRouter(prefix="/api/images", tags=["images"])
settings = get_settings()
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=ImageOut, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Image:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    ext = Path(file.filename or "image").suffix
    unique_name = f"{uuid4().hex}{ext}"
    destination = Path(settings.upload_dir) / unique_name

    content = await file.read()
    destination.write_bytes(content)

    image = Image(filename=file.filename or unique_name, file_path=str(destination), owner_id=current_user.id)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@router.get("/", response_model=list[ImageOut])
def list_images(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Image]:
    return db.query(Image).filter(Image.owner_id == current_user.id).order_by(Image.id.desc()).all()


@router.post("/{image_id}/ocr", response_model=OCRResponse)
def run_ocr(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OCRResponse:
    image = db.query(Image).filter(Image.id == image_id, Image.owner_id == current_user.id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    text = extract_text_from_image(image.file_path)
    image.ocr_text = text
    db.commit()

    return OCRResponse(image_id=image.id, ocr_text=text)
