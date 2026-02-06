# Python Authentication + OCR Image Gallery (MySQL + API)

This project gives you a complete Python starter app with:

- User registration and login (JWT authentication)
- Image upload API
- Drag-and-drop gallery reordering API
- OCR API (read text from selected image)
- MySQL database integration with SQLAlchemy
- Simple web UI to test auth, upload, reorder, and OCR
- Git worktree helper script

## Stack

- FastAPI
- SQLAlchemy + PyMySQL
- MySQL
- JWT (`python-jose`)
- Password hashing (`passlib`)
- OCR (`pytesseract` + Pillow)

## 1) Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update `.env` for your MySQL credentials.

## 2) Create Database

```sql
CREATE DATABASE gallery_db;
```

## 3) Run

```bash
uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000

## API Endpoints

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`

### Images

- `GET /api/images` - list user images
- `POST /api/images` - upload image
- `POST /api/images/{image_id}/ocr` - extract text from image
- `PUT /api/images/reorder` - reorder by `image_ids`
- `DELETE /api/images/{image_id}` - remove image

## OCR Notes

Install Tesseract engine in your OS:

- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- macOS (brew): `brew install tesseract`

## Git Worktree

Create a new worktree with branch:

```bash
./scripts/create_worktree.sh feature/new-api ../python-learn-new-api
```

Manual equivalent:

```bash
git worktree add -b feature/new-api ../python-learn-new-api
```

## Suggested Next Improvements

- Refresh tokens
- Role-based access
- Image thumbnails
- Async task queue for OCR (Celery/RQ)
- Alembic migrations
- S3 storage support
