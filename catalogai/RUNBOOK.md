# CatalogAI Operations Runbook

This runbook provides operational procedures for deploying, maintaining, and troubleshooting the CatalogAI system.

## 🚀 Deployment Procedures

### Initial Deployment

1. **Prerequisites Check**
   ```bash
   # Verify Docker and Docker Compose
   docker --version
   docker compose version
   
   # Check system resources
   df -h  # Disk space (minimum 2GB free)
   free -h  # Memory (minimum 2GB RAM)
   ```

2. **Environment Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd catalogai
   
   # Copy environment configuration
   cp .env.example .env
   
   # Edit configuration as needed
   nano .env
   ```

3. **Deploy Services**
   ```bash
   cd ops
   docker compose up -d --build
   
   # Verify deployment
   docker compose ps
   docker compose logs -f
   ```

4. **Health Verification**
   ```bash
   # Check backend health
   curl http://localhost:8000/health/
   
   # Check frontend
   curl http://localhost:3000/
   
   # Verify model training completed
   curl http://localhost:8000/admin/metrics
   ```

### Production Deployment

1. **Production Environment Variables**
   ```bash
   # .env.production
   DB_URL=postgresql://user:pass@db:5432/catalogai
   THRESH_AUTH=0.15
   THRESH_SYN=0.70
   MAX_IMAGE_MB=8
   LOG_LEVEL=WARNING
   NEXT_PUBLIC_API_BASE=https://api.catalogai.com
   ```

2. **Production Docker Compose**
   ```yaml
   # docker-compose.prod.yml
   version: '3.8'
   services:
     backend:
       build: ../backend
       environment:
         - DB_URL=${DB_URL}
         - LOG_LEVEL=WARNING
       restart: always
       deploy:
         resources:
           limits:
             memory: 1G
             cpus: '0.5'
   ```

3. **SSL/TLS Setup**
   ```bash
   # Using Let's Encrypt with nginx
   certbot --nginx -d catalogai.com -d api.catalogai.com
   ```

## 🔧 Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- [ ] Check service health endpoints
- [ ] Monitor disk space usage
- [ ] Review error logs
- [ ] Verify backup completion

#### Weekly
- [ ] Update system packages
- [ ] Review performance metrics
- [ ] Clean up old scan records
- [ ] Test backup restoration

#### Monthly
- [ ] Update dependencies
- [ ] Review and rotate logs
- [ ] Performance optimization review
- [ ] Security updates

### Model Management

#### Retraining the Model

1. **Scheduled Retraining**
   ```bash
   # Create cron job for weekly retraining
   0 2 * * 0 curl -X POST http://localhost:8000/admin/train
   ```

2. **Manual Retraining**
   ```bash
   # Via API
   curl -X POST http://localhost:8000/admin/train
   
   # Via admin interface
   # Navigate to http://localhost:3000/admin
   # Click "Retrain Model" button
   ```

3. **Monitoring Training Progress**
   ```bash
   # Check logs during training
   docker compose logs -f backend
   
   # Verify new model metrics
   curl http://localhost:8000/admin/metrics
   ```

#### Threshold Adjustment

1. **Performance-Based Adjustment**
   ```bash
   # Get current thresholds
   curl http://localhost:8000/admin/thresholds
   
   # Update thresholds
   curl -X PUT http://localhost:8000/admin/thresholds \
     -H "Content-Type: application/json" \
     -d '{"thresh_auth": 0.12, "thresh_syn": 0.75}'
   ```

2. **A/B Testing Thresholds**
   - Deploy with different thresholds to test groups
   - Monitor false positive/negative rates
   - Adjust based on user feedback and accuracy metrics

### Database Management

#### Backup Procedures

1. **SQLite Backup (Development)**
   ```bash
   # Create backup
   docker compose exec backend sqlite3 /app/app.db ".backup /app/backup.db"
   
   # Copy backup to host
   docker compose cp backend:/app/backup.db ./backups/
   ```

2. **PostgreSQL Backup (Production)**
   ```bash
   # Create backup
   docker compose exec db pg_dump -U catalogai catalogai > backup.sql
   
   # Automated backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   docker compose exec db pg_dump -U catalogai catalogai > "backup_${DATE}.sql"
   gzip "backup_${DATE}.sql"
   ```

#### Database Cleanup

1. **Remove Old Scan Records**
   ```sql
   -- Remove scans older than 90 days
   DELETE FROM scans WHERE created_at < datetime('now', '-90 days');
   
   -- Vacuum database to reclaim space
   VACUUM;
   ```

2. **Archive Old Data**
   ```bash
   # Export old records before deletion
   sqlite3 app.db "SELECT * FROM scans WHERE created_at < datetime('now', '-90 days');" > archived_scans.csv
   ```

## 📊 Monitoring and Alerting

### Health Monitoring

1. **Service Health Checks**
   ```bash
   #!/bin/bash
   # health_check.sh
   
   # Check backend
   if ! curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
     echo "Backend health check failed"
     exit 1
   fi
   
   # Check frontend
   if ! curl -f http://localhost:3000/ > /dev/null 2>&1; then
     echo "Frontend health check failed"
     exit 1
   fi
   
   echo "All services healthy"
   ```

2. **Resource Monitoring**
   ```bash
   # Monitor disk usage
   df -h | grep -E '(8[0-9]|9[0-9])%' && echo "Disk usage critical"
   
   # Monitor memory usage
   free | awk 'NR==2{printf "Memory Usage: %s/%sMB (%.2f%%)\n", $3,$2,$3*100/$2 }'
   ```

### Performance Metrics

1. **API Response Times**
   ```bash
   # Monitor scan endpoint performance
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/scans/
   ```

2. **Model Performance Tracking**
   ```bash
   # Get current model metrics
   curl http://localhost:8000/admin/metrics | jq '.accuracy'
   ```

### Log Management

1. **Log Rotation**
   ```bash
   # Configure logrotate
   /var/log/catalogai/*.log {
     daily
     rotate 30
     compress
     delaycompress
     missingok
     notifempty
     create 644 root root
   }
   ```

2. **Log Analysis**
   ```bash
   # Find errors in logs
   docker compose logs backend | grep ERROR
   
   # Monitor scan volumes
   docker compose logs backend | grep "POST /scans" | wc -l
   ```

## 🚨 Troubleshooting Guide

### Common Issues

#### Backend Won't Start

**Symptoms:**
- Container exits immediately
- Health check fails
- Database connection errors

**Diagnosis:**
```bash
# Check container logs
docker compose logs backend

# Check container status
docker compose ps

# Test database connectivity
docker compose exec backend python -c "from app.db import engine; print('DB OK')"
```

**Solutions:**
1. **Database Issues:**
   ```bash
   # Reset database
   docker compose down -v
   docker compose up -d
   ```

2. **Permission Issues:**
   ```bash
   # Fix file permissions
   sudo chown -R 1000:1000 ./data
   ```

3. **Memory Issues:**
   ```bash
   # Increase Docker memory limit
   # Edit Docker Desktop settings or docker-compose.yml
   ```

#### Model Training Fails

**Symptoms:**
- Training endpoint returns error
- Model metrics unavailable
- Predictions return fallback results

**Diagnosis:**
```bash
# Check training logs
docker compose logs backend | grep -i train

# Verify seed data
docker compose exec backend ls -la /app/data/seeds/

# Test feature extraction
docker compose exec backend python -c "from app.pipeline.features import extract_features; print('Features OK')"
```

**Solutions:**
1. **Insufficient Resources:**
   ```bash
   # Increase memory allocation
   docker compose down
   # Edit docker-compose.yml to increase memory limits
   docker compose up -d
   ```

2. **Missing Dependencies:**
   ```bash
   # Rebuild with fresh dependencies
   docker compose build --no-cache backend
   ```

#### Frontend Build Failures

**Symptoms:**
- Frontend container won't start
- Build errors in logs
- TypeScript compilation errors

**Diagnosis:**
```bash
# Check build logs
docker compose logs frontend

# Test local build
cd frontend
npm run build
```

**Solutions:**
1. **Dependency Issues:**
   ```bash
   # Clear and reinstall
   docker compose exec frontend rm -rf node_modules
   docker compose exec frontend npm install
   ```

2. **Environment Variables:**
   ```bash
   # Verify environment variables
   docker compose exec frontend env | grep NEXT_PUBLIC
   ```

### Performance Issues

#### Slow Image Processing

**Symptoms:**
- Scan requests timeout
- High CPU usage
- Memory leaks

**Diagnosis:**
```bash
# Monitor resource usage
docker stats

# Check processing times
curl -w "@curl-format.txt" -F "files=@test.jpg" http://localhost:8000/scans/
```

**Solutions:**
1. **Optimize Image Processing:**
   ```python
   # Reduce max image size in config
   MAX_IMAGE_MB=4  # Reduce from 8MB
   ```

2. **Scale Backend:**
   ```yaml
   # docker-compose.yml
   backend:
     deploy:
       replicas: 2
   ```

#### Database Performance

**Symptoms:**
- Slow scan history loading
- Database locks
- High disk I/O

**Solutions:**
1. **Add Database Indexes:**
   ```sql
   CREATE INDEX idx_scans_created_at ON scans(created_at);
   CREATE INDEX idx_scans_label ON scans(label);
   ```

2. **Implement Pagination:**
   ```bash
   # Use smaller page sizes
   curl "http://localhost:8000/scans/?per_page=10"
   ```

## 🔄 Backup and Recovery

### Backup Strategy

1. **Automated Backups**
   ```bash
   #!/bin/bash
   # backup.sh
   DATE=$(date +%Y%m%d_%H%M%S)
   
   # Backup database
   docker compose exec backend sqlite3 /app/app.db ".backup /tmp/backup.db"
   docker compose cp backend:/tmp/backup.db "./backups/db_${DATE}.db"
   
   # Backup model artifacts
   docker compose cp backend:/app/app/pipeline/artifacts "./backups/models_${DATE}/"
   
   # Compress backups
   tar -czf "backup_${DATE}.tar.gz" "./backups/db_${DATE}.db" "./backups/models_${DATE}/"
   ```

2. **Backup Verification**
   ```bash
   # Test backup integrity
   sqlite3 backup.db "PRAGMA integrity_check;"
   ```

### Recovery Procedures

1. **Database Recovery**
   ```bash
   # Stop services
   docker compose down
   
   # Restore database
   cp backups/db_20240101_120000.db ./data/app.db
   
   # Restart services
   docker compose up -d
   ```

2. **Model Recovery**
   ```bash
   # Restore model artifacts
   docker compose cp backups/models_20240101_120000/ backend:/app/app/pipeline/artifacts/
   
   # Restart backend
   docker compose restart backend
   ```

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Configuration**
   ```nginx
   upstream catalogai_backend {
       server backend1:8000;
       server backend2:8000;
       server backend3:8000;
   }
   ```

2. **Database Scaling**
   - Use PostgreSQL with read replicas
   - Implement connection pooling
   - Consider database sharding for large datasets

### Vertical Scaling

1. **Resource Allocation**
   ```yaml
   # docker-compose.yml
   backend:
     deploy:
       resources:
         limits:
           memory: 2G
           cpus: '1.0'
         reservations:
           memory: 1G
           cpus: '0.5'
   ```

## 🔐 Security Operations

### Security Monitoring

1. **Access Logs**
   ```bash
   # Monitor suspicious activity
   docker compose logs nginx | grep -E "(40[0-9]|50[0-9])"
   ```

2. **Vulnerability Scanning**
   ```bash
   # Scan Docker images
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
     aquasec/trivy image catalogai-backend:latest
   ```

### Security Updates

1. **Regular Updates**
   ```bash
   # Update base images
   docker compose pull
   docker compose up -d --build
   ```

2. **Dependency Updates**
   ```bash
   # Backend dependencies
   cd backend
   pip list --outdated
   
   # Frontend dependencies
   cd frontend
   npm audit
   npm update
   ```

---

This runbook should be updated regularly as the system evolves and new operational procedures are developed.