import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.image import ImageItem
from app.models.user import User
from app.schemas.image import ImageResponse, ReorderRequest
from app.services.ocr import extract_text

router = APIRouter(prefix="/api/images", tags=["images"])
settings = get_settings()


@router.get("", response_model=list[ImageResponse])
def list_images(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(ImageItem)
        .filter(ImageItem.owner_id == user.id)
        .order_by(ImageItem.order_index.asc())
        .all()
    )


@router.post("", response_model=ImageResponse)
def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    uploads_dir = Path(settings.uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename).suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = f"{uuid4().hex}{extension}"
    destination = uploads_dir / filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    next_order = (
        db.query(ImageItem)
        .filter(ImageItem.owner_id == user.id)
        .count()
    )
    image = ImageItem(
        filename=filename,
        original_name=file.filename,
        owner_id=user.id,
        order_index=next_order,
        ocr_text="",
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@router.post("/{image_id}/ocr", response_model=ImageResponse)
def run_ocr(
    image_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    image = (
        db.query(ImageItem)
        .filter(ImageItem.id == image_id, ImageItem.owner_id == user.id)
        .first()
    )
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image_path = Path(settings.uploads_dir) / image.filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image file missing")

    image.ocr_text = extract_text(image_path)
    db.commit()
    db.refresh(image)
    return image


@router.put("/reorder")
def reorder_images(
    payload: ReorderRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    images = (
        db.query(ImageItem)
        .filter(ImageItem.owner_id == user.id, ImageItem.id.in_(payload.image_ids))
        .all()
    )
    found_ids = {image.id for image in images}
    if found_ids != set(payload.image_ids):
        raise HTTPException(status_code=400, detail="Invalid image ids")

    id_to_image = {image.id: image for image in images}
    for index, image_id in enumerate(payload.image_ids):
        id_to_image[image_id].order_index = index

    db.commit()
    return {"message": "Gallery reordered"}


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    image = (
        db.query(ImageItem)
        .filter(ImageItem.id == image_id, ImageItem.owner_id == user.id)
        .first()
    )
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image_path = Path(settings.uploads_dir) / image.filename
    if image_path.exists():
        image_path.unlink()

    db.delete(image)
    db.commit()
    return {"message": "Image deleted"}
