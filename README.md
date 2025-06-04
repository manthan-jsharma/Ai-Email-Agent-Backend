# AI Email Agent

An intelligent email management system that uses AI to automatically generate and send email responses. The system integrates with Gmail via OAuth, uses Google Pub/Sub for real-time email notifications, and leverages OpenAI for generating contextually appropriate responses.

## Architecture

\`\`\`
project-root/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── database/         # PostgreSQL schema
├── docker/           # Docker configuration
├── redis/            # Redis configuration
└── scripts/          # Utility scripts
\`\`\`

## Features

- **Gmail Integration**: OAuth authentication and full Gmail API access
- **Real-time Notifications**: Google Pub/Sub integration for instant email updates
- **AI-Powered Responses**: OpenAI integration for generating contextual email replies
- **Three-Tab Interface**:
  - **Compose**: Send new emails
  - **Sent**: View sent email history
  - **Tasks**: Manage AI-generated responses
- **Background Processing**: Celery workers for async AI processing
- **Responsive Design**: Modern UI with Tailwind CSS and shadcn/ui

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Primary database
- **Redis**: Message broker and caching
- **Celery**: Background task processing
- **Google APIs**: Gmail and Pub/Sub integration
- **OpenAI API**: AI response generation

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Modern component library
- **Lucide React**: Icon library

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Google Cloud Project with Gmail and Pub/Sub APIs enabled
- OpenAI API key

### Environment Variables

Copy the `.env` file and update with your actual API keys:

\`\`\`bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_PUBSUB_TOPIC=gmail-notifications

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_email_agent

# Security
JWT_SECRET_KEY=your_jwt_secret
NEXTAUTH_SECRET=your_nextauth_secret
\`\`\`

### Development Setup

1. **Clone and setup**:
\`\`\`bash
git clone <repository>
cd ai-email-agent
\`\`\`

2. **Backend setup**:
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

3. **Frontend setup**:
\`\`\`bash
cd frontend
npm install
\`\`\`

4. **Database setup**:
\`\`\`bash
# Create PostgreSQL database
createdb ai_email_agent

# Run schema
psql ai_email_agent < database/schema.sql
\`\`\`

5. **Start services**:
\`\`\`bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Celery Worker
cd backend
celery -A workers.ai_worker worker --loglevel=info

# Terminal 3: Frontend
cd frontend
npm run dev

# Terminal 4: Redis
redis-server
\`\`\`

### Docker Setup

\`\`\`bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
\`\`\`

## API Endpoints

### Authentication
- `GET /auth/login` - Initiate Gmail OAuth
- `GET /auth/callback` - OAuth callback handler
- `POST /auth/refresh` - Refresh access token

### Gmail
- `GET /gmail/emails/{user_email}` - Get user emails
- `POST /gmail/send` - Send email

### AI Agent
- `POST /agent/generate-response` - Generate AI response
- `POST /agent/send-response` - Send AI response
- `GET /agent/responses/{user_email}` - Get AI responses

### Pub/Sub
- `POST /pubsub/webhook` - Gmail notification webhook
- `POST /pubsub/setup-watch` - Setup Gmail watch

## Gmail Pub/Sub Setup

1. **Create Pub/Sub topic**:
\`\`\`bash
gcloud pubsub topics create gmail-notifications
\`\`\`

2. **Create subscription**:
\`\`\`bash
gcloud pubsub subscriptions create gmail-notifications-sub \
  --topic=gmail-notifications \
  --push-endpoint=https://your-domain.com/pubsub/webhook
\`\`\`

3. **Grant Gmail permissions**:
\`\`\`bash
gcloud projects add-iam-policy-binding your-project-id \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
\`\`\`

## Usage

1. **Authentication**: Click "Connect Gmail Account" to authenticate
2. **Compose**: Use the Compose tab to send emails
3. **Monitor**: Incoming emails trigger automatic AI response generation
4. **Review**: Check the Tasks tab for AI-generated responses
5. **Send**: Approve and send AI responses with one click

## Security Considerations

- OAuth tokens are encrypted and stored securely
- All API endpoints require authentication
- Environment variables contain sensitive data
- CORS is configured for frontend domain only
- Rate limiting should be implemented for production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
