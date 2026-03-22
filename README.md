# QuantumPulse AI — Autonomous RF Spectrum Intelligence System

<div align="center">

**Real-time AI-powered RF spectrum simulation, analysis, prediction, and quantum-inspired optimization**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-000000?style=flat-square&logo=threedotjs&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

</div>

---

## Overview

QuantumPulse AI is a production-grade, microservices-based system that:

1. **Simulates** multi-signal RF spectrum environments with configurable noise, interference, and modulation (AM/FM/CW)
2. **Analyzes** signals using FFT, Welch PSD, spectrogram, and statistical feature extraction
3. **Predicts** spectrum congestion using LSTM with attention and Transformer neural networks
4. **Optimizes** frequency allocation using quantum-inspired simulated annealing with tunneling transitions
5. **Visualizes** everything in real-time via a React dashboard with 3D wave animations (Three.js), live charts, and WebSocket streaming

---

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  RF Sim     │───▶│ Signal Processing│───▶│  AI Prediction  │───▶│  Optimization   │
│  Service    │    │  Service         │    │  (LSTM/Trans.)  │    │  Engine         │
└─────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
       │                    │                       │                       │
       └────────────────────┴───────────────────────┴───────────────────────┘
                                        │
                              ┌─────────┴─────────┐
                              │   FastAPI Gateway  │
                              │  REST + WebSocket  │
                              └─────────┬─────────┘
                                        │
                         ┌──────────────┼──────────────┐
                         │              │              │
                    ┌────┴────┐   ┌─────┴─────┐  ┌────┴────┐
                    │ React   │   │ PostgreSQL│  │  Redis  │
                    │ Frontend│   │           │  │  Cache  │
                    └─────────┘   └───────────┘  └─────────┘
```

### Data Flow Pipeline

```
RF Simulation → Signal Processing → AI Prediction → Optimization → API → WebSocket → Frontend
```

---

## Project Structure

```
├── backend/
│   ├── config/              # Application settings
│   ├── database/            # DB session, Redis cache
│   ├── models/              # SQLAlchemy models + Pydantic schemas
│   ├── routes/              # API endpoints + WebSocket streaming
│   ├── services/            # Core business logic
│   │   ├── rf_simulation.py        # Multi-signal RF generation
│   │   ├── signal_processing.py    # FFT, PSD, feature extraction
│   │   ├── ai_prediction.py        # LSTM/Transformer models
│   │   └── optimization_engine.py  # Quantum-inspired optimizer
│   ├── utils/               # Helpers
│   ├── main.py              # FastAPI app entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React UI components
│   │   │   ├── WaveScene.jsx        # Three.js 3D wave visualization
│   │   │   ├── SpectrumChart.jsx    # Time-domain waveform
│   │   │   ├── FFTChart.jsx         # Frequency spectrum
│   │   │   ├── HeatmapPanel.jsx     # Band occupancy heatmap
│   │   │   ├── PredictionPanel.jsx  # AI prediction display
│   │   │   └── OptimizationPanel.jsx# Before/After comparison
│   │   ├── hooks/           # WebSocket hook
│   │   ├── services/        # API client
│   │   └── App.jsx          # Main app
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

---

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/Shivansh-00/QuantumPulse-AI-Autonomous-RF-Spectrum-Intelligence-System.git
cd QuantumPulse-AI-Autonomous-RF-Spectrum-Intelligence-System

# Start all services
docker compose up --build

# Access:
#   Frontend:  http://localhost:3000
#   Backend:   http://localhost:8000
#   API Docs:  http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Copy and edit environment config
copy .env.example .env

# Start backend (needs PostgreSQL & Redis running locally)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

> **Note:** For local dev without PostgreSQL/Redis, the backend will still start — database operations will fail gracefully but the simulation pipeline works via the REST API.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/rf/simulate` | Run RF simulation with custom parameters |
| `GET` | `/api/rf/quick-sim` | Quick simulation with defaults |
| `POST` | `/api/rf/analyze` | Analyze signal (FFT, PSD, features) |
| `POST` | `/api/predict/congestion` | Predict congestion levels |
| `POST` | `/api/predict/train` | Train AI model on synthetic data |
| `POST` | `/api/optimize/frequency` | Run quantum-inspired optimization |
| `WS` | `/ws/stream` | Real-time pipeline streaming |

Full interactive docs at **`/docs`** (Swagger UI).

---

## Key Technologies

### RF Simulation
- Multi-signal generation with AM/FM/CW modulation
- AWGN noise + random interference bursts
- Configurable: frequency, amplitude, bandwidth, noise level

### Signal Processing
- FFT-based spectrum analysis
- Welch power spectral density
- Spectrogram (time-frequency)
- Peak detection, band occupancy, statistical features

### AI Prediction (PyTorch)
- **LSTM with Attention** — sequence modeling with learnable focus
- **Transformer Encoder** — multi-head self-attention for temporal patterns
- Congestion risk classification (LOW / MEDIUM / HIGH)
- Synthetic training data generation for bootstrapping

### Quantum-Inspired Optimization
- **Simulated annealing** with Metropolis criterion
- **Quantum tunneling** — probabilistic large jumps to escape local minima
- **Superposition initialization** — parallel state evaluation for best start
- Objective: minimize interference, maximize signal clarity

### Frontend
- React 18 + Vite
- Three.js / React Three Fiber — animated 3D wave field
- Recharts — waveforms, FFT, predictions, scatter plots
- Tailwind CSS — glassmorphism dark theme
- WebSocket — live streaming pipeline updates

---

## Database Schema

### `signal_logs`
Stores RF simulation runs with configuration and summary data.

### `prediction_logs`
Stores AI prediction results with congestion levels and risk classification.

### `optimization_logs`
Stores optimization results with before/after allocations and improvement metrics.

---

## Deployment

### Backend → Render / AWS
- Use the `backend/Dockerfile`
- Set environment variables for `DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS`

### Frontend → Vercel
```bash
cd frontend
npm run build
# Deploy the dist/ folder to Vercel
```

### CI/CD
GitHub Actions workflow runs on every push to `main`:
- Python lint (ruff) + tests
- Node.js build verification
- Docker compose build validation

---

## License

MIT
