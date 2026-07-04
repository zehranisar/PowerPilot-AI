# Electricity Forecasting Application

A full-stack web application for electricity consumption forecasting using multiple machine learning models with AI-powered chatbot assistance.

## 🚀 Features

- 🔐 **User Authentication** - Signup, Login, Password Reset
- 📊 **Dashboard** - Consumption statistics, peak hours, cluster analysis
- 🤖 **Multiple ML Models** - Linear Regression, Decision Tree, Random Forest, KNN
- 📈 **Model Comparison** - Compare and select the best performing model
- 🔮 **Predictions** - Predict consumption using selected model
- 📁 **Data Management** - Use existing data or upload your own CSV files
- 💬 **AI Chat Assistant** - Get insights using Google Gemini AI
- 📊 **Performance Metrics** - R² Score, RMSE, MAE for model evaluation

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **JWT** - Authentication
- **scikit-learn** - Machine Learning models
- **Google Gemini API** - AI Chatbot

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Axios** - HTTP client

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL database
- Google Gemini API key (for AI chat)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/habib-u-rahman/Electricity_forcasting_using_different_ML_Model.git
cd Electricity_forcasting_using_different_ML_Model
```

### 2. Database Setup

Create a PostgreSQL database:
```sql
CREATE DATABASE Electricity_forcasting;
```

### 3. Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file in project root:
```env
# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Electricity_forcasting

# JWT Secret Key
SECRET_KEY=your-secret-key-here

# Google Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here
```

3. Generate secret key:
```bash
python generate_secret_key.py
```

4. Run database migrations:
```bash
python backend/scripts/migrate_user_table.py
python backend/scripts/migrate_model_performance.py
```

5. Start backend server:
```bash
python run_server.py
```

Backend will run on `http://localhost:8000`

### 4. Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## 📖 Usage

### First Time Setup

1. **Signup/Login** - Create an account or login
2. **Choose Data Source**:
   - Use existing `data.csv` file (trains automatically)
   - Upload your own CSV file
3. **Train Models** - Models train automatically or after upload
4. **View Dashboard** - See statistics and analyses
5. **Compare Models** - Click "Model Comparison" to see all models
6. **Select Best Model** - Choose the model with best performance
7. **Make Predictions** - Use selected model for predictions
8. **Chat with AI** - Ask questions about your data

### CSV File Format

If uploading your own file, ensure it has these columns:
- `datetime` - Date and time (e.g., "2025-01-01 00:00:00")
- `temperature` - Temperature value (float)
- `consumption` - Consumption value (float)
- `is_weekend` - Optional (boolean or 0/1)

Example:
```csv
datetime,temperature,consumption,is_weekend
2025-01-01 00:00:00,21.3,145.2,False
2025-01-01 01:00:00,20.8,142.6,False
```

## 🤖 Machine Learning Models

The application trains 4 different models:

1. **Linear Regression** - Fast, simple baseline for linear relationships
2. **Decision Tree** - Interpretable, captures non-linear patterns
3. **Random Forest** - Usually best accuracy, ensemble method
4. **K-Nearest Neighbors (KNN)** - Good for local patterns

### Performance Metrics

- **R² Score**: Measures how well model explains variance (0-1, higher is better)
- **RMSE**: Root Mean Squared Error - prediction error in same units (lower is better)
- **MAE**: Mean Absolute Error - average absolute difference (lower is better)

## 📁 Project Structure

```
Electricity_forcasting/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication
│   │   └── routers/             # API routes
│   └── scripts/                 # Migration scripts
├── frontend/
│   └── src/
│       ├── pages/               # React pages
│       ├── components/          # React components
│       └── services/            # API services
├── ml/
│   ├── train_models.py          # Model training
│   └── utils.py                 # Prediction utilities
├── data.csv                     # Sample data
└── requirements.txt             # Python dependencies
```

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Data & Training
- `GET /api/v1/data/training-status` - Get training status
- `POST /api/v1/data/choose-data-source` - Choose data source
- `POST /api/v1/data/upload-data-file` - Upload CSV file
- `POST /api/v1/data/train-model` - Train models
- `GET /api/v1/data/model-comparison` - Get model comparison
- `POST /api/v1/data/select-model` - Select model to use

### Predictions
- `POST /api/v1/predict/knn` - Make prediction
- `GET /api/v1/predict/summary` - Get consumption summary
- `GET /api/v1/predict/clusters` - Get consumption clusters

### Chat
- `POST /api/v1/chat` - Chat with AI assistant

## 📝 License

This project is open source and available for educational purposes.

## 👤 Author

**Habib U Rahman**

## 🙏 Acknowledgments

- scikit-learn for machine learning models
- FastAPI for the web framework
- React for the frontend framework
- Google Gemini for AI chat capabilities

