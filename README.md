# 🎨 BlusWipe - AI Background Remover

**Developed by Eleblu Nunana**

A powerful AI-powered background removal tool built with Python and deployed on Netlify. Remove backgrounds from images instantly using state-of-the-art U2Net deep learning model.

## ✨ Features

- 🤖 **AI-Powered**: Uses U2Net neural network for precise background removal
- 🚀 **Serverless**: Deployed on Netlify Functions for scalability
- 📱 **Responsive**: Works perfectly on desktop and mobile devices
- 🎯 **Easy to Use**: Simple drag-and-drop interface
- 💨 **Fast Processing**: Optimized for quick image processing
- 🔒 **Secure**: No image storage, processed in memory only

## 🏗️ Project Structure

```
BlusWipe-Production/
├── dist/                    # Frontend assets (static files)
│   └── index.html          # Main web interface
├── netlify/
│   └── functions/          # Serverless functions
│       ├── remove-background.py  # Main AI processing function
│       ├── health.py       # Health check endpoint
│       └── background_remover.py # AI model utilities
├── models/                 # AI model cache directory
├── outputs/               # Processed images output
├── uploads/               # Temporary upload directory
├── netlify.toml          # Netlify deployment configuration
├── requirements.txt      # Python dependencies
├── runtime.txt          # Python version specification
└── README.md           # This file
```

## 🚀 Deployment Guide

### Prerequisites

- Python 3.11+
- Node.js 18+ (for Netlify CLI)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/BlusMotif/BlusWipe.git
   cd BlusWipe-Production
   ```

2. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally**
   ```bash
   netlify dev
   ```

5. **Access the application**
   - Frontend: http://localhost:8888
   - Functions: http://localhost:8888/.netlify/functions/

### Production Deployment

#### Option 1: Netlify Web UI

1. **Connect Repository**
   - Go to [Netlify Dashboard](https://app.netlify.com)
   - Click "New site from Git"
   - Connect your GitHub repository

2. **Configure Build Settings**
   - Build command: `echo 'Static build complete'`
   - Publish directory: `dist`
   - Functions directory: `netlify/functions`

3. **Deploy**
   - Click "Deploy site"
   - Wait for build to complete

#### Option 2: Netlify CLI

1. **Login to Netlify**
   ```bash
   netlify login
   ```

2. **Initialize site**
   ```bash
   netlify init
   ```

3. **Deploy**
   ```bash
   netlify deploy --prod
   ```

### Environment Variables

No environment variables required for basic deployment. All dependencies are managed through `requirements.txt`.

## 🔧 Configuration

### netlify.toml

The `netlify.toml` file contains optimized settings for:
- Function timeout: 300 seconds
- Memory allocation: 1024 MB
- Cache headers for performance
- Security headers
- API routing

### requirements.txt

Optimized dependencies for Netlify Functions:
- **Pillow**: Image processing
- **rembg**: AI background removal
- **torch**: PyTorch for model execution
- **onnxruntime**: ONNX model runtime
- **numpy**: Numerical computing

## 📱 Usage

1. **Visit the deployed site**
2. **Upload an image**:
   - Click "Choose File" or drag & drop
   - Supports: JPG, PNG, WEBP
   - Max size: 10MB

3. **Process image**:
   - Click "Remove Background"
   - Wait for AI processing

4. **Download result**:
   - Click "Download Processed Image"
   - Image saved as PNG with transparency

## 🛠️ Technical Details

### AI Model
- **Architecture**: U2Net (U^2-Net)
- **Purpose**: Salient object detection and background removal
- **Performance**: Optimized for accuracy and speed
- **Format**: ONNX for cross-platform compatibility

### Backend Architecture
- **Framework**: Netlify Functions (Python)
- **Processing**: In-memory image handling
- **Storage**: No persistent storage (privacy-focused)
- **Scaling**: Auto-scaling serverless functions

### Frontend Technology
- **Framework**: Vanilla JavaScript (no dependencies)
- **Styling**: Bootstrap 5 + Custom CSS
- **Features**: Responsive design, drag-drop, progress indicators

## 🚨 Troubleshooting

### Common Issues

1. **Cold Start Delays**
   - First request may take 10-30 seconds
   - Subsequent requests are faster
   - This is normal for serverless functions

2. **Large Image Processing**
   - Images > 5MB may take longer
   - Consider resizing before upload
   - Maximum recommended: 10MB

3. **Function Timeout**
   - Processing timeout: 5 minutes
   - Very large/complex images may timeout
   - Try with smaller images

### Development Issues

1. **Dependencies not installing**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

2. **Local development not working**
   ```bash
   netlify dev --live
   ```

3. **Functions not deploying**
   - Check Python version (must be 3.11)
   - Verify file structure matches documentation
   - Check Netlify build logs

## 📞 Support

- **Developer**: Eleblu Nunana
- **Issues**: GitHub Issues
- **Documentation**: This README

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Made with ❤️ by Eleblu Nunana**
