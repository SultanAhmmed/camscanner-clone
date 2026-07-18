# CamScanner Clone

A web-based document scanner that turns photos of documents into PDFs. Built with FastAPI, OpenCV, and Docker. Handles edge detection, perspective correction, and adaptive thresholding.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- Document edge detection via Canny edge detection and contour analysis
- Perspective correction (flattens angled photos using homography)
- Four processing modes:
  - **Scan** - black & white, adaptive thresholding, shadows removed
  - **Color** - original colors preserved
  - **Gray** - standard grayscale
  - **Enhanced** - high contrast via CLAHE
- Multi-page PDF export
- Drag-and-drop web UI with live previews
- Docker deployment
- Pytest suite with GitHub Actions CI

## Quick Start

### Docker

```bash
git clone https://github.com/SultanAhmmed/camscanner-clone.git
cd camscanner-clone

docker build -t camscanner-api .
docker run -d -p 8000:8000 --name camscanner camscanner-api
```
or
```bash
docker compose up --build
docker compose up
```

Open [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html).

### Local dev with uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/YOUR_GITHUB_USERNAME/camscanner-clone.git
cd camscanner-clone

uv sync
uv run uvicorn app.main:app --reload
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/scan-document` | POST | Process a single image |
| `/scan-to-pdf` | POST | Process multiple images into a PDF |

### Scan a single document

```bash
curl -X POST "http://localhost:8000/scan-document?mode=scan" \
  -F "file=@document.jpg" \
  --output scanned_result.jpg
```

### Create a multi-page PDF

```bash
curl -X POST "http://localhost:8000/scan-to-pdf?mode=scan" \
  -F "files=@page1.jpg" \
  -F "files=@page2.jpg" \
  --output final_document.pdf
```

## Project Structure

```text
camscanner-clone/
├── app/                          # FastAPI application
│   ├── __init__.py
│   └── main.py                   # Routes, static file mounting
├── src/                           # Core CV logic
│   ├── __init__.py
│   ├── order_points.py           # Corner ordering
│   ├── four_point_transform.py   # Perspective warp
│   └── process_document.py       # Main processing pipeline
├── static/                        # Frontend assets
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/
│   ├── test_api.py
│   └── test_processing.py
├── .github/workflows/             # CI
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Testing

```bash
uv run pytest tests/ -v

uv run pytest tests/ --cov=src --cov=app
```

## Tech Stack

- **Backend:** FastAPI, Uvicorn
- **Image processing:** OpenCV, NumPy
- **PDF generation:** img2pdf
- **Package management:** uv
- **Containerization:** Docker
- **Testing:** pytest, httpx
- **CI/CD:** GitHub Actions

## Contributing

Pull requests welcome. For larger changes, open an issue first.

## License

MIT - see [LICENSE](LICENSE).
