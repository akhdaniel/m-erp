# Installation Guide for XERPIUM ERP System

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04 LTS or later, CentOS 8/RHEL 8, or macOS
- **CPU**: Minimum 2 cores, recommended 4+ cores
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 20GB free space, recommended 50GB+ for production
- **Docker**: Docker Engine v20.10+ with Docker Compose v2.0+
- **Python**: Python 3.9+

### Install Required System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose python3 python3-pip python3-venv git curl
sudo usermod -aG docker $USER  # Add current user to docker group
```

#### CentOS/RHEL:
```bash
sudo yum update -y
sudo yum install -y docker python3 python3-pip git curl
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER  # Add current user to docker group
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### macOS:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 docker docker-compose git
# Docker Desktop needs to be installed separately from https://www.docker.com/products/docker-desktop
```

## Step 1: Clone the Repository

```bash
cd /opt  # or any preferred directory
sudo git clone https://github.com/your-org/m-erp.git
sudo chown -R $USER:$USER m-erp
cd m-erp
```

## Step 2: Set Up Python Virtual Environment

```bash
cd /opt/m-erp
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

## Step 3: Install Python Dependencies

```bash
# Install system-wide dependencies
pip install alembic psycopg2-binary redis httpx requests pyjwt python-multipart python-dotenv

# If using Poetry (if pyproject.toml exists)
pip install poetry
poetry install
```

## Step 4: Set Up Environment Variables

Create a global `.env` file in the root directory:

```bash
touch .env
```

Add these common environment variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/xerp_db
REDIS_URL=redis://localhost:6379

# Authentication
AUTH_SECRET=your-super-secret-jwt-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Service Configuration
SERVICE_NAME=main
COMPANY_ID=1

# Logging
LOG_LEVEL=INFO

# Development/Production
ENVIRONMENT=production  # or development
```

## Step 5: Set Up Database

### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install -y postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install -y postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS - install via Homebrew
brew install postgresql
brew services start postgresql
```

### Create Database and User
```bash
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE DATABASE xerp_db;
CREATE USER xerp_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE xerp_db TO xerp_user;
ALTER USER xerp_user CREATEDB;
\q
```

## Step 6: Configure Individual Services

### For each service in `/services/` directory:

1. Navigate to the service directory:
```bash
cd /opt/m-erp/services/sales-service
```

2. Create or update the service-specific `.env` file:
```bash
cat > .env << EOF
DATABASE_URL=postgresql://xerp_user:your_secure_password@localhost:5432/sales_db
REDIS_URL=redis://localhost:6379
AUTH_SECRET=your-super-secret-jwt-key-change-in-production
SERVICE_NAME=sales
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF
```

3. Create the service's database:
```bash
sudo -u postgres createdb sales_db
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sales_db TO xerp_user;"
```

## Step 7: Run Database Migrations

If you have alembic migrations for each service:

```bash
# For each service directory
cd /opt/m-erp/services/sales-service
source /opt/m-erp/venv/bin/activate
python -m alembic upgrade head
```

## Step 8: Set Up Docker Compose

Create a main `docker-compose.yml` file in the root directory:

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: xerp-postgres
    environment:
      POSTGRES_DB: xerp_db
      POSTGRES_USER: xerp_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - xerp-network

  redis:
    image: redis:7-alpine
    container_name: xerp-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - xerp-network

  sales-service:
    build: ./services/sales-service
    container_name: xerp-sales-service
    environment:
      - DATABASE_URL=postgresql://xerp_user:your_secure_password@postgres:5432/sales_db
      - REDIS_URL=redis://redis:6379
      - AUTH_SECRET=your-super-secret-jwt-key-change-in-production
    ports:
      - "8001:8000"
    depends_on:
      - postgres
      - redis
    networks:
      - xerp-network

  # Add other services following the same pattern

volumes:
  postgres_data:
  redis_data:

networks:
  xerp-network:
    driver: bridge
EOF
```

## Step 9: Build and Start Services

### Using Docker Compose:

```bash
cd /opt/m-erp
docker-compose up -d --build
```

### Or start services individually:

```bash
# Source virtual environment
source /opt/m-erp/venv/bin/activate

# Start each service in background
cd /opt/m-erp/services/sales-service
nohup uvicorn main:app --host 0.0.0.0 --port 8001 > sales_service.log 2>&1 &

# Repeat for other services...
```

## Step 10: Set Up API Gateway (if using Kong)

```bash
# Install Kong if required
curl -Lo kong-3.0.0.ubuntu-focal_amd64.deb "https://download.konghq.com/gateway-3.x-ubuntu-focal/pool/all/k/kong/kong_3.0.0.ubuntu-focal_amd64.deb"
sudo apt install -y ./kong-3.0.0.ubuntu-focal_amd64.deb
sudo kong migrations bootstrap
sudo systemctl start kong
sudo systemctl enable kong
```

## Step 11: Set Up Reverse Proxy (Nginx)

```bash
# Install Nginx
sudo apt install -y nginx  # Ubuntu/Debian
sudo yum install -y nginx  # CentOS/RHEL

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/xerp << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8001;  # Main API Gateway
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/v1/sales/ {
        proxy_pass http://localhost:8001;
    }
    
    # Add other service routes as needed
}
EOF

sudo ln -s /etc/nginx/sites-available/xerp /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

## Step 12: Set Up SSL (Optional but Recommended for Production)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx  # Ubuntu
sudo yum install -y certbot python3-certbot-nginx  # CentOS

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Step 13: Set Up Monitoring and Logging

### Install monitoring tools:
```bash
# For application logs
mkdir -p /var/log/xerp
sudo chown $USER:$USER /var/log/xerp

# For PostgreSQL logs
sudo mkdir -p /var/log/postgresql
sudo chown postgres:postgres /var/log/postgresql
```

### Set up log rotation:
```bash
sudo tee /etc/logrotate.d/xerp << 'EOF'
/var/log/xerp/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        # Service restart commands if needed
    endscript
}
EOF
```

## Step 14: Set Up Systemd Services (Optional - for production)

Create systemd service files for each service:

```bash
sudo tee /etc/systemd/system/xerp-sales.service << 'EOF'
[Unit]
Description=XERPIUM Sales Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/m-erp/services/sales-service
EnvironmentFile=/opt/m-erp/.env
ExecStart=/opt/m-erp/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable xerp-sales
sudo systemctl start xerp-sales
```

## Step 15: Verification and Testing

### Check service status:
```bash
docker-compose ps  # If using Docker
systemctl status xerp-sales  # If using systemd
```

### Test API endpoints:
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health  # Other services
```

### Check database connectivity:
```bash
psql -h localhost -U xerp_user -d xerp_db -c "SELECT version();"
```

## Step 16: Security Hardening

### Set secure permissions:
```bash
sudo chown -R root:root /opt/m-erp
sudo chmod -R 755 /opt/m-erp
sudo chmod 600 /opt/m-erp/.env /opt/m-erp/services/*/.env
```

### Firewall configuration:
```bash
# Ubuntu/Debian
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'  # or specific ports like 80, 443, 8001-8010

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## Post-Installation Tasks

1. **Backup Strategy**: Set up regular PostgreSQL backups
2. **Monitoring**: Set up monitoring with tools like Prometheus/Grafana
3. **Alerting**: Configure alerting for service failures
4. **Documentation**: Update API documentation
5. **Security**: Regular security updates and patches

## Troubleshooting

### Common Issues:

1. **Port conflicts**: Check if required ports are available
2. **Database connection**: Verify database credentials and network connectivity
3. **Docker permissions**: Ensure user is in docker group
4. **Environment variables**: Verify all .env files are properly configured

### Useful Commands:

```bash
# View Docker logs
docker-compose logs -f service_name

# Check running processes
ps aux | grep uvicorn

# Database maintenance
pg_dump -h localhost -U xerp_user xerp_db > backup.sql
```

This installation guide provides a comprehensive approach to setting up the XERPIUM ERP system on a new server. Adjust paths, passwords, and service names according to your specific deployment requirements.