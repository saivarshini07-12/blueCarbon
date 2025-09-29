# Docker Deployment Guide for YourCarbonFootprint

## Prerequisites

- Docker and Docker Compose installed on your system
- A Groq API key (for AI features)

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd Carbon_Accounting
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env file and add your GROQ_API_KEY
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   Open your browser and go to `http://localhost:8501`

## Alternative: Build and Run with Docker Only

1. **Build the Docker image**:
   ```bash
   docker build -t yourcarbonfootprint .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8501:8501 \
     -e GROQ_API_KEY=your_groq_api_key_here \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/.env:/app/.env:ro \
     yourcarbonfootprint
   ```

## Configuration

### Environment Variables

- `GROQ_API_KEY`: Required for AI-powered features
- `DATA_DIR`: Optional, defaults to `./data`
- `LOG_LEVEL`: Optional, defaults to `INFO`

### Volumes

- `./data:/app/data`: Persists emissions data and reports
- `./.env:/app/.env:ro`: Mounts environment configuration (read-only)

## Production Deployment

For production deployment, consider:

1. **Use a reverse proxy** (nginx, traefik) for HTTPS termination
2. **Set up proper logging** and monitoring
3. **Use Docker secrets** for sensitive environment variables
4. **Configure backup** for the data volume
5. **Set resource limits** in docker-compose.yml:

```yaml
services:
  yourcarbonfootprint:
    # ... other configuration
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Health Check

The container includes a health check that monitors the Streamlit application status. You can check the health status with:

```bash
docker ps
# or
docker-compose ps
```

## Troubleshooting

1. **Port already in use**: Change the port mapping in docker-compose.yml or use a different port:
   ```bash
   docker-compose up --build -p 8502:8501
   ```

2. **Permission issues with data volume**: Ensure the data directory has proper permissions:
   ```bash
   chmod 755 data/
   ```

3. **Missing API key**: Make sure your .env file contains a valid GROQ_API_KEY

4. **Container logs**: Check logs for debugging:
   ```bash
   docker-compose logs -f yourcarbonfootprint
   ```

## Stopping the Application

```bash
docker-compose down
```

To also remove volumes:
```bash
docker-compose down -v
```
