# 🧬 AI-Based Sperm Detection & Male Infertility Analysis System

> **AI-powered research and clinical decision-support platform for sperm detection, concentration estimation, motility tracking, morphology screening, and male fertility analysis from microscopy images and videos.**

**Research / Clinical Decision-Support Notice:**
This project is intended for research and clinical decision-support workflows only. It is **not a final medical diagnosis**, does not replace qualified clinicians or laboratory experts, and should not be considered a validated CASA system without appropriate dataset-specific training, calibration, clinical validation, and regulatory review.

---

## 🚀 Overview

The **AI-Based Sperm Detection and Male Infertility Analysis System** is a production-oriented research scaffold designed to analyze sperm microscopy images and videos using computer vision, deep learning, and quantitative image analysis.

The platform combines:

* 🔬 Computer vision-based sperm detection
* 🤖 YOLO/segmentation model integration
* 🔢 Sperm cell counting
* 📊 Concentration estimation
* 🎥 Video-based motility analysis
* 📍 Sperm tracking
* 🏃 Velocity and movement-path estimation
* 🧬 Morphology screening
* 📑 Automated research reports
* 🖥️ Web-based clinical/research dashboard
* 🔐 API authentication and coded sample identifiers
* 🐳 Docker-based deployment
* 🧪 Automated testing and CI

The architecture is designed so that the initial deterministic OpenCV detector can later be replaced or supplemented by trained sperm-specific deep-learning models.

---

# ✨ Key Features

## 🔬 Sperm Detection

The baseline computer-vision pipeline performs:

1. Grayscale conversion
2. Contrast enhancement
3. Otsu thresholding
4. Adaptive thresholding
5. Threshold fusion
6. Morphological cleanup
7. Contour extraction
8. Area filtering
9. Circularity filtering
10. Aspect-ratio filtering
11. Centroid extraction
12. Bounding-box extraction

For research-grade deployment, trained YOLO or segmentation models can be integrated.

---

## 🤖 AI/ML Model Support

The system provides an adapter architecture for sperm-specific models.

Supported research direction:

* YOLO
* YOLO segmentation
* Mask R-CNN
* Custom PyTorch models
* Ultralytics models
* Future transformer-based vision models

Example configuration:

```env
YOLO_WEIGHTS_PATH=/app/models/sperm-yolo.pt
```

When configured, the YOLO adapter can replace the OpenCV baseline detector.

---

# 📊 Sperm Concentration Estimation

The system can estimate sperm concentration when appropriate microscope calibration information is available.

Required parameters may include:

* Microscope calibration
* Microns-per-pixel
* Chamber depth
* Detected sperm count
* Image/frame dimensions

Example metadata:

```json
{
  "microns_per_pixel": 0.33,
  "chamber_depth_microns": 20,
  "max_frames": 300
}
```

> Concentration estimates are research outputs and must be validated against the relevant laboratory counting protocol and equipment.

---

# 🎥 Motility & Tracking

For microscopy videos, the system can perform frame-by-frame tracking.

Current baseline approach:

```text
Detection
   ↓
Centroid Extraction
   ↓
Nearest-Neighbor Association
   ↓
Track Construction
   ↓
Movement Analysis
   ↓
Velocity Estimation
   ↓
Motility Metrics
```

Potential outputs include:

* Track ID
* Frame positions
* Movement distance
* Movement direction
* Velocity
* Movement path
* Abnormal movement flags

Reliable velocity estimation requires accurate:

* Video FPS
* Microscope calibration
* Pixel-to-distance conversion

---

# 🧬 Morphology Screening

The system includes shape-based morphology screening using detected cell features.

Potential features include:

* Area
* Perimeter
* Aspect ratio
* Circularity
* Bounding-box dimensions
* Head-shape characteristics
* Tail-related geometric features

Research morphology categories can include:

* Tapered head
* Amorphous head
* Double head
* Bent neck
* Coiled tail
* Short tail
* Other abnormal morphology patterns

> Shape-based screening is **not equivalent to validated manual morphology assessment**. Clinical morphology analysis requires appropriate staining, microscopy, laboratory protocols, and trained review.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │     Next.js Dashboard   │
                    │     Clinical / Research │
                    │          UI             │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      FastAPI Backend     │
                    │      REST API Layer      │
                    └────────────┬────────────┘
                                 │
             ┌───────────────────┼──────────────────┐
             │                   │                  │
             ▼                   ▼                  ▼
      ┌─────────────┐     ┌─────────────┐    ┌─────────────┐
      │ Detection   │     │ Tracking    │    │ Reporting   │
      │ Pipeline    │     │ Pipeline    │    │ Engine      │
      └──────┬──────┘     └──────┬──────┘    └──────┬──────┘
             │                   │                  │
             ▼                   ▼                  ▼
      OpenCV / YOLO       Motility Metrics     Analysis Report
      Segmentation        Velocity / Paths     Decision Support
             │
             ▼
      ┌─────────────────────────────────┐
      │       Database / Storage        │
      │ SQLite / PostgreSQL / Object    │
      │ Storage                         │
      └─────────────────────────────────┘
```

---

# 📁 Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/          # FastAPI endpoints
│   │   ├── core/                # Configuration and security
│   │   ├── db/                  # SQLAlchemy models/session
│   │   ├── ml/                  # Detection, tracking, metrics, reporting
│   │   └── services/            # Storage and serialization helpers
│   │
│   ├── tests/                   # Backend tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-ml.txt
│
├── frontend/
│   ├── app/                     # Next.js App Router
│   ├── components/              # Dashboard components
│   ├── lib/                     # API client, types, helpers
│   ├── scripts/                 # Build compatibility scripts
│   └── Dockerfile
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# ⚡ Quick Start

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <repository-folder>
```

---

## 2. Configure Environment

Create a local environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure required values inside `.env`.

---

# 🐳 Docker Deployment

Build and start the complete stack:

```bash
docker compose up --build
```

Frontend:

```text
http://localhost:3000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

Stop the stack:

```bash
docker compose down
```

---

# 🐍 Local Backend Development

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

# 🤖 Install Optional ML Dependencies

When trained YOLO/PyTorch weights are available:

```bash
pip install -r requirements-ml.txt
```

Configure the model:

```env
YOLO_WEIGHTS_PATH=/app/models/sperm-yolo.pt
```

---

# 🖥️ Local Frontend Development

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

---

# 🔌 API

## Upload Image or Video

Example:

```bash
curl -X POST http://localhost:8000/api/v1/analyses/uploads \
  -F "file=@sample.mp4" \
  -F "patient_code=SAMPLE-001" \
  -F "sample_metadata={\"microns_per_pixel\":0.33,\"chamber_depth_microns\":20,\"max_frames\":300}"
```

---

## List Analyses

```bash
curl http://localhost:8000/api/v1/analyses
```

---

## Retrieve Analysis Report

```bash
curl http://localhost:8000/api/v1/analyses/{analysis_id}/report
```

---

# 🔐 API Authentication

If `API_KEY` is configured in `.env`, include it with requests:

```http
X-API-Key: your-key
```

Example:

```bash
curl http://localhost:8000/api/v1/analyses \
  -H "X-API-Key: your-key"
```

For production deployment, replace the basic API-key approach with an appropriate identity and access-management system such as OIDC/OAuth.

---

# ⚙️ Configuration

Example environment configuration:

```env
DATABASE_URL=sqlite:///./app.db

API_KEY=change-me

YOLO_WEIGHTS_PATH=/app/models/sperm-yolo.pt

UPLOAD_DIR=./uploads

MAX_UPLOAD_SIZE_MB=500
```

SQLite is provided for development.

For production:

```env
DATABASE_URL=postgresql://user:password@postgres:5432/sperm_analysis
```

---

# 🧪 Testing

Run backend tests:

```bash
cd backend
pytest
```

Run with verbose output:

```bash
pytest -v
```

The repository is structured to support automated testing through CI.

---

# 🔬 Scientific Methodology

The system is designed around the following analytical workflow:

```text
Microscopy Image / Video
          │
          ▼
   Image Preprocessing
          │
          ▼
     Sperm Detection
          │
          ▼
    Cell Localization
          │
     ┌────┴─────┐
     ▼          ▼
 Counting     Tracking
     │          │
     ▼          ▼
Concentration Motility
     │          │
     └────┬─────┘
          ▼
    Morphology
      Screening
          │
          ▼
   Quality Control
          │
          ▼
  Research Report
```

---

# 📐 Scientific Assumptions

### Concentration

Concentration estimation requires:

* Microscope calibration
* Chamber depth
* Accurate sperm detection
* Appropriate counting protocol

### Motility

Motility analysis requires:

* Reliable video frames
* Known FPS
* Stable microscopy
* Appropriate tracking
* Pixel-to-distance calibration

### Velocity

When calibration is available:

```text
Velocity = Physical Distance / Time
```

Velocity can be reported in:

```text
µm/s
```

### Morphology

Morphology screening uses computational shape features and should not be interpreted as a validated clinical morphology diagnosis.

---

# 📊 Research Metrics

The platform is designed to support future calculation of CASA-style motility metrics, including:

* VAP — Average Path Velocity
* ALH — Amplitude of Lateral Head Displacement
* BCF — Beat Cross Frequency
* STR — Straightness
* LIN — Linearity
* WOB — Wobble

These metrics require validated tracking definitions and appropriate experimental calibration before clinical interpretation.

---

# 🛡️ Security & Medical Data Handling

For research or clinical environments:

* Use coded sample IDs instead of names.
* Avoid direct personal identifiers in uploaded files.
* Enable authentication.
* Use HTTPS outside local development.
* Encrypt media at rest.
* Encrypt database storage.
* Restrict report access by role.
* Maintain audit logs.
* Apply data-retention policies.
* Secure backups.
* Validate informed-consent requirements.
* Follow applicable institutional ethics/IRB requirements.
* Follow applicable medical-data and privacy regulations.

> Never upload identifiable patient information to an unsecured development environment.

---

# 🧠 Production Scaling Roadmap

The initial architecture can be extended toward production-scale research infrastructure.

### Compute

Replace synchronous analysis with:

* Celery
* Dramatiq
* Arq
* Background workers
* GPU inference workers

### Storage

Move uploaded media to:

* S3-compatible object storage
* Encrypted cloud storage
* Institutional research storage

### Database

Move from SQLite to:

* PostgreSQL
* Managed PostgreSQL
* High-availability database infrastructure

### ML Infrastructure

Add:

* Model registry
* Dataset versioning
* Experiment tracking
* Model cards
* Model version metadata
* Training pipelines
* GPU inference
* Model monitoring

---

# 🧪 Future Research Roadmap

## Phase 1 — Detection

* Train sperm-specific YOLO models
* Evaluate segmentation models
* Improve detection under low contrast
* Detect overlapping sperm
* Handle debris and bubbles

## Phase 2 — Tracking

* Improve multi-object tracking
* Optical-flow-assisted tracking
* Handle occlusion
* Improve dense-scene tracking
* Track long trajectories

## Phase 3 — Morphology

Develop classifiers for:

* Normal morphology
* Tapered heads
* Amorphous heads
* Double heads
* Bent necks
* Coiled tails
* Short tails

## Phase 4 — Quality Control

Automatically detect:

* Poor focus
* Bubbles
* Debris
* Low contrast
* Excessive motion blur
* Insufficient sperm count
* Poor illumination

## Phase 5 — Domain Adaptation

Evaluate performance across:

* Different microscopes
* Different cameras
* Different stains
* Different chambers
* Different magnifications
* Different frame rates
* Different laboratories

## Phase 6 — Clinical Research

Compare model outputs against:

* Expert annotations
* Laboratory measurements
* Reference CASA systems
* Independent validation datasets

---

# 🌐 Federated Learning Research

A future version could investigate federated learning so participating laboratories can collaboratively improve models without centrally collecting all protected microscopy media.

Potential architecture:

```text
             ┌──────────────────┐
             │ Central Training  │
             │ / Model Server    │
             └────────┬─────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ Clinic A│   │ Clinic B│   │ Clinic C│
   │ Dataset │   │ Dataset │   │ Dataset │
   └─────────┘   └─────────┘   └─────────┘
        │             │             │
        ▼             ▼             ▼
     Local         Local         Local
     Training      Training      Training
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                Model Updates
```

This is a research direction and requires careful privacy, security, and validation design.

---

# 📚 Research & Validation Requirements

Before any clinical deployment, the system should undergo appropriate validation covering:

### Dataset Quality

* Diverse microscopy datasets
* Expert annotations
* Multiple laboratories
* Multiple microscope systems
* Multiple acquisition conditions

### Model Evaluation

Measure:

* Precision
* Recall
* F1-score
* mAP
* Detection sensitivity
* Tracking accuracy
* Counting error
* Concentration estimation error
* Motility classification accuracy

### Clinical Validation

Compare against appropriate reference methods and qualified expert assessment.

Important validation dimensions include:

```text
Technical Validation
        ↓
Analytical Validation
        ↓
External Validation
        ↓
Clinical Validation
        ↓
Regulatory Review
```

---

# ⚠️ Limitations

This repository is a **research scaffold**, not a clinically validated diagnostic product.

Results can be affected by:

* Microscope quality
* Camera quality
* Magnification
* Illumination
* Focus
* Staining
* Sample preparation
* Chamber type
* Video FPS
* Dataset bias
* Detection-model performance
* Tracking errors
* Calibration errors
* Domain shift

Therefore, outputs must be interpreted within the appropriate laboratory and research context.

---

# 🗺️ Development Roadmap

* [x] FastAPI backend
* [x] Image/video upload workflow
* [x] OpenCV baseline detector
* [x] Analysis records
* [x] Database abstraction
* [x] Basic tracking architecture
* [x] Morphology feature extraction
* [x] Report generation architecture
* [x] Next.js dashboard
* [x] Docker Compose
* [x] Automated testing structure
* [x] CI workflow
* [ ] Trained sperm-specific YOLO model
* [ ] Segmentation model
* [ ] Advanced multi-object tracking
* [ ] CASA metric implementation
* [ ] Expert-annotated validation dataset
* [ ] Model registry
* [ ] GPU inference service
* [ ] Advanced quality-control system
* [ ] External validation
* [ ] Clinical research validation
* [ ] Federated learning research

---

# 💻 Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* OpenCV
* PyTorch
* Ultralytics
* Pydantic

### Frontend

* Next.js
* React
* TypeScript
* Modern responsive dashboard architecture

### Database

* SQLite
* PostgreSQL

### Infrastructure

* Docker
* Docker Compose
* GitHub Actions

### AI/ML

* Computer Vision
* Object Detection
* Image Segmentation
* Multi-Object Tracking
* Deep Learning
* Quantitative Microscopy

---

# 📄 License

Add the project's chosen license here, for example:

```text
MIT License
```

If this repository is intended for academic or clinical research, choose a license that is compatible with the project's datasets, model weights, dependencies, and institutional requirements.

---

# 👨‍🔬 Research Positioning

This project sits at the intersection of:

```text
Artificial Intelligence
        +
Computer Vision
        +
Biomedical Engineering
        +
Reproductive Medicine
        +
Medical Image Analysis
        +
Deep Learning
```

The long-term research objective is to develop a reproducible computational framework for quantitative sperm microscopy analysis while maintaining appropriate scientific validation, uncertainty estimation, privacy, and clinical safety.
