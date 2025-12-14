# Streamlit Agent Application - Deployment Guide

This guide provides comprehensive instructions for deploying the Streamlit Agent application in various environments, from local development to production systems.

## 🚀 Deployment Overview

The Streamlit Agent application can be deployed in multiple ways:

- **Local Development**: Direct Python execution
- **Docker Container**: Containerized deployment
- **Cloud Platforms**: AWS, GCP, Azure
- **Traditional Servers**: Linux/Windows servers
- **Container Orchestration**: Kubernetes, Docker Swarm

## 📋 Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 1GB free space (more for diagram storage)
- **Network**: Internet access for MCP servers
- **OS**: Linux, macOS, or Windows

### Dependencies

- **Core**: Streamlit, Strands Agents, MCP
- **System**: Graphviz (for diagram generation)
- **Optional**: Docker, Kubernetes CLI

## 🏠 Local Development Deployment

### Quick Setup

```bash
# Clone/navigate to project
cd streamlit_agent

# Install dependencies
pip install -r requirements.txt

# Start application
python start.py
```

### Virtual Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start application
python start.py
```

### Development Configuration

Create `config.dev.json`:
```json
{
  "port": 8501,
  "host": "localhost",
  "debug": true,
  "log_level": "DEBUG",
  "cleanup_old_diagrams": false
}
```

Start with development config:
```bash
python start.py --config-file config.dev.json
```

## 🐳 Docker Deployment

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p generated-diagrams logs test_screenshots

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start application
CMD ["python", "start.py", "--host", "0.0.0.0"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  streamlit-agent:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./generated-diagrams:/app/generated-diagrams
      - ./logs:/app/logs
      - ./config.prod.json:/app/config.json
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Build and Run

```bash
# Build Docker image
docker build -t streamlit-agent .

# Run container
docker run -d \
  --name streamlit-agent \
  -p 8501:8501 \
  -v $(pwd)/generated-diagrams:/app/generated-diagrams \
  -v $(pwd)/logs:/app/logs \
  streamlit-agent

# Or use Docker Compose
docker-compose up -d
```

### Docker Production Configuration

Create `config.docker.json`:
```json
{
  "host": "0.0.0.0",
  "port": 8501,
  "debug": false,
  "log_level": "INFO",
  "streamlit_config": {
    "server.headless": true,
    "browser.gatherUsageStats": false
  },
  "logging_config": {
    "log_to_console": true,
    "log_to_file": true
  }
}
```

## ☁️ Cloud Platform Deployment

### AWS Deployment

#### AWS ECS (Elastic Container Service)

1. **Create ECR Repository:**
```bash
aws ecr create-repository --repository-name streamlit-agent
```

2. **Build and Push Image:**
```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t streamlit-agent .
docker tag streamlit-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/streamlit-agent:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/streamlit-agent:latest
```

3. **ECS Task Definition:**
```json
{
  "family": "streamlit-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "streamlit-agent",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/streamlit-agent:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/streamlit-agent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### AWS EC2 Deployment

```bash
# Connect to EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Deploy application
docker run -d \
  --name streamlit-agent \
  -p 80:8501 \
  --restart unless-stopped \
  streamlit-agent
```

### Google Cloud Platform (GCP)

#### Cloud Run Deployment

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/streamlit-agent

# Deploy to Cloud Run
gcloud run deploy streamlit-agent \
  --image gcr.io/PROJECT-ID/streamlit-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 2Gi \
  --cpu 1
```

#### GKE (Google Kubernetes Engine)

Create `k8s-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: streamlit-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: streamlit-agent
  template:
    metadata:
      labels:
        app: streamlit-agent
    spec:
      containers:
      - name: streamlit-agent
        image: gcr.io/PROJECT-ID/streamlit-agent
        ports:
        - containerPort: 8501
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: streamlit-agent-service
spec:
  selector:
    app: streamlit-agent
  ports:
  - port: 80
    targetPort: 8501
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

### Microsoft Azure

#### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name streamlit-agent \
  --image streamlit-agent:latest \
  --dns-name-label streamlit-agent-unique \
  --ports 8501 \
  --memory 2 \
  --cpu 1
```

#### Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name streamlit-agent-plan \
  --resource-group myResourceGroup \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group myResourceGroup \
  --plan streamlit-agent-plan \
  --name streamlit-agent-app \
  --deployment-container-image-name streamlit-agent:latest
```

## 🖥️ Traditional Server Deployment

### Linux Server (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv graphviz

# Create application user
sudo useradd -m -s /bin/bash streamlit-agent
sudo su - streamlit-agent

# Setup application
git clone <repository-url> streamlit_agent
cd streamlit_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/streamlit-agent.service > /dev/null <<EOF
[Unit]
Description=Streamlit Agent Application
After=network.target

[Service]
Type=simple
User=streamlit-agent
WorkingDirectory=/home/streamlit-agent/streamlit_agent
Environment=PATH=/home/streamlit-agent/streamlit_agent/venv/bin
ExecStart=/home/streamlit-agent/streamlit_agent/venv/bin/python start.py --host 0.0.0.0 --port 8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable streamlit-agent
sudo systemctl start streamlit-agent
```

### Windows Server

```powershell
# Install Python (if not already installed)
# Download from https://www.python.org/downloads/

# Setup application
git clone <repository-url> streamlit_agent
cd streamlit_agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create Windows service (using NSSM)
# Download NSSM from https://nssm.cc/download
nssm install StreamlitAgent
nssm set StreamlitAgent Application "C:\path\to\streamlit_agent\venv\Scripts\python.exe"
nssm set StreamlitAgent AppParameters "start.py --host 0.0.0.0 --port 8501"
nssm set StreamlitAgent AppDirectory "C:\path\to\streamlit_agent"
nssm start StreamlitAgent
```

## 🔧 Kubernetes Deployment

### Complete Kubernetes Manifests

#### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: streamlit-agent
```

#### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: streamlit-agent-config
  namespace: streamlit-agent
data:
  config.json: |
    {
      "host": "0.0.0.0",
      "port": 8501,
      "debug": false,
      "log_level": "INFO",
      "streamlit_config": {
        "server.headless": true,
        "browser.gatherUsageStats": false
      }
    }
```

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: streamlit-agent
  namespace: streamlit-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: streamlit-agent
  template:
    metadata:
      labels:
        app: streamlit-agent
    spec:
      containers:
      - name: streamlit-agent
        image: streamlit-agent:latest
        ports:
        - containerPort: 8501
        volumeMounts:
        - name: config-volume
          mountPath: /app/config.json
          subPath: config.json
        - name: diagrams-volume
          mountPath: /app/generated-diagrams
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config-volume
        configMap:
          name: streamlit-agent-config
      - name: diagrams-volume
        emptyDir: {}
```

#### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: streamlit-agent-service
  namespace: streamlit-agent
spec:
  selector:
    app: streamlit-agent
  ports:
  - port: 80
    targetPort: 8501
  type: ClusterIP
```

#### Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: streamlit-agent-ingress
  namespace: streamlit-agent
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: streamlit-agent.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: streamlit-agent-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n streamlit-agent
kubectl get services -n streamlit-agent
kubectl get ingress -n streamlit-agent

# View logs
kubectl logs -f deployment/streamlit-agent -n streamlit-agent
```

## 🔒 Production Security

### SSL/TLS Configuration

#### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name streamlit-agent.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name streamlit-agent.example.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Apache Reverse Proxy

```apache
<VirtualHost *:443>
    ServerName streamlit-agent.example.com
    
    SSLEngine on
    SSLCertificateFile /path/to/certificate.crt
    SSLCertificateKeyFile /path/to/private.key
    
    ProxyPreserveHost On
    ProxyPass / http://localhost:8501/
    ProxyPassReverse / http://localhost:8501/
    
    ProxyPass /ws ws://localhost:8501/ws
    ProxyPassReverse /ws ws://localhost:8501/ws
</VirtualHost>
```

### Firewall Configuration

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8501/tcp   # Block direct access to Streamlit
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 📊 Monitoring & Logging

### Application Monitoring

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'streamlit-agent'
    static_configs:
      - targets: ['localhost:8501']
    metrics_path: /_stcore/metrics
```

#### Grafana Dashboard

Create dashboard with panels for:
- Application uptime
- Response times
- Error rates
- Resource usage
- Active users

### Log Management

#### Centralized Logging with ELK Stack

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

  streamlit-agent:
    build: .
    ports:
      - "8501:8501"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Streamlit Agent

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest tests/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build Docker image
      run: |
        docker build -t streamlit-agent:${{ github.sha }} .
    - name: Deploy to production
      run: |
        # Add deployment commands here
        echo "Deploying to production..."
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest tests/

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t streamlit-agent:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - kubectl set image deployment/streamlit-agent streamlit-agent=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main
```

## 🚀 Scaling & Performance

### Horizontal Scaling

#### Load Balancer Configuration

```nginx
upstream streamlit_backend {
    server 127.0.0.1:8501;
    server 127.0.0.1:8502;
    server 127.0.0.1:8503;
}

server {
    listen 80;
    location / {
        proxy_pass http://streamlit_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Docker Swarm

```yaml
# docker-stack.yml
version: '3.8'

services:
  streamlit-agent:
    image: streamlit-agent:latest
    ports:
      - "8501:8501"
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    networks:
      - streamlit-network

networks:
  streamlit-network:
    driver: overlay
```

Deploy:
```bash
docker stack deploy -c docker-stack.yml streamlit-agent-stack
```

### Performance Optimization

#### Application Configuration

```json
{
  "agent_timeout": 60,
  "max_diagrams": 50,
  "cleanup_old_diagrams": true,
  "max_diagram_age_hours": 2,
  "streamlit_config": {
    "server.maxUploadSize": 50,
    "server.maxMessageSize": 50,
    "server.enableStaticServing": true
  }
}
```

#### Resource Limits

```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

## 🛠️ Troubleshooting Deployment

### Common Deployment Issues

1. **Port Binding Failures**
   ```bash
   # Check port usage
   netstat -tulpn | grep 8501
   # Use different port
   python start.py --port 8502
   ```

2. **Permission Issues**
   ```bash
   # Fix file permissions
   chmod -R 755 streamlit_agent/
   chown -R app:app streamlit_agent/
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats
   # Increase memory limits
   ```

4. **Network Connectivity**
   ```bash
   # Test connectivity
   curl -f http://localhost:8501/_stcore/health
   # Check firewall rules
   ```

### Health Checks

```bash
# Application health check
curl -f http://localhost:8501/_stcore/health

# Component validation
python start.py --validate-only

# Log analysis
tail -f logs/startup.log
grep -i error logs/streamlit_agent_errors.log
```

---

**Need deployment help?** Check the troubleshooting section or review the deployment logs for specific error messages and solutions.