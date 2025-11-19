
## 3. Project Documentation (`DOCS.md`)

```markdown
# TUF AvatarTalk - Full Documentation

## 📚 Table of Contents
1. [System Architecture](#-system-architecture)
2. [Development Setup](#-development-setup)
3. [Deployment Guide](#-deployment-guide)
4. [API Reference](#-api-reference)
5. [Troubleshooting](#-troubleshooting)
6. [FAQs](#-faqs)

## 🏗️ System Architecture

### High-Level Overview
[Diagram showing frontend, backend, and third-party services]

### Data Flow
1. User speaks into microphone
2. Frontend streams audio to backend via WebSocket
3. Backend processes audio and generates response
4. Response is streamed back to frontend
5. Frontend plays audio and animates avatar

## 🛠️ Development Setup

### Prerequisites
- Node.js 16+ (Frontend)
- Python 3.9+ (Backend)
- Docker (Optional)

### Local Development
1. Start backend service
2. Start frontend development server
3. Access at `http://localhost:5173`

## 🌐 Deployment Guide

### Backend
[Detailed deployment instructions for various platforms]

### Frontend
[Build and deployment steps]

## 📡 API Reference

### WebSocket API
[Detailed WebSocket protocol documentation]

### REST API
[If applicable]

## 🚨 Troubleshooting

### Common Issues
1. **Microphone Access**
   - Ensure browser has microphone permissions
   - Check console for errors

2. **WebSocket Connection**
   - Verify backend is running
   - Check CORS settings

3. **3D Model Loading**
   - Check browser console for errors
   - Verify model files are in correct location

## ❓ FAQs

### General
**Q: What browsers are supported?**
A: Latest versions of Chrome, Firefox, and Edge.

**Q: How do I update the avatar model?**
A: Replace the model files in `public/models/` and update the import path.

### Development
**Q: How do I add a new animation?**
1. Add animation file to `public/animations/`
2. Import and register in `src/animations/index.js`
3. Use in your component with the `useAnimations` hook
