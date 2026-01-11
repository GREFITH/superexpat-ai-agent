# SuperExpat AI Agent System 🌍

**AI-Powered Event & Job Discovery Platform with RAG Architecture**

![SuperExpat Banner](https://img.shields.io/badge/AI-Powered-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green) ![React](https://img.shields.io/badge/React-18-blue) ![Gemini](https://img.shields.io/badge/Gemini-AI-purple)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Screenshots](#screenshots)
- [License](#license)

---

## 🎯 Overview

SuperExpat AI Agent is an intelligent event and job discovery platform that uses **Retrieval Augmented Generation (RAG)** architecture powered by Google's Gemini AI. The system aggregates data from multiple sources (Eventbrite, SerpAPI) and provides AI-generated summaries to help users find relevant events and job opportunities worldwide.

### Key Highlights

- 🤖 **AI-Powered Search**: Gemini 1.5 Flash model generates contextual summaries
- 🔍 **Multi-Source Aggregation**: Combines Eventbrite + Google Events data
- 🧠 **RAG Architecture**: Uses vector embeddings for enhanced context
- 🌐 **Global Coverage**: Search events/jobs in major cities worldwide
- ⚡ **Real-time Processing**: Fast API responses with intelligent caching

---

## ✨ Features

### 🎉 Event Discovery
- Search concerts, festivals, conferences, meetups
- Filter by location (London, Berlin, Paris, NYC, etc.)
- View event details: date, time, venue, pricing
- Direct booking links

### 💼 Job Search
- Find career opportunities globally
- Company information and job descriptions
- Direct application links
- Location-based filtering

### 🤖 AI Intelligence
- **Context-Aware Summaries**: AI understands your search intent
- **Smart Recommendations**: Highlights best matches
- **Natural Language**: Ask in plain English
- **RAG Integration**: Uses knowledge base for better responses

### 🎨 User Experience
- Clean, modern interface
- Responsive design (mobile + desktop)
- Real-time search results
- Loading states and error handling

---

## 🏗️ Architecture

### System Design

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   FastAPI    │────────▶│  External   │
│   (React)   │         │   Backend    │         │    APIs     │
└─────────────┘         └──────────────┘         └─────────────┘
                               │                        │
                               ▼                        │
                        ┌──────────────┐               │
                        │  Gemini AI   │               │
                        │     RAG      │               │
                        └──────────────┘               │
                               │                        │
                               ▼                        ▼
                        ┌──────────────┐         ┌─────────────┐
                        │ Vector Store │         │ Eventbrite  │
                        │  (ChromaDB)  │         │  SerpAPI    │
                        └──────────────┘         └─────────────┘
```

### RAG Pipeline

1. **Query Processing**: Detect intent (event/job) and extract location
2. **Data Fetching**: Aggregate from Eventbrite + SerpAPI
3. **Vector Search**: Retrieve relevant context from knowledge base
4. **AI Generation**: Gemini AI creates personalized summary
5. **Response Formatting**: Structure data for frontend display

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.109
- **AI Model**: Google Gemini 1.5 Flash
- **Vector Store**: ChromaDB + Sentence Transformers
- **APIs**: Eventbrite API, SerpAPI
- **Language**: Python 3.11+

### Frontend
- **Framework**: React 18
- **Styling**: Custom CSS with gradients
- **Icons**: Lucide React
- **HTTP Client**: Fetch API

### Infrastructure
- **Backend Hosting**: Railway / Render
- **Frontend Hosting**: Vercel
- **Version Control**: Git + GitHub

---

## 📦 Installation

### Prerequisites

```bash
# Required
- Python 3.11+
- Node.js 18+
- Git

# API Keys (free tier available)
- Eventbrite API Key
- SerpAPI Key
- Google Gemini API Key
```

### Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/superexpat-ai-agent.git
cd superexpat-ai-agent/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your API keys:
# EVENTBRITE_API_KEY=your_key_here
# SERPAPI_KEY=your_key_here
# GEMINI_API_KEY=your_key_here

# 5. Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

### Frontend Setup

```bash
# 1. Navigate to frontend
cd ../frontend

# 2. Install dependencies
npm install

# 3. Configure API URL (optional for local dev)
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# 4. Start development server
npm start
```

Frontend will open at: `http://localhost:3000`

---

## 📖 API Documentation

### Base URL
```
Local: http://localhost:8000
Production: https://your-app.up.railway.app
```

### Endpoints

#### 1. Chat Endpoint
**POST** `/api/chat`

Search for events or jobs with AI-powered responses.

**Request:**
```json
{
  "message": "concerts in London",
  "page": 1,
  "page_size": 20
}
```

**Response:**
```json
{
  "intent": "event",
  "query": "concerts in London",
  "location": "London",
  "total_results": 15,
  "ai_summary": "🎵 London's music scene is thriving! I found 15 amazing concerts including performances at the O2 Arena and Royal Albert Hall...",
  "results": [
    {
      "id": "eb_123456",
      "type": "event",
      "title": "Coldplay Live 2026",
      "poster": "https://...",
      "start_date": "2026-03-15",
      "start_time": "19:30",
      "venue": "O2 Arena",
      "address": "Peninsula Square, London SE10 0DX",
      "price": "Paid",
      "source": "Eventbrite",
      "url": "https://..."
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
}
```

#### 2. Health Check
**GET** `/api/status`

Check system health and API configuration.

**Response:**
```json
{
  "status": "healthy",
  "service": "SuperExpat AI Agent",
  "timestamp": "2026-01-12T10:30:00Z"
}
```

#### 3. Metrics
**GET** `/api/metrics`

Get system performance metrics (internal use).

---

## 🚀 Deployment

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Deploy Backend to Railway

1. **Sign up**: Go to [railway.app](https://railway.app)
2. **New Project**: Click "New Project" → "Deploy from GitHub"
3. **Select Repo**: Choose your `superexpat-ai-agent` repository
4. **Configure**: Railway auto-detects FastAPI
5. **Add Variables**:
   ```
   EVENTBRITE_API_KEY=your_key
   SERPAPI_KEY=your_key
   GEMINI_API_KEY=your_key
   GEMINI_MODEL=gemini-1.5-flash
   ```
6. **Deploy**: Railway automatically builds and deploys
7. **Get URL**: Copy your backend URL (e.g., `https://superexpat.up.railway.app`)

#### Deploy Frontend to Vercel

```bash
cd frontend

# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy
vercel

# 4. Add environment variable in Vercel dashboard
# REACT_APP_API_URL = https://superexpat.up.railway.app

# 5. Production deployment
vercel --prod
```

### Option 2: Vercel (Both via GitHub)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy SuperExpat AI Agent"
   git push origin main
   ```

2. **Import to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your GitHub repository
   - Vercel auto-detects React app
   - Add environment variable: `REACT_APP_API_URL`
   - Deploy!

3. **Backend**: Deploy to Railway (same steps as above)

---

## 📸 Screenshots

### Home Screen
![Home](docs/screenshots/home.png)
*Clean welcome screen with quick action buttons*

### Search Results
![Results](docs/screenshots/results.png)
*AI-generated summary with event cards in responsive grid*

### Event Details
![Details](docs/screenshots/details.png)
*Detailed event information with booking links*

---

## 🧪 Testing

### Manual Testing

```bash
# Test backend health
curl http://localhost:8000/api/status

# Test search
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "events in London", "page": 1, "page_size": 10}'
```

### Automated Tests (Future)

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

---

## 📊 Performance

- **Average Response Time**: 1.2s - 2.5s
- **Concurrent Users**: Up to 100 (free tier)
- **Data Sources**: 2 (Eventbrite + SerpAPI)
- **AI Processing**: Real-time with Gemini 1.5 Flash
- **Cache Strategy**: Smart caching for repeated queries

---

## 🔐 Security

- API keys stored in environment variables
- CORS properly configured
- Input validation on all endpoints
- Rate limiting (planned)
- HTTPS in production

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Grefith Gohel** - *Initial work* - [YourGitHub](https://github.com/GREFITH)

---

## 🙏 Acknowledgments

- Google Gemini AI for language model
- Eventbrite for events data
- SerpAPI for Google Events integration
- FastAPI community
- React community

---

## 📞 Support

For support, email: grefithgohel90@gmail.com

Or open an issue: [GitHub Issues](https://github.com/GREFITH/superexpat-ai-agent/issues)

---

## 🗺️ Roadmap

- [ ] Add more cities
- [ ] Implement user authentication
- [ ] Save favorite events
- [ ] Email notifications
- [ ] Mobile app (React Native)
- [ ] Advanced filters (price range, date range)
- [ ] Social sharing features

---

**Made with ❤️ using FastAPI, React, and Gemini AI**
