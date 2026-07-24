# ⚡ PowerPilot AI

> **An AI-powered electricity demand forecasting platform that combines Machine Learning, interactive analytics, and intelligent assistance to help users predict and understand electricity consumption with confidence.**

---
<p align="center">

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?logo=tailwindcss&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white)

</p>

## 📌 Overview

PowerPilot AI is a full-stack web application designed to forecast electricity demand using multiple machine learning algorithms. The platform enables users to upload datasets, compare model performance, visualize predictions through interactive dashboards, and receive AI-powered insights for better decision-making.

The application combines modern web technologies with artificial intelligence to deliver an intuitive and data-driven forecasting experience.

---
# ✨ Features

PowerPilot AI provides a complete end-to-end solution for electricity demand forecasting, combining Machine Learning with modern web technologies.

| 🚀 Feature | 📖 Description |
|------------|----------------|
| 🔐 Secure Authentication | JWT-based user registration and login system. |
| ⚡ Demand Forecasting | Predict electricity consumption using Machine Learning models. |
| 🤖 Multiple ML Models | Compare Linear Regression, Decision Tree, Random Forest, and KNN. |
| 📊 Interactive Dashboard | Visualize predictions through beautiful charts and analytics. |
| 📈 Model Comparison | Evaluate model performance using multiple evaluation metrics. |
| 📁 CSV Dataset Upload | Upload custom datasets for forecasting. |
| 💬 AI Chat Assistant | Ask questions and receive intelligent responses using Google Gemini AI. |
| 📉 Performance Metrics | View MAE, RMSE, and R² scores for every prediction model. |
| 📱 Responsive Interface | Optimized experience across desktop, tablet, and mobile devices. |


---
# 🤖 Machine Learning Models

PowerPilot AI evaluates multiple regression algorithms to identify the best-performing model for electricity demand forecasting.

| Model | Purpose |
|-------|----------|
| 📈 Linear Regression | Baseline prediction model |
| 🌳 Decision Tree | Tree-based regression |
| 🌲 Random Forest | Ensemble learning model |
| 👥 K-Nearest Neighbors (KNN) | Instance-based learning |

### Model Evaluation Metrics

- ✅ R² Score
- ✅ Root Mean Squared Error (RMSE)
- ✅ Mean Absolute Error (MAE)

---

# 🛠 Technology Stack

## 🎨 Frontend

- React
- Vite
- Tailwind CSS
- Recharts
- Axios

---

## ⚙️ Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Pydantic

---

## 🧠 Machine Learning

- Scikit-learn
- Pandas
- NumPy
- Joblib

---

## 🤖 Artificial Intelligence

- Google Gemini API

---
# 🏗️ System Architecture

```mermaid
graph TD

User[User]
Frontend[React + Vite Frontend]
Backend[FastAPI Backend]
Database[(PostgreSQL Database)]
ML[Machine Learning Models]
Gemini[Google Gemini API]
Prediction[Electricity Demand Prediction]
Dashboard[Dashboard & Analytics]

User --> Frontend
Frontend --> Backend
Backend --> Database
Backend --> ML
Backend --> Gemini
ML --> Prediction
Gemini --> Prediction
Prediction --> Dashboard
Dashboard --> User
```
# 🔄 Application Workflow

```mermaid
graph TD

A[Upload Dataset]
B[Data Preprocessing]
C[Train ML Models]
D[Generate Prediction]
E[Evaluate Performance]
F[Dashboard Visualization]
G[AI Assistant]
H[User Insights]

A --> B
B --> C
C --> D
D --> E
E --> F
F --> G
G --> H
```


# 📚 API Documentation

PowerPilot AI uses **FastAPI**, providing automatically generated interactive API documentation.

## Swagger UI

```
http://localhost:8000/docs
```

## ReDoc

```
http://localhost:8000/redoc
```

### Main Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |
| POST | `/predict` | Predict electricity demand |
| POST | `/upload` | Upload dataset |
| POST | `/chat` | AI Assistant |
| GET | `/dashboard` | Dashboard Analytics |
| GET | `/models` | Available ML Models |

---
# ⚙️ Environment Variables

Create a `.env` file inside the backend directory.

```env
DATABASE_URL=postgresql://username:password@localhost:5432/powerpilot_ai

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60

GEMINI_API_KEY=your_google_gemini_api_key
```

> Replace the placeholder values with your own database credentials and API keys.

---
# 🚀 Installation Guide

## Clone Repository

```bash
git clone https://github.com/zehranisar/PowerPilot-AI.git
```

```bash
cd PowerPilot-AI
```

---

## Backend Setup

```bash
cd backend
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Backend

```bash
uvicorn app.main:app --reload
```

---

## Frontend Setup

```bash
cd frontend
```

Install Packages

```bash
npm install
```

Run Frontend

```bash
npm run dev
```

Application will start at

```
http://localhost:5173
```

Backend API

```
http://localhost:8000
```

---
# 🚀 Installation Guide

## Clone Repository

```bash
git clone https://github.com/zehranisar/PowerPilot-AI.git
```

```bash
cd PowerPilot-AI
```

---

## Backend Setup

```bash
cd backend
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Backend

```bash
uvicorn app.main:app --reload
```

---

## Frontend Setup

```bash
cd frontend
```

Install Packages

```bash
npm install
```

Run Frontend

```bash
npm run dev
```

Application will start at

```
http://localhost:5173
```

Backend API

```
http://localhost:8000
```

---
# 📂 Project Structure

```text
PowerPilot-AI
│
├── backend
│   ├── app
│   ├── routers
│   ├── models
│   ├── schemas
│   ├── services
│   ├── utils
│   └── main.py
│
├── frontend
│   ├── src
│   │   ├── components
│   │   ├── pages
│   │   ├── assets
│   │   ├── hooks
│   │   └── services
│   │
│   └── public
│
├── ml
│
├── dataset
│
├── requirements.txt
│
└── README.md
```

---
# 🛣️ Roadmap

## Completed ✅

- User Authentication
- Electricity Demand Forecasting
- Multiple Machine Learning Models
- AI Chat Assistant
- Interactive Dashboard
- Model Comparison
- CSV Dataset Upload
- Performance Metrics

---

## Upcoming 🚀

- Deep Learning (LSTM) Forecasting
- Weather API Integration
- Real-Time Energy Monitoring
- Docker Support
- CI/CD Deployment
- Explainable AI (SHAP)
- Email Reports
- Mobile Responsive Improvements

---
# 🤝 Contributing

Contributions are welcome!

If you would like to improve this project:

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature/your-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push your branch

```bash
git push origin feature/your-feature
```

5. Open a Pull Request

---
# 📄 License

This project is licensed for educational and research purposes.

Feel free to use this project for learning, academic work, and personal development.

---
# 🙏 Acknowledgements

Special thanks to the amazing open-source technologies that made this project possible.

- React
- Vite
- FastAPI
- PostgreSQL
- Scikit-learn
- Tailwind CSS
- Google Gemini AI
- Recharts

---
# 👩‍💻 Developer

## Zehra Nisar

Computer Science Student

Passionate about Artificial Intelligence, Machine Learning, Full Stack Development, and building intelligent software solutions.

### Skills

- Python
- FastAPI
- React
- PostgreSQL
- Machine Learning
- Scikit-learn
- Tailwind CSS
- SQLAlchemy
- Google Gemini AI

### GitHub

https://github.com/zehranisar

---
# ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.

Your support helps improve the project and motivates future development.

---
