# CIS Backend - Docker Setup

This project runs in a Docker container for easy deployment and development.

## Quick Start

1. **Using Make (Recommended):**
   ```bash
   make build
   make up
   ```

2. **Using Docker Compose directly:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

## Available Commands

### Development Commands
```bash
make help          # Show all available commands
make build         # Build the Docker image
make up            # Start the application
make down          # Stop the application
make logs          # View application logs
make shell         # Open shell in container
make restart       # Restart the application
make clean         # Clean up Docker resources
make dev           # Development mode with hot reload
```

### Manual Docker Commands
```bash
# Build and start
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down

# Open shell
docker-compose exec backend bash
```

## Environment Configuration

The application uses environment variables from `.env` file. Make sure it contains:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1
APPARELS_S3_BUCKET_NAME=your_bucket
BUCKET_BASE_URL=https://your-bucket.s3.region.amazonaws.com/

# Application
ENV=production
LOG_LEVEL=INFO
```

## API Endpoints

- **Health Check:** `GET http://localhost:8001/health`
- **Upload Files:** `POST http://localhost:8001/analyze-contracts`
- **Upload Files (legacy):** `POST http://localhost:8001/upload`

## File Upload Example

```bash
curl -X POST "http://localhost:8001/analyze-contracts" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@contract.pdf"
```

## Development

### Hot Reload
For development with automatic code reloading:
```bash
make dev
```

### Volume Mounts
The development setup mounts the entire project directory for live code changes.

### Logs
View real-time logs:
```bash
make logs
```

## Production Considerations

1. **Remove development volume mount** in `docker-compose.yml`
2. **Set proper environment variables**
3. **Add nginx reverse proxy** (uncomment nginx section in docker-compose.yml)
4. **Use proper secrets management** instead of .env file

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   sudo lsof -i :8001
   # Kill the process or change port
   ```

2. **Permission issues:**
   ```bash
   sudo chown -R $USER:$USER uploads/
   ```

3. **Build failures:**
   ```bash
   make clean
   make build
   ```

### Health Check
The container includes a health check that monitors `/health` endpoint.

## Architecture

```
┌─────────────────┐
│   Docker Host   │
│                 │
│ ┌─────────────┐ │
│ │  Container  │ │
│ │ ┌─────────┐ │ │
│ │ │FastAPI  │ │ │
│ │ │App      │ │ │
│ │ └─────────┘ │ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │   S3 Bucket │ │
│ └─────────────┘ │
└─────────────────┘
```
