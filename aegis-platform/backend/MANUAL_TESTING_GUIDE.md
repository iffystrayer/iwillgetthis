# Manual Testing Guide - Aegis Platform

## 🚀 Getting Started with Manual Testing

### Step 1: Start the Development Server

From the backend directory, run:

```bash
# Activate virtual environment
source aegis_env/bin/activate

# Start the server
python start_server.py
```

**Expected Output:**
```
🚀 Starting Aegis Risk Management Platform...
============================================================
🌐 Server URL: http://127.0.0.1:8000
📚 API Documentation: http://127.0.0.1:8000/docs
📖 ReDoc Documentation: http://127.0.0.1:8000/redoc
🔍 OpenAPI Spec: http://127.0.0.1:8000/openapi.json
============================================================
✅ Server starting... Press CTRL+C to stop
```

### Step 2: Verify Server is Running

Open your web browser and navigate to: **http://127.0.0.1:8000**

You should see a JSON response:
```json
{
  "message": "Welcome to Aegis Risk Management Platform",
  "version": "1.0.0",
  "status": "operational",
  "timestamp": "2025-08-03T22:30:00Z"
}
```

---

## 📚 Interactive API Documentation

### Swagger UI (Recommended for Testing)
**URL:** http://127.0.0.1:8000/docs

This provides an interactive interface where you can:
- View all available endpoints
- Test API calls directly in the browser
- See request/response formats
- Execute API calls with real data

### ReDoc Documentation
**URL:** http://127.0.0.1:8000/redoc

Clean, readable API documentation for reference.

---

## 🧪 Manual Testing Scenarios

### Test 1: Basic Health Checks

#### 1.1 Root Endpoint
- **URL:** `GET http://127.0.0.1:8000/`
- **Expected:** Welcome message with platform info
- **Browser Test:** Just visit the URL

#### 1.2 Health Check
- **URL:** `GET http://127.0.0.1:8000/health`
- **Expected:** `{"status": "healthy", "timestamp": "..."}`

#### 1.3 API Status
- **URL:** `GET http://127.0.0.1:8000/api/v1/status`
- **Expected:** Detailed system status information

### Test 2: API Documentation Access

#### 2.1 OpenAPI Specification
- **URL:** `GET http://127.0.0.1:8000/openapi.json`
- **Expected:** Complete OpenAPI JSON specification
- **Test:** Should return valid JSON with all endpoint definitions

#### 2.2 Interactive Documentation
- **URL:** http://127.0.0.1:8000/docs
- **Test:** Page loads with interactive API explorer
- **Actions:** Try expanding different endpoint sections

### Test 3: Core Business Endpoints

#### 3.1 Asset Management
```bash
# List all assets (will require auth in full version)
curl -X GET "http://127.0.0.1:8000/api/v1/assets"

# Get asset categories
curl -X GET "http://127.0.0.1:8000/api/v1/assets/categories"
```

#### 3.2 Risk Management
```bash
# List risks
curl -X GET "http://127.0.0.1:8000/api/v1/risks"

# Get risk dashboard
curl -X GET "http://127.0.0.1:8000/api/v1/risks/dashboard"
```

#### 3.3 Dashboard Overview
```bash
# Get overview dashboard
curl -X GET "http://127.0.0.1:8000/api/v1/dashboards/overview"
```

---

## 🔧 Testing with Swagger UI

### Step 1: Access Swagger UI
Navigate to: http://127.0.0.1:8000/docs

### Step 2: Test Basic Endpoints

1. **Find the "Health Check" section**
   - Click on `GET /health`
   - Click "Try it out"
   - Click "Execute"
   - Verify you get a 200 response

2. **Test Asset Categories**
   - Find `GET /api/v1/assets/categories`
   - Click "Try it out"
   - Click "Execute"
   - Should return list of asset categories

3. **Test Dashboard Overview**
   - Find `GET /api/v1/dashboards/overview`
   - Click "Try it out"
   - Click "Execute"
   - Should return dashboard data

### Step 3: Test Error Handling

1. **Test Invalid Endpoint**
   - Manually navigate to: http://127.0.0.1:8000/invalid-endpoint
   - Should return 404 error with proper format

2. **Test Malformed Requests**
   - In Swagger UI, find a POST endpoint
   - Try sending invalid JSON data
   - Verify proper error responses

---

## 🛠️ Advanced Manual Testing

### Using cURL Commands

#### Basic GET Requests
```bash
# Health check
curl -X GET "http://127.0.0.1:8000/health" -H "accept: application/json"

# Assets list
curl -X GET "http://127.0.0.1:8000/api/v1/assets" -H "accept: application/json"

# Risk dashboard
curl -X GET "http://127.0.0.1:8000/api/v1/risks/dashboard" -H "accept: application/json"
```

#### Test with Different Content Types
```bash
# Request with JSON content type
curl -X GET "http://127.0.0.1:8000/api/v1/assets/categories" \
  -H "accept: application/json" \
  -H "Content-Type: application/json"
```

### Using Postman

1. **Import OpenAPI Spec**
   - Open Postman
   - Import → URL
   - Enter: http://127.0.0.1:8000/openapi.json
   - Creates full collection of endpoints

2. **Test Collections**
   - Use the generated collection to test all endpoints
   - Verify response formats and status codes

---

## 🔍 What to Look For During Testing

### 1. Response Format Consistency
All responses should follow this format:
```json
{
  "data": { ... },
  "message": "Success message",
  "status": "success",
  "timestamp": "2025-08-03T22:30:00Z",
  "version": "1.0.0"
}
```

### 2. HTTP Status Codes
- **200**: Successful GET requests
- **201**: Successful POST requests (resource created)
- **400**: Bad request (invalid input)
- **401**: Unauthorized (missing/invalid auth)
- **404**: Not found
- **422**: Validation error
- **500**: Server error

### 3. Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": [...]
  },
  "status": "error",
  "timestamp": "2025-08-03T22:30:00Z"
}
```

### 4. Performance Indicators
- Response times should be < 3 seconds for most endpoints
- Dashboard endpoints may take up to 5 seconds
- No timeout errors or connection issues

---

## 🐛 Common Issues and Troubleshooting

### Issue 1: Server Won't Start
**Error:** `ModuleNotFoundError` or import errors

**Solution:**
```bash
# Make sure virtual environment is activated
source aegis_env/bin/activate

# Install missing dependencies
pip install fastapi uvicorn sqlalchemy pydantic
```

### Issue 2: Port Already in Use
**Error:** `Address already in use`

**Solution:**
```bash
# Kill existing process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python start_server.py --port 8001
```

### Issue 3: 404 Errors on Valid Endpoints
**Possible Causes:**
- Server not fully started
- Wrong URL format
- Missing trailing slashes

**Check:**
- Wait for server to fully initialize
- Verify URL spelling and format
- Check server logs for errors

### Issue 4: CORS Issues in Browser
**Error:** CORS policy blocking requests

**Solution:** Use Swagger UI or curl instead of browser JavaScript for testing

---

## 📋 Manual Testing Checklist

### Basic Functionality ✓
- [ ] Server starts without errors
- [ ] Health endpoint responds correctly
- [ ] Root endpoint returns welcome message
- [ ] OpenAPI documentation loads properly
- [ ] Swagger UI is accessible and functional

### API Endpoints ✓
- [ ] Asset management endpoints respond
- [ ] Risk management endpoints respond
- [ ] Dashboard endpoints return data
- [ ] Analytics endpoints are accessible
- [ ] Training management endpoints respond

### Error Handling ✓
- [ ] 404 errors for invalid endpoints
- [ ] Proper error message format
- [ ] Validation errors for invalid input
- [ ] Graceful handling of edge cases

### Performance ✓
- [ ] Response times under 3 seconds
- [ ] No timeout errors
- [ ] Server handles multiple concurrent requests
- [ ] Memory usage remains stable

### Documentation ✓
- [ ] Swagger UI shows all endpoints
- [ ] ReDoc documentation is complete
- [ ] OpenAPI spec is valid JSON
- [ ] Endpoint descriptions are clear

---

## 🎯 Next Steps After Manual Testing

1. **Document Issues Found**
   - Create issue list with details
   - Include steps to reproduce
   - Note expected vs actual behavior

2. **Performance Testing**
   - Test with multiple simultaneous requests
   - Monitor response times under load
   - Check memory and CPU usage

3. **Integration Testing**
   - Test workflows end-to-end
   - Verify data consistency
   - Test business logic flows

4. **User Experience Testing**
   - Verify API usability
   - Check documentation clarity
   - Test error message helpfulness

---

## 📞 Need Help?

If you encounter issues during manual testing:

1. **Check Server Logs:** Look at terminal output for error messages
2. **Verify Environment:** Ensure virtual environment is active
3. **Check Dependencies:** Run `pip list` to verify installations
4. **Review Documentation:** Check endpoint documentation in Swagger UI
5. **Test Basic Endpoints First:** Start with `/health` and work up

**Happy Testing! 🚀**