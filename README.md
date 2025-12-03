# OnlyPark - Smart Parking Management System

OnlyPark is a modern parking management application that streamlines parking spot reservations and administration. Built with Flask and Vue.js, it provides a seamless experience for both users and administrators.

## 🚀 Features

- **User Management**: Secure registration and authentication system
- **Real-time Parking**: Browse and reserve available parking spots
- **Admin Dashboard**: Comprehensive analytics and parking lot management
- **Email Notifications**: Automated daily reminders and booking confirmations
- **Analytics**: Visual charts for parking usage and revenue tracking
- **Responsive Design**: Modern UI that works on all devices

## 🛠️ Tech Stack

**Backend:**
- Flask (Python web framework)
- SQLAlchemy (Database ORM)
- Celery (Background task processing)
- Redis (Caching and message broker)
- JWT (Authentication)

**Frontend:**
- Vue.js 3 (JavaScript framework)
- Bootstrap 5 (UI components)
- Chart.js (Data visualization)
- Vite (Build tool)

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Redis Server
- WSL (for Redis on Windows)

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/MAD-2-Vehicle-Parking-App.git
cd MAD-2-Vehicle-Parking-App
```

### 2. Backend Setup
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 3. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```

### 4. Redis Server (WSL/Ubuntu)
```bash
redis-server
redis-cli ping
```

### 5. Background Tasks
Open separate terminals for each:

**Celery Worker:**
```powershell
celery -A app.celery worker -l info -P threads
```

**Celery Beat (Scheduler):**
```powershell
celery -A app.celery beat --loglevel=info
```

## 📱 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Admin Panel**: Login with `admin@admin.com` / `admin`

## 🏗️ Project Structure

```
├── backend/
│   ├── controllers/         # API route handlers
│   ├── models.py           # Database models
│   ├── app.py              # Main application
│   ├── celery_app.py       # Background tasks
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page components
│   │   └── services/       # API services
│   └── package.json        # Node dependencies
└── README.md
```

## 🔧 Key Features

- **JWT Authentication**: Secure user sessions
- **Role-based Access**: Separate user and admin interfaces
- **Real-time Updates**: Live parking availability
- **Email Integration**: Automated notification system
- **Data Analytics**: Usage statistics and revenue reports
- **Responsive Design**: Mobile-friendly interface

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is part of a university coursework assignment.

---

**OnlyPark** - Revolutionizing parking management, one spot at a time.