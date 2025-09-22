# FinbrAIn - Multi-Agent Financial Advisory System

A sophisticated AI-powered financial research and analysis platform built with LangChain, LangGraph, FastAPI, and Next.js.

## 🎯 Project Overview

FinbrAIn implements a multi-agent system for autonomous financial research with the following capabilities:

### Agent Functions
- **Autonomous Investment Research Agent** that:
  - Plans research steps for any stock symbol
  - Uses tools dynamically (APIs, datasets, retrieval)
  - Self-reflects to assess output quality
  - Learns across runs with persistent memory

### Workflow Patterns
1. **Prompt Chaining**: News → Preprocess → Classify → Extract → Summarize
2. **Routing**: Direct content to specialist agents (earnings, news, market analyzers)
3. **Evaluator-Optimizer**: Generate analysis → evaluate quality → refine using feedback

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI   │    │  FastAPI Backend │    │   Agent System  │
│   (Port 3000)  │◄──►│   (Port 8000)   │◄──►│   (LangGraph)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MUI Components│    │   API Endpoints │    │  Memory System  │
│   React Hooks   │    │   Data Models   │    │  Vector Store   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API Key
- Optional: NewsAPI, Alpha Vantage, FRED API keys

### Backend Setup

1. **Clone and navigate to backend**:
```bash
cd backend
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Start the backend**:
```bash
python app/main.py
```
Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend**:
```bash
cd finbrain
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start the development server**:
```bash
npm run dev
```
Frontend will be available at `http://localhost:3000`

## 📋 API Endpoints

### Agents Service (`/api/agents`)
- `POST /research` - Comprehensive stock research
- `GET /data/{symbol}` - Financial data for stock
- `GET /fundamentals/{symbol}` - Fundamental analysis
- `GET /news/{symbol}` - Latest news
- `GET /economic-context` - Economic indicators
- `POST /batch-research` - Batch stock analysis

### Analysis Service (`/api/analysis`)
- `POST /news/process` - Process news through chain
- `POST /content/route` - Route content to specialists
- `POST /analysis/evaluate` - Evaluate and optimize analysis
- `POST /batch/route-content` - Batch content routing

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Financial APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here
FRED_API_KEY=your_fred_api_key_here

# LangSmith (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=finbrain-agents

# Application Settings
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

## 📊 Data Sources

- **Yahoo Finance**: Stock prices, fundamentals, company info
- **NewsAPI**: Financial news and sentiment
- **FRED API**: Economic indicators
- **Alpha Vantage**: Additional financial data

## 🧠 Agent System

### Investment Research Agent
Autonomous agent built with LangGraph that:
- Creates research plans
- Collects data from multiple sources
- Performs comprehensive analysis
- Self-evaluates and improves
- Maintains persistent memory

### Specialist Agents
- **Earnings Analyst**: Financial reports and metrics
- **News Analyst**: Sentiment and market impact
- **Market Analyst**: Price action and trends
- **Technical Analyst**: Chart patterns and indicators
- **Economic Analyst**: Macro indicators and policy

### Memory System
- **SQLite Storage**: Structured data and sessions
- **Vector Store**: Semantic search and similarity
- **Learning Tracking**: Performance and improvements

## 🔄 Workflows

### 1. Prompt Chaining
```
Raw News → Validation → Preprocessing → Classification → Extraction → Summary
```

### 2. Content Routing
```
Content Analysis → Specialist Selection → Expert Analysis → Results
```

### 3. Evaluator-Optimizer
```
Initial Analysis → Quality Evaluation → Feedback → Optimization → Final Output
```

## 🎨 Frontend Features

- **Real-time Stock Analysis**: Interactive research interface
- **News Processing**: Visualize news analysis pipeline
- **Agent Routing**: See how content routes to specialists
- **Quality Evaluation**: Monitor analysis quality scores
- **Performance Dashboards**: Track agent learning and improvements

## 🧪 Testing

Run backend tests:
```bash
cd backend
pytest
```

Run frontend tests:
```bash
cd finbrain
npm test
```

## 📈 Performance Monitoring

The system includes:
- Request/response time tracking
- Agent performance metrics
- Memory usage optimization
- Quality score tracking
- Learning progression analysis

## 🔐 Security

- API key management through environment variables
- Request validation and sanitization
- Rate limiting (when configured)
- CORS configuration for frontend integration

## 🚀 Deployment

### Backend Deployment
```bash
# Using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Using Docker (create Dockerfile)
docker build -t finbrain-backend .
docker run -p 8000:8000 finbrain-backend
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Start production server
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions and support:
- Create an issue on GitHub
- Check the documentation
- Review the API endpoints at `http://localhost:8000/docs`

## 🔮 Future Enhancements

- Real-time market data streaming
- Advanced portfolio optimization
- Multi-language support
- Mobile app development
- Integration with trading platforms
- Advanced risk modeling
- Social sentiment analysis

---

**Built with ❤️ using LangChain, LangGraph, FastAPI, and Next.js**