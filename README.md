# MediaVerify

A comprehensive media verification system with Flutter frontend and FastAPI backend.

## 📋 System Overview

MediaVerify consists of two main components:

- Flutter mobile application (client)
- FastAPI backend server

## 🚀 Getting Started

### Prerequisites

#### Flutter App

- Flutter SDK (>=3.0.0)
- Dart SDK (>=3.0.0)
- An IDE (VS Code, Android Studio, or IntelliJ)
- Git

#### Backend Server

- Python 3.8+
- MongoDB
- AWS Account with S3 bucket
- Git

### 📥 Installation

#### 1. Clone the Repository

```bash
git clone [your-repository-url]
cd MediaVerify
```

#### 2. Backend Setup (Server)

1. Navigate to server directory and set up Python environment:

```bash
cd server
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

2. Install server dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` file in the server directory:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=user_management

# JWT
SECRET_KEY=your-secret-key-here  # Generate using: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=your-region
AWS_S3_BUCKET=your-bucket-name
```

4. Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at:

- API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

#### 3. Flutter App Setup (Client)

1. Navigate to app directory:

```bash
cd app
```

2. Install Flutter dependencies:

```bash
flutter pub get
```

3. Create `.env` file in the app root directory:

```env
API_BASE_URL=http://localhost:8000
```

4. Run the Flutter app:

```bash
# For development
flutter run

# For specific platform
flutter run -d android
flutter run -d ios
flutter run -d chrome
```

## 📱 App Features

### Authentication Screens

- **Login Screen** (`/login`): User authentication screen
- **Register Screen** (`/register`): New user registration

### User Screens

- **User Home Screen** (`/userHome`): Dashboard for regular users
- **Upload Screen** (`/upload`): Media upload functionality
  - Supports image uploads (JPG, PNG, GIF)
  - Supports audio uploads (MP3, WAV, OGG)

### Admin Screens

- **Admin Home Screen** (`/adminHome`): Dashboard for administrators
  - Media approval workflow
  - User management
  - System monitoring

## 🔧 Services

### Client Services

- **Authentication Services** (`auth_services.dart`)
  - User authentication
  - Session management
- **User Services** (`user_service.dart`)
  - Profile management
- **Admin Services** (`admin_service.dart`)
  - Administrative functions
- **Storage Services** (`storage_services.dart`)
  - Media file handling
- **API Configuration** (`api_config.dart`)
  - API integration

### Server Features

- User Authentication with JWT
- User Profile Management
- Media Upload and Management
- Admin Approval System
- S3 Integration for File Storage
- MongoDB Database
- OpenAPI Documentation

## 🏗️ Project Structure

```
MediaVerify/
├── app/                    # Flutter application
│   ├── lib/
│   │   ├── config/        # Configuration files
│   │   ├── models/        # Data models
│   │   ├── screens/       # UI screens
│   │   ├── services/      # Business logic
│   │   └── widgets/       # UI components
│   └── pubspec.yaml       # Flutter dependencies
│
└── server/                 # FastAPI backend
    ├── app/
    │   ├── routes/        # API endpoints
    │   ├── models/        # Data models
    │   └── services/      # Business logic
    ├── requirements.txt    # Python dependencies
    └── .env               # Server configuration
```

## 🔒 Security Notes

1. Never commit `.env` files to version control
2. Use HTTPS in production
3. Regularly rotate JWT secret keys
4. Configure proper CORS policies
5. Set up appropriate S3 bucket permissions
6. Use secure MongoDB configuration

## 🛠️ Technical Requirements

- Flutter SDK: >=3.0.0
- Dart SDK: >=3.0.0
- Python: >=3.8
- MongoDB: >=4.4
- Dependencies are managed in respective dependency files

## 📝 Development Notes

- The app uses Material Design
- Implements secure authentication
- Features real-time media status updates
- Includes admin approval workflow
- Uses S3 for scalable media storage
