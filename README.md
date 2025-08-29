# 🤖 Personalized AI Travel Guide

A comprehensive AI-powered travel companion that provides personalized travel recommendations and maintains a favorites list. Built with Python, featuring both a Streamlit web interface and a production-ready FastAPI backend.

## 🌟 Features

- **AI-Powered Recommendations**: Get personalized travel guides for any city using Google's Gemini AI
- **Interactive Chat Interface**: Ask follow-up questions and get detailed information about attractions
- **Favorites Management**: Save and manage your favorite places with SQLite database
- **Dual Interface**: Choose between Streamlit web app or REST API
- **Production Ready**: Dockerized with proper logging, error handling, and CORS support
- **Multilingual Support**: Chat in different languages with Amelie, your AI travel guide

## 🏗️ Architecture

```
├── app.py              # Streamlit web interface
├── api.py              # FastAPI REST API server
├── tool.py             # AI response generation using LangChain
├── db.py               # SQLite database operations
├── Dockerfile          # Container configuration
└── requirements.txt    # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))
- Docker (optional, for containerized deployment)

### Option 1: Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd personalized-ai-travel-guide
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Create a `.env` file:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ENVIRONMENT=development
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501
   PORT=8080
   ```

3. **Run Streamlit App**
   ```bash
   streamlit run app.py
   ```
   Access at: `http://localhost:8501`

4. **Run FastAPI Server**
   ```bash
   python api.py
   ```
   Access at: `http://localhost:8080`
   API Documentation: `http://localhost:8080/docs`

### Option 2: Docker Deployment

1. **Build Container**
   ```bash
   docker build -t travel-guide .
   ```

2. **Run Container**
   ```bash
   docker run -p 8080:8080 -e GEMINI_API_KEY=your_key_here travel-guide
   ```

## 📖 Usage Guide

### Streamlit Interface

1. **Enter API Key**: Add your Gemini API key in the sidebar
2. **Choose City**: Enter the city you're traveling to
3. **Generate Guide**: Click "Generate Guide" to get AI recommendations
4. **Interactive Chat**: Ask questions like:
   - "Tell me more about the Eiffel Tower"
   - "What's the best time to visit?"
   - "Save Louvre Museum" (to add to favorites)
5. **Manage Favorites**: View and clear your saved places in the sidebar

### FastAPI Endpoints

#### Core Endpoints

**Get Travel Guide**
```http
POST /guide
Content-Type: application/json

{
  "city": "Paris"
}
```

**Chat with AI Guide**
```http
POST /chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Tell me about museums in Paris"}
  ],
  "city_context": "Paris"
}
```

**Save Favorite Place**
```http
POST /favorites
Content-Type: application/json

{
  "city": "Paris",
  "place_name": "Eiffel Tower"
}
```

**Get All Favorites**
```http
GET /favorites
```

**Clear All Favorites**
```http
DELETE /favorites
```

**Health Check**
```http
GET /health
```

#### Response Examples

**Travel Guide Response**
```json
{
  "guide_content": "🗼 **Eiffel Tower** - **Location**: Champ de Mars...",
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

**Chat Response**
```json
{
  "response": "The Eiffel Tower is definitely a must-see! Here are some insider tips...",
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ |
| `PORT` | Server port | 8080 | ❌ |
| `ENVIRONMENT` | Runtime environment | development | ❌ |
| `ALLOWED_ORIGINS` | CORS allowed origins | * | ❌ |

### Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    place_name TEXT NOT NULL UNIQUE
);
```

## 🤖 AI Guide Persona
Meet **Amelie** - your AI travel companion with:
- Witty and modern personality
- Extensive travel knowledge
- Multilingual capabilities
- Personalized recommendations
- Interactive conversation style

## 🔧 Development

### Project Structure

```
📁 personalized-ai-travel-guide/
├── 📄 app.py                 # Streamlit frontend
├── 📄 api.py                 # FastAPI backend
├── 📄 tool.py                # AI integration layer
├── 📄 db.py                  # Database operations
├── 📄 Dockerfile             # Container setup
├── 📄 requirements.txt       # Dependencies
├── 📄 .env                   # Environment config
└── 📄 travel_guide.db        # SQLite database
```

### Key Dependencies
- **FastAPI**: Modern web framework for APIs
- **Streamlit**: Interactive web app framework  
- **LangChain**: AI integration and prompt management
- **Google GenerativeAI**: Gemini AI model access
- **SQLite**: Lightweight database for favorites
- **Pandas**: Data manipulation for favorites display
- **Uvicorn/Gunicorn**: ASGI server for production

### Adding New Features

1. **New API Endpoint**: Add to `api.py` with proper validation
2. **Database Changes**: Modify `db.py` and update schema
3. **AI Prompts**: Update templates in `tool.py`
4. **UI Changes**: Modify `app.py` for Streamlit interface

## 🚀 Production Deployment

### Docker Production Setup

```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "api:app"]
```

### Cloud Platform Deployment

**Google Cloud Run**
```bash
gcloud run deploy travel-guide \
  --image gcr.io/PROJECT-ID/travel-guide \
  --platform managed \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=your_key
```

**Heroku**
```bash
heroku create your-travel-guide
heroku config:set GEMINI_API_KEY=your_key
git push heroku main
```

### Performance Optimization

- **Caching**: Implement Redis for API response caching
- **Rate Limiting**: Add request rate limiting for production
- **Load Balancing**: Use multiple workers for high traffic
- **CDN**: Serve static assets through CDN

## 🔒 Security Considerations

- **API Key Security**: Never commit API keys to version control
- **Input Validation**: All inputs are validated using Pydantic models
- **CORS Configuration**: Configure allowed origins appropriately
- **Rate Limiting**: Implement in production to prevent abuse
- **Database Security**: Use prepared statements to prevent injection

## 🐛 Troubleshooting

### Common Issues

**"Gemini API key not configured"**
- Ensure `GEMINI_API_KEY` is set in environment or `.env` file
- Verify API key is valid at Google AI Studio

**"Database locked" errors**
- Check file permissions on `travel_guide.db`
- Ensure only one process is accessing the database

**CORS errors in browser**
- Update `ALLOWED_ORIGINS` environment variable
- Check frontend URL is included in allowed origins

**Docker build fails**
- Ensure Docker daemon is running
- Check Dockerfile syntax and dependencies

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for public methods
- Write tests for new features
- Update documentation for changes
  
## 🙏 Acknowledgments

- **Google Gemini AI**: For powering the intelligent recommendations
- **LangChain**: For seamless AI integration
- **Streamlit**: For rapid UI development
- **FastAPI**: For robust API framework

## 📞 Support
For support and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API documentation at `/docs` endpoint

---

**Built with ❤️ for travelers worldwide** 🌍
