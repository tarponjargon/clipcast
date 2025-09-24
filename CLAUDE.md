# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Starting the Development Environment
```bash
./start.sh  # Starts Docker containers, webpack dev server, and ngrok
```

### Build and Package Management
```bash
npm install --legacy-peer-deps  # Install npm packages
npm run start  # Start webpack dev server for development
npm run production  # Build for production
npm run deploy  # Deploy to production (includes predeploy/postdeploy scripts)
```

### Python Package Management
```bash
# Install Python packages (while containers are running)
pip3 install [PACKAGE]; pip3 freeze > requirements.txt; docker exec -it clipcast-local pip3 install -r requirements.txt
```

### Testing
```bash
# Run Playwright tests (always use --workers=1 to avoid parallel execution issues)
npx playwright test --workers=1  # Run all tests headless
npx playwright test --workers=1 --ui --headed --debug  # Development mode with UI
npx playwright test --workers=1 e2e/03_add_episode.spec.js --project=webkit --trace=on  # Run specific test
npx playwright test --workers=1 --trace=on --project=chromium  # Run with specific browser
```

### Docker Container Management
```bash
docker exec -it clipcast-local /bin/bash  # SSH to Flask app container
docker exec -it clipcast-local-database /bin/bash  # SSH to MySQL container
docker logs --follow clipcast-local  # Tail application logs
docker compose down  # Stop all containers
```

### Flask Commands
```bash
# Inside container or with flask cli
flask shell  # Start interactive shell
flask process_content  # Process queued podcast content
flask process_podcast_episode [content_id]  # Process specific episode
flask process_email  # Process email queue
flask delete_old_files  # Clean up S3 storage
```

## Architecture Overview

### Technology Stack
- **Backend**: Python/Flask with Gunicorn
- **Frontend**: Bootstrap 5, HTMX for dynamic updates, custom JavaScript
- **Database**: MySQL 8.2
- **Caching**: Redis for sessions and cache
- **Storage**: S3-compatible object storage for audio files
- **Text-to-Speech**: OpenAI TTS, Amazon Polly, Google TTS
- **Testing**: Playwright for E2E tests
- **Development**: Docker Compose, Webpack, ngrok for local development

### Key Application Flows

1. **Content Processing Pipeline**:
   - User submits URL or text content
   - Content queued in `podcast_content` table with status 'queued'
   - Background processor fetches content (uses Playwright or requests)
   - Text extracted using trafilatura
   - Audio generated via TTS services (OpenAI/Google/Polly)
   - MP3 uploaded to S3 storage
   - RSS feed updated for user's podcast

2. **User Authentication**:
   - Session management via Redis
   - Cookie-based auth with UUID user IDs
   - Google OAuth integration available
   - Password reset via email tokens

3. **Payment Integration**:
   - Stripe for subscription management
   - Webhook handling for payment events
   - Premium vs base voice tiers

### Critical File Locations

- **Flask App Factory**: `flask_app/__init__.py`
- **Content Processing**: `flask_app/modules/content/process_content.py`
- **User Management**: `flask_app/modules/user/`
- **TTS Services**: `flask_app/modules/tts/`
- **Database Manager**: `flask_app/modules/database/db_manager.py`
- **Routes**: `flask_app/routes/` (views, api, partials)
- **Frontend Assets**: `public_html/` (built by webpack)

### Environment Configuration

Required environment variables (see `.envrc.sample`):
- Database: `MYSQL_*` variables
- S3: `S3_BUCKET`, `S3_URL`, `S3_ACCESS_KEY`, `S3_SECRET_ACCESS_KEY`
- TTS APIs: `OPENAI_API_KEY`, `AWS_ACCESS_KEY_ID`, `GOOGLE_APPLICATION_CREDENTIALS`
- Stripe: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`
- Email: `MAIL_USERNAME`, `MAIL_PASSWORD` (Gmail app password)
- Server: `SERVER_HOST` (ngrok domain), `WEB_HOST`, `APP_HOST`

### Database Schema Notes

Key tables:
- `users`: User accounts with subscription status
- `podcast_content`: Content queue and episode data
- `voices`: Available TTS voices and configurations
- RSS feeds are generated dynamically from podcast_content

### Testing Approach

- E2E tests use Playwright with real browser automation
- Tests run sequentially (`--workers=1`) to avoid conflicts
- Test data uses environment variables (`TEST_EMAIL1`, etc.)
- Database cleanup handled between tests