# IDM Latent Space - Modern Web GUI

> **Comprehensive web-based interface for analyzing and generating high-dimensional latent spaces in electronic music production**

![React](https://img.shields.io/badge/Frontend-React%2018-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![TypeScript](https://img.shields.io/badge/Language-TypeScript-blue)
![Material-UI](https://img.shields.io/badge/UI-Material--UI-purple)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-orange)

## 🎯 Overview

This modern web-based GUI replaces the previous PySide6 desktop interface with a comprehensive, scalable platform featuring:

- **Real-time Dashboard** with live metrics and visualizations
- **Dataset Management** with drag-and-drop upload and preprocessing
- **ML Model Training** with interactive parameter tuning
- **Latent Space Exploration** with 3D visualizations
- **Real-time Analysis** with WebSocket connections
- **Responsive Design** optimized for desktop and tablet

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
app/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── config.py          # Configuration management
│   ├── database.py        # Database setup and connections
│   └── logging.py         # Structured logging configuration
├── api/
│   └── endpoints/         # API route handlers
│       ├── datasets.py    # Dataset management endpoints
│       ├── models.py      # ML model endpoints
│       ├── analysis.py    # Real-time analysis endpoints
│       ├── auth.py        # Authentication endpoints
│       └── metrics.py     # System metrics endpoints
├── models/                # Database models (SQLAlchemy)
├── services/              # Business logic services
└── utils/                 # Utility functions
```

### Frontend (React + TypeScript)
```
frontend/src/
├── App.tsx                # Main application component
├── pages/                 # Page components
│   ├── Dashboard.tsx      # Main dashboard
│   ├── Datasets.tsx       # Dataset management
│   ├── Models.tsx         # Model training and evaluation
│   ├── Analysis.tsx       # Real-time analysis
│   └── Settings.tsx       # Configuration settings
├── components/            # Reusable components
│   ├── layout/           # Navigation and layout
│   ├── dashboard/        # Dashboard widgets
│   ├── visualizations/   # Charts and graphs
│   └── forms/            # Form components
└── store/                # Redux state management
    └── slices/           # Redux slices for different domains
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **PostgreSQL 12+** (or SQLite for development)
- **Redis 6+** (optional, for caching and background tasks)

### Installation

1. **Clone and setup environment:**
```bash
git clone https://github.com/shepherdvovkes/idmlatentspace.git
cd idmlatentspace

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

2. **Quick start with the automated script:**
```bash
./start.sh
```

This script will:
- Check dependencies
- Install Python packages in virtual environment
- Install Node.js packages
- Create necessary directories
- Start backend server on port 8000
- Start frontend development server on port 3000
- Start background workers (if configured)

3. **Manual setup (alternative):**

**Backend:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Access the Application

- **Frontend Interface:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Interactive API Explorer:** http://localhost:8000/redoc

## 💡 Key Features

### 🎛️ Dashboard
- **Real-time Metrics:** System performance, dataset statistics, model accuracy
- **Quick Actions:** Upload datasets, train models, analyze presets
- **Activity Feed:** Recent operations and system events
- **Latent Space Visualization:** Interactive 3D exploration

### 📊 Dataset Management
- **Drag-and-Drop Upload:** Support for SysEx, JSON, CSV, MIDI files
- **Real-time Validation:** Instant feedback on file format and quality
- **Preprocessing Pipeline:** Normalization, feature selection, dimensionality reduction
- **Progress Tracking:** Live updates on processing status

### 🧠 Machine Learning
- **Interactive Training:** Configure algorithms and hyperparameters
- **Real-time Monitoring:** Training progress, loss curves, validation metrics
- **Model Comparison:** Side-by-side performance analysis
- **Export/Import:** Save and load trained models

### 🔬 Analysis
- **Real-time Processing:** Instant preset analysis via WebSocket
- **Similarity Search:** Find similar presets in latent space
- **Genre Classification:** Automatic style detection
- **Parameter Importance:** Understand which controls matter most

### 📱 Responsive Design
- **Desktop Optimized:** Full-featured interface for researchers
- **Tablet Friendly:** Touch-optimized controls for producers
- **Dark Theme:** Electronic music aesthetic with cyan/orange accents

## 🎨 UI/UX Design

### Color Scheme
- **Primary:** #00D4FF (Cyan) - Digital/Electronic theme
- **Secondary:** #FF6B00 (Orange) - Energy/Creativity
- **Background:** #0A0A0A (Deep Black) with #1A1A1A panels
- **Text:** #FFFFFF primary, #B0B0B0 secondary

### Typography
- **Primary Font:** Inter (clean, modern)
- **Monospace:** JetBrains Mono (code and data)

### Components
- **Cards:** Rounded corners with subtle borders
- **Buttons:** Flat design with gradient accents
- **Charts:** Dark theme with colored highlights
- **Tables:** Striped rows with hover effects

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/idm_latent_space

# API Settings
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# File Storage
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_DIR=uploads

# ML Settings
MAX_WORKERS=4
BATCH_SIZE=1000
```

### Frontend Configuration

Key settings in `frontend/src/config.ts`:
- API base URL
- WebSocket endpoint
- Chart themes
- Upload limits

## 📈 Performance

### Optimization Features
- **Code Splitting:** Lazy-loaded pages and components
- **Memoization:** React.memo and useMemo for expensive operations
- **Virtual Scrolling:** Handle large datasets efficiently
- **WebSocket:** Real-time updates without polling
- **Caching:** Redis for frequent API responses

### Monitoring
- **Prometheus Metrics:** Request counts, duration, system resources
- **Structured Logging:** JSON logs with correlation IDs
- **Error Tracking:** Comprehensive error boundaries and reporting

## 🧪 Testing

### Backend Tests
```bash
# Run Python tests
source venv/bin/activate
pytest --cov=app --cov-report=html

# Run with coverage
pytest --cov=app --cov-fail-under=85
```

### Frontend Tests
```bash
# Run React tests
cd frontend
npm test

# Run with coverage
npm test -- --coverage --watchAll=false
```

### Integration Tests
```bash
# End-to-end tests with full stack
npm run test:e2e
```

## 🚀 Deployment

### Development
```bash
./start.sh
```

### Production with Docker
```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
# Apply configurations
kubectl apply -f kubernetes/

# Check status
kubectl get pods -l app=idm-latent-space
```

## 🛠️ Development

### Adding New Features

1. **Backend Endpoint:**
```python
# app/api/endpoints/new_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/new-endpoint")
async def new_endpoint():
    return {"message": "Hello from new feature"}
```

2. **Frontend Component:**
```typescript
// frontend/src/components/NewComponent.tsx
import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

const NewComponent: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">New Feature</Typography>
      </CardContent>
    </Card>
  );
};

export default NewComponent;
```

3. **Redux State:**
```typescript
// frontend/src/store/slices/newFeatureSlice.ts
import { createSlice } from '@reduxjs/toolkit';

const newFeatureSlice = createSlice({
  name: 'newFeature',
  initialState: { data: [] },
  reducers: {
    setData: (state, action) => {
      state.data = action.payload;
    },
  },
});

export default newFeatureSlice.reducer;
```

### Code Style

- **Python:** Black formatting, flake8 linting, mypy type checking
- **TypeScript:** ESLint with TypeScript rules, Prettier formatting
- **Imports:** Absolute imports, organized by type (React, libraries, local)

## 🔐 Security

### Authentication
- JWT tokens with refresh mechanism
- Role-based access control (Admin, Researcher, Producer, Viewer)
- API key authentication for programmatic access

### Data Protection
- Input validation and sanitization
- Rate limiting on all endpoints
- HTTPS enforcement in production
- Secure file upload with virus scanning

## 📚 API Documentation

### Key Endpoints

#### Dataset Management
- `POST /api/v1/datasets` - Upload new dataset
- `GET /api/v1/datasets` - List all datasets
- `POST /api/v1/datasets/{id}/preprocess` - Start preprocessing

#### Model Training
- `POST /api/v1/models/train` - Start training job
- `GET /api/v1/models/{id}` - Get model details
- `POST /api/v1/models/{id}/evaluate` - Evaluate model

#### Real-time Analysis
- `WebSocket /ws/analysis` - Real-time preset analysis
- `POST /api/v1/analysis/preset` - Single preset analysis

Full API documentation available at `/docs` when server is running.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes following code style guidelines
4. Add tests for new functionality
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Create Pull Request

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🆘 Support

- **GitHub Issues:** Report bugs and request features
- **Documentation:** Comprehensive guides in `/docs`
- **Discord:** Real-time community support
- **Email:** contact@idmlatentspace.com

## 🗺️ Roadmap

### Phase 1: Core Platform ✅
- [x] React frontend with Material-UI
- [x] FastAPI backend with PostgreSQL
- [x] Dataset upload and management
- [x] Real-time dashboard

### Phase 2: ML Integration 🚧
- [ ] Model training pipeline
- [ ] Real-time analysis WebSocket
- [ ] Latent space visualization
- [ ] Performance metrics

### Phase 3: Advanced Features 📋
- [ ] Collaborative experiments
- [ ] Model marketplace
- [ ] Plugin system
- [ ] Mobile app

### Phase 4: Research Tools 📋
- [ ] Academic paper generation
- [ ] Citation management
- [ ] Experiment reproducibility
- [ ] Data sharing protocols

---

**Built with ❤️ for the electronic music research community**