# AI-Based Sperm Detection and Male Infertility Analysis System

Production-oriented research scaffold for detecting sperm cells in microscope images or videos, estimating concentration, tracking motility, screening morphology, and generating male fertility decision-support reports.

This project is **research and clinical decision-support software only**. It is not a final medical diagnosis, not a replacement for qualified clinicians, and not a validated laboratory CASA system without dataset-specific training, calibration, regulatory review, and clinical validation.

## What It Builds

- FastAPI backend for uploads, analysis records, and report retrieval.
- OpenCV baseline detector plus YOLO/segmentation adapter for trained sperm models.
- Cell counting and concentration estimation using microscope calibration and chamber depth.
- Nearest-neighbor tracking for motility, velocity, movement path, and abnormal motion flags.
- Morphology screening from detected cell shape features.
- Next.js dashboard for doctors, embryologists, and researchers.
- SQLite by default, PostgreSQL-compatible via `DATABASE_URL`.
- Docker Compose, tests, CI workflow, and GitHub-ready layout.

## Project Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- api/routes/          # FastAPI endpoints
|   |   |-- core/                # config and security
|   |   |-- db/                  # SQLAlchemy models/session
|   |   |-- ml/                  # detection, tracking, metrics, reporting
|   |   `-- services/            # storage and serialization helpers
|   |-- tests/
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- requirements-ml.txt
|-- frontend/
|   |-- app/                     # Next.js app router pages
|   |-- components/              # dashboard components
|   |-- lib/                     # API client types/helpers
|   |-- scripts/                 # Next build compatibility wrapper
|   `-- Dockerfile
|-- docker-compose.yml
|-- .env.example
`-- .github/workflows/ci.yml
```

## Quick Start

1. Create a local environment file:

```bash
cp .env.example .env
```

2. Start the stack:

```bash
docker compose up --build
```

3. Open the dashboard:

```text
http://localhost:3000
```

The backend API runs at:

```text
http://localhost:8000
```

## Local Backend Development

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Install the optional YOLO/PyTorch stack when trained weights are available:

```bash
pip install -r requirements-ml.txt
```

Health check:

```bash
curl http://localhost:8000/health
```

Run tests:

```bash
cd backend
pytest
```

## Local Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## API Usage

Upload an image or video:

```bash
curl -X POST http://localhost:8000/api/v1/analyses/uploads \
  -F "file=@sample.mp4" \
  -F "patient_code=SAMPLE-001" \
  -F "sample_metadata={\"microns_per_pixel\":0.33,\"chamber_depth_microns\":20,\"max_frames\":300}"
```

List analyses:

```bash
curl http://localhost:8000/api/v1/analyses
```

Fetch one report:

```bash
curl http://localhost:8000/api/v1/analyses/{analysis_id}/report
```

If `API_KEY` is set in `.env`, send it as:

```bash
X-API-Key: your-key
```

## AI/ML Pipeline

The default detector is a deterministic OpenCV baseline:

1. Grayscale conversion and contrast enhancement.
2. Otsu and adaptive threshold fusion.
3. Morphological cleanup.
4. Contour filtering by area, circularity, and aspect ratio.
5. Centroid and bounding-box extraction.

For production research, train a sperm-specific YOLO or segmentation model and set:

```env
YOLO_WEIGHTS_PATH=/app/models/sperm-yolo.pt
```

The YOLO adapter will load Ultralytics weights and use model predictions instead of the OpenCV baseline.

## Scientific Assumptions

- Concentration estimation requires microscope calibration and chamber depth.
- Motility requires video with reliable FPS.
- Velocity is reported in microns/second when calibration exists.
- Morphology screening is shape-feature based and not equivalent to strict manual morphology without validated staining, optics, and trained review.
- Screening thresholds are configurable research defaults and must be aligned with local lab protocols.

## Security and Medical Data Handling

- Use coded sample IDs only; do not upload names or direct identifiers.
- Configure `API_KEY` or replace it with OIDC/OAuth before deployment.
- Encrypt uploaded media and database volumes at rest in production.
- Serve only over HTTPS outside local development.
- Restrict access by role and audit report access.
- Apply retention policies for images, videos, and derived reports.
- Validate consent, IRB/ethics requirements, and local medical data regulations before clinical use.

## Scaling Path

- Replace synchronous analysis with a queue worker such as Celery, Dramatiq, or Arq.
- Store media in S3-compatible encrypted object storage.
- Move from SQLite to PostgreSQL with managed backups.
- Add model registry, dataset versioning, and model card metadata.
- Add per-frame overlays and exported annotated videos.
- Add role-based access control and audit logging.
- Add calibration profiles per microscope and counting chamber.
- Add DICOM/lab system integrations if required by the institution.

## Future Research Roadmap

- Train YOLOv8/YOLOv11 or Mask R-CNN/segmentation models on annotated sperm microscopy datasets.
- Compare detector performance against CASA reference systems.
- Add optical-flow-assisted tracking for dense scenes.
- Estimate VAP, ALH, BCF, STR, LIN, and WOB with CASA-style definitions.
- Classify morphology subtypes: tapered head, amorphous head, double head, bent neck, coiled tail, short tail.
- Add uncertainty estimation and quality-control rejection for poor focus, bubbles, debris, and low contrast.
- Evaluate domain adaptation across microscopes, stains, chambers, and camera frame rates.
- Add federated learning support so clinics can improve models without centralizing protected media.
<<<<<<< HEAD
your content
=======
github content
>>>>>>> branch
