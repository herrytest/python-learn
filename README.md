# Image Gallery Auth API (FastAPI + MySQL + OCR)

This project includes:

- User registration and login (JWT authentication)
- Drag-and-drop image upload UI
- Image gallery per user
- OCR API to read text from selected images (using Tesseract)
- MySQL database integration

## Worktree / Project Tree

```text
app/
  api/          # API routes (auth + image)
  core/         # Settings and security helpers
  db/           # SQLAlchemy engine/session
  models/       # ORM models
  schemas/      # Pydantic schemas
  services/     # OCR service
  static/       # JS/CSS frontend
  templates/    # HTML template
tests/
```

## Quick Start

1. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

2. Configure environment:

```bash
cp .env.example .env
```

3. (Optional) If you want local quick testing without MySQL, set `DATABASE_URL=sqlite:///./local.db`.

4. Create MySQL database:

```sql
CREATE DATABASE image_gallery;
```

5. Run app:

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## API Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/images/upload` (auth required)
- `GET /api/images/` (auth required)
- `POST /api/images/{image_id}/ocr` (auth required)

## OCR Notes

Install Tesseract engine in your OS and set `TESSERACT_CMD` in `.env` if needed.
