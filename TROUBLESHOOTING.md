# CredTech Platform Troubleshooting Guide

## "Failed to fetch analytics data" Error

### Quick Fix Steps

1. **Start the platform with sample data**:
   ```bash
   python quick_start.py
   ```

2. **Or manually start services**:
   ```bash
   # Start database
   docker-compose up -d postgres redis
   
   # Wait for database to be ready
   sleep 10
   
   # Populate sample data
   python populate_sample_data.py
   
   # Start API server
   cd api && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   
   # In another terminal, start frontend
   cd frontend && npm install && npm start
   ```

3. **Test API endpoints**:
   ```bash
   python test_api.py
   ```

### Common Issues and Solutions

#### 1. Database Connection Issues

**Symptoms**: 
- "Failed to fetch analytics data"
- API returns 500 errors
- Database connection errors

**Solutions**:
```bash
# Check if database is running
docker-compose ps

# Restart database services
docker-compose down
docker-compose up -d postgres redis

# Check database logs
docker-compose logs postgres
```

#### 2. Empty Database

**Symptoms**:
- API returns empty arrays
- No companies or scores shown
- Analytics charts are empty

**Solutions**:
```bash
# Populate with sample data
python populate_sample_data.py

# Or manually add data via API docs
# Go to http://localhost:8000/docs
```

#### 3. API Server Not Running

**Symptoms**:
- "Network Error" in frontend
- Cannot reach http://localhost:8000
- Connection refused errors

**Solutions**:
```bash
# Check if API is running
curl http://localhost:8000/health

# Start API server manually
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Check for Python dependency issues
python test_setup.py
```

#### 4. Frontend Build Issues

**Symptoms**:
- Frontend won't start
- npm install errors
- React compilation errors

**Solutions**:
```bash
cd frontend

# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Start development server
npm start
```

#### 5. CORS Issues

**Symptoms**:
- "CORS policy" errors in browser console
- API calls blocked by browser

**Solutions**:
- API already has CORS middleware configured
- Check that API is running on port 8000
- Verify frontend proxy configuration in package.json

#### 6. Port Conflicts

**Symptoms**:
- "Port already in use" errors
- Services won't start

**Solutions**:
```bash
# Check what's using the ports
netstat -an | findstr :8000
netstat -an | findstr :3000
netstat -an | findstr :5432

# Kill processes using the ports (Windows)
taskkill /F /PID <process_id>

# Or change ports in configuration files
```

### Verification Steps

1. **Check all services are running**:
   ```bash
   # Database
   docker-compose ps
   
   # API
   curl http://localhost:8000/health
   
   # Frontend
   curl http://localhost:3000
   ```

2. **Test API endpoints**:
   ```bash
   python test_api.py
   ```

3. **Check browser console**:
   - Open browser developer tools (F12)
   - Look for network errors or CORS issues
   - Check console for JavaScript errors

4. **Verify data exists**:
   ```bash
   # Check companies endpoint
   curl http://localhost:8000/companies
   
   # Check dashboard endpoint  
   curl http://localhost:8000/dashboard
   
   # Check analytics endpoint
   curl http://localhost:8000/analytics
   ```

### Environment-Specific Issues

#### Windows
- Use PowerShell or Command Prompt as Administrator
- Ensure Docker Desktop is running
- Check Windows Firewall settings

#### macOS/Linux
- Use `sudo` for Docker commands if needed
- Check that ports aren't blocked by firewall

### Getting Help

If issues persist:

1. **Check logs**:
   ```bash
   # API logs
   cd api && python -m uvicorn main:app --log-level debug
   
   # Database logs
   docker-compose logs postgres
   
   # Frontend logs
   cd frontend && npm start
   ```

2. **Run health check**:
   ```bash
   python health_check.py
   ```

3. **Verify setup**:
   ```bash
   python test_setup.py
   ```

### Success Indicators

When everything is working correctly:

- ✅ http://localhost:8000/health returns `{"status": "healthy"}`
- ✅ http://localhost:8000/companies returns array of companies
- ✅ http://localhost:8000/dashboard returns dashboard data
- ✅ http://localhost:8000/analytics returns analytics data
- ✅ http://localhost:3000 shows the frontend dashboard
- ✅ Analytics page loads without "Failed to fetch" errors
- ✅ Charts and data are displayed correctly