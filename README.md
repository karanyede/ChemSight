# ChemSight - Chemical Equipment Parameter Visualizer

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2+-green.svg)
![React](https://img.shields.io/badge/react-18+-61dafb.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)

**A hybrid analytics platform for chemical equipment monitoring and analysis**

[Live Demo](https://chemsight.vercel.app) • [Report Bug](https://github.com/karanyede/ChemSight/issues) • [Request Feature](https://github.com/karanyede/ChemSight/issues)

</div>

---

## 📋 Overview

ChemSight is a full-stack analytics platform designed for chemical equipment monitoring. It provides a unified REST API backend that powers both a modern web dashboard and a desktop application, enabling engineers to upload CSV equipment logs, analyze performance metrics, and generate comprehensive PDF reports.

### Key Features

✨ **Multi-Client Architecture**

- 🌐 Responsive React web dashboard with real-time charts
- 🖥️ PyQt5 desktop application for on-premise deployments
- 📱 Mobile-friendly interface with accessibility support

📊 **Data Analytics**

- CSV upload with automatic schema validation
- Real-time summary statistics (flowrate, pressure, temperature)
- Equipment type distribution analysis
- Interactive Chart.js visualizations
- Automatic dataset retention (keeps last 5 uploads per user)

🔐 **Security & Authentication**

- Token-based authentication (DRF TokenAuth)
- CORS-protected API endpoints
- Rate limiting and request throttling
- Secure session management

📄 **Reporting**

- Automated PDF report generation
- Downloadable analytics summaries
- Export functionality from both web and desktop clients

---

## 🚀 Tech Stack

### Backend

- **Framework:** Django 4.2+ with Django REST Framework
- **Database:** PostgreSQL (production) / SQLite (development)
- **API:** RESTful architecture with token authentication
- **Server:** Gunicorn with WhiteNoise for static files
- **Analytics:** Pandas for data processing, ReportLab for PDF generation

### Frontend (Web)

- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **UI:** Chart.js for data visualization
- **HTTP Client:** Axios with interceptors
- **Routing:** React Router v6

### Desktop Application

- **Framework:** PyQt5
- **Charts:** Matplotlib
- **Threading:** QThread for non-blocking operations
- **API Client:** Shared with web frontend

---

## 🏗️ Project Structure

```
ChemSight/
├── backend/                 # Django REST API
│   ├── api/                # Core API application
│   │   ├── models.py       # Database models
│   │   ├── serializers.py  # DRF serializers
│   │   ├── views.py        # API views
│   │   └── urls.py         # API routing
│   ├── config/             # Django settings
│   ├── uploads/            # CSV upload storage
│   └── reports/            # Generated PDF reports
│
├── web-frontend/           # React SPA
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Helper functions
│   └── public/             # Static assets
│
├── desktop-app/            # PyQt5 application
│   ├── main.py            # Application entry point
│   ├── api_client.py      # REST API client
│   └── ui/                # UI components
│
└── sample_data/           # Example CSV files
    └── sample_equipment_data.csv
```

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (for production) or SQLite (for development)
- Git

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/karanyede/ChemSight.git
cd ChemSight/backend

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
EOF

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
cd web-frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_BASE_URL=http://localhost:8000/api/" > .env.local

# Start development server
npm run dev

# Build for production
npm run build
```

### Desktop Application Setup

```bash
cd desktop-app

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

---

## 🌐 Deployment

### Production Deployment (Current Setup)

- **Frontend:** Deployed on [Vercel](https://chemsight.vercel.app)
- **Backend:** Deployed on [Railway](https://railway.app)
- **Database:** PostgreSQL on Railway

### Environment Variables

**Backend (Railway):**

```bash
DJANGO_SECRET_KEY=<your-secret-key>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}},localhost
DATABASE_URL=<auto-provided-by-railway>
CORS_ALLOWED_ORIGINS=https://chemsight.vercel.app
CSRF_TRUSTED_ORIGINS=https://chemsight.vercel.app,https://${{RAILWAY_PUBLIC_DOMAIN}}
```

**Frontend (Vercel):**

```bash
VITE_API_BASE_URL=https://chemsight-production.up.railway.app/api/
```

---

## 📊 Usage

### Web Dashboard

1. Navigate to [https://chemsight.vercel.app](https://chemsight.vercel.app)
2. Register a new account or login
3. Upload a CSV file (use `sample_data/sample_equipment_data.csv` for testing)
4. View analytics dashboard with charts and statistics
5. Download PDF reports for any dataset

### Desktop Application

1. Launch the application: `python desktop-app/main.py`
2. Configure API endpoint in settings (default: `http://localhost:8000/api/`)
3. Use the same credentials as the web interface
4. Upload files and generate reports offline

### API Endpoints

```
POST   /api/auth/register/           # User registration
POST   /api/auth/login/              # User login
GET    /api/datasets/                # List all datasets
POST   /api/upload/                  # Upload CSV file
GET    /api/datasets/{id}/           # Get dataset details
GET    /api/datasets/{id}/summary/   # Get analytics summary
GET    /api/datasets/{id}/records/   # Get dataset records
GET    /api/datasets/{id}/report/    # Download PDF report
GET    /api/metrics/                 # Get user metrics
GET    /api/healthz/                 # Health check
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd web-frontend
npm run test

# Run with coverage
npm run test:coverage
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Karan Yede**

- GitHub: [@karanyede](https://github.com/karanyede)
- Project Link: [https://github.com/karanyede/ChemSight](https://github.com/karanyede/ChemSight)

---

## 🙏 Acknowledgments

- Built as part of the FOSSEE Web Development Screening Task
- Inspired by modern full-stack application architectures
- Special thanks to the Django, React, and PyQt communities

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ by Karan Yede

</div>
