from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.routers.auth import get_current_user

router = APIRouter()

def get_gemini_response(question: str, user_id: int, db: Session, current_user=None) -> str:
    """Get response from Google Gemini API with comprehensive context"""
    try:
        import google.generativeai as genai
        
        # API key directly in code
        api_key = "AIzaSyBz51AgEhiNBdk-JBLwa_ZM6o9raWi_9eA"
        
        genai.configure(api_key=api_key)
        # Use gemini-2.5-flash (fast and efficient) or gemini-2.5-pro (more capable)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Get user's consumption data for context
        records = db.query(models.ConsumptionRecord).filter(
            models.ConsumptionRecord.user_id == user_id
        ).order_by(models.ConsumptionRecord.created_at.desc()).limit(100).all()
        
        # Get recent chat history for context
        recent_chats = db.query(models.ChatHistory).filter(
            models.ChatHistory.user_id == user_id
        ).order_by(models.ChatHistory.created_at.desc()).limit(5).all()
        
        # Get user's model information
        user_model_perf = db.query(models.ModelPerformance).filter(
            models.ModelPerformance.user_id == user_id
        ).all()
        
        selected_model = None
        if current_user:
            selected_model = current_user.selected_model
        else:
            user_obj = db.query(models.User).filter(models.User.id == user_id).first()
            if user_obj:
                selected_model = user_obj.selected_model
        
        # Build comprehensive context
        context = """You are an expert AI assistant for an Electricity Consumption Forecasting application. 
Your role is to help users understand their electricity consumption patterns, make predictions, and provide insights.

PROJECT CONTEXT:
This is a comprehensive Electricity Forecasting application with the following features:

1. DATA SOURCE MANAGEMENT:
   - Users can choose to use existing data.csv file or upload their own CSV file
   - Data must have columns: datetime, temperature, consumption, is_weekend
   - Files are validated before training

2. MACHINE LEARNING MODELS:
   The application trains FOUR different machine learning models:
   a) Linear Regression: Fast, simple baseline model for linear relationships
   b) Decision Tree Regressor: Interpretable tree-based model, can capture non-linear patterns
   c) Random Forest Regressor: Ensemble method, usually best accuracy, combines multiple decision trees
   d) K-Nearest Neighbors (KNN): Instance-based learning, good for local patterns
   
   All models are trained on user-specific data and stored separately for each user.

3. MODEL COMPARISON & SELECTION:
   - Users can compare all 4 models using performance metrics:
     * R² Score (R-squared): Measures how well model explains variance (0-1, higher is better, 1 = perfect)
     * RMSE (Root Mean Squared Error): Average prediction error in same units as consumption (lower is better)
     * MAE (Mean Absolute Error): Average absolute difference between predictions and actual values (lower is better)
   - Users can view performance charts and select which model to use for predictions
   - Best model (highest R²) is automatically selected by default
   - Selected model is used for all future predictions

4. DASHBOARD FEATURES:
   - Consumption Statistics: Total consumption, average consumption, peak hour, lowest hour
   - Cluster Analysis: Uses KMeans clustering (3 clusters) to identify consumption patterns
   - Model Comparison: Access to compare and select models
   - Quick Actions: Links to predictions, model comparison, and AI chat

5. PREDICTIONS:
   - Uses the user's SELECTED model (not just KNN)
   - Predicts consumption based on:
     * Hour of day (0-23)
     * Temperature (in Celsius)
     * Day type (Weekend or Weekday)
   - Model automatically switches based on user's selection

6. MODEL TRAINING PROCESS:
   - When user chooses data source, models train automatically (existing data) or after upload
   - Training includes: feature engineering (hour extraction, weekend detection), scaling, model training, evaluation
   - Performance metrics are calculated and saved to database
   - Models are saved in user-specific directories: ml/models/user_{user_id}/

7. DATA ANALYSIS:
   - KMeans clustering identifies 3 consumption pattern groups
   - Statistical analysis of consumption patterns
   - Time-based analysis (hourly patterns, weekend vs weekday)

USER'S MODEL INFORMATION:
"""
        
        if user_model_perf:
            context += f"The user has trained {len(user_model_perf)} models:\n"
            for perf in user_model_perf:
                mae_str = f"{perf.mae:.2f}" if perf.mae is not None else "N/A"
                context += f"- {perf.model_name.replace('_', ' ').title()}: R² = {perf.r2_score:.4f} ({(perf.r2_score*100):.2f}%), RMSE = {perf.rmse:.2f}, MAE = {mae_str}\n"
            
            if selected_model:
                context += f"\nCurrently Selected Model: {selected_model.replace('_', ' ').title()}\n"
            else:
                best_model = max(user_model_perf, key=lambda x: x.r2_score)
                context += f"\nBest Model (auto-selected): {best_model.model_name.replace('_', ' ').title()} with R² = {best_model.r2_score:.4f}\n"
        else:
            context += "The user has not trained models yet. They need to choose a data source and train models first.\n"

        context += "\nUSER'S DATA CONTEXT:\n"
        
        if records:
            total = sum(r.consumption for r in records)
            avg = total / len(records)
            peak_hour_records = {}
            for r in records:
                if r.hour not in peak_hour_records:
                    peak_hour_records[r.hour] = []
                peak_hour_records[r.hour].append(r.consumption)
            
            peak_hour = max(peak_hour_records.items(), key=lambda x: sum(x[1])/len(x[1]))[0] if peak_hour_records else None
            lowest_hour = min(peak_hour_records.items(), key=lambda x: sum(x[1])/len(x[1]))[0] if peak_hour_records else None
            
            context += f"""The user has {len(records)} consumption records in the database.
- Total Consumption: {total:.2f} kWh
- Average Consumption: {avg:.2f} kWh per record
- Peak Consumption Hour: {peak_hour}:00 (if available)
- Lowest Consumption Hour: {lowest_hour}:00 (if available)

Recent consumption patterns:
"""
            # Add some sample records
            for r in records[:5]:
                context += f"- Hour {r.hour}:00, Temp {r.temperature}°C, {'Weekend' if r.is_weekend else 'Weekday'}, Consumption: {r.consumption:.2f} kWh\n"
        else:
            context += "The user has no consumption records yet. They can load sample data from data.csv file.\n"
        
        # Add chat history context
        if recent_chats:
            context += "\nRECENT CONVERSATION HISTORY:\n"
            for chat in reversed(recent_chats):  # Show in chronological order
                context += f"User: {chat.question}\nAssistant: {chat.answer}\n\n"
        
        context += """
CAPABILITIES:
You can help with:
1. Explaining all 4 machine learning models (Linear Regression, Decision Tree, Random Forest, KNN)
2. Interpreting model performance metrics (R², RMSE, MAE) and what they mean
3. Helping users understand which model to select and why
4. Explaining consumption patterns and trends
5. Interpreting dashboard statistics
6. Understanding how predictions work with the selected model
7. Explaining clustering results (KMeans with 3 clusters)
8. Providing energy-saving tips based on consumption patterns
9. Answering questions about electricity forecasting concepts
10. Helping users understand their data better
11. Making recommendations based on consumption data and model performance
12. Explaining technical terms (kWh, peak hours, clustering, R², RMSE, MAE, etc.)
13. Guiding users through data source selection and model training
14. Explaining the difference between the 4 models and when to use each
15. Any other questions related to electricity consumption, forecasting, machine learning, or this application

MODEL-SPECIFIC INFORMATION:
- Linear Regression: Best for linear relationships, fast, interpretable coefficients
- Decision Tree: Can capture non-linear patterns, easy to understand, may overfit
- Random Forest: Usually most accurate, handles non-linear patterns well, robust to overfitting
- KNN: Good for local patterns, sensitive to feature scaling, can be slow with large datasets

PERFORMANCE METRICS EXPLANATION:
- R² Score: Proportion of variance explained (0-1). 1.0 = perfect predictions, 0.0 = no better than average
- RMSE: Root Mean Squared Error in same units as consumption. Lower is better. Shows typical prediction error.
- MAE: Mean Absolute Error. Average absolute difference. Lower is better. More intuitive than RMSE.

RESPONSE GUIDELINES:
- Be helpful, clear, and concise
- Use the user's actual data and model information when relevant
- Provide specific examples from their data and model performance when possible
- Explain technical concepts (models, metrics) in simple terms
- If the user asks about something not in their data, explain what they need to do
- When discussing models, mention all 4 models, not just KNN
- Explain which model might be best for their use case based on their performance metrics
- Be friendly and professional
- If you don't know something, admit it rather than guessing
- Always mention that users can compare and select models in the Model Comparison section

CURRENT QUESTION:
"""
        context += f"User: {question}\n\n"
        context += "Please provide a comprehensive, helpful response based on the context above."
        
        response = model.generate_content(context)
        return response.text
    except Exception as e:
        # Fallback response if Gemini fails
        return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}. Please try again later or contact support."

@router.post("/chat", response_model=schemas.ChatResponse)
async def chat(
    request: schemas.ChatRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI assistant using Google Gemini and save to history"""
    try:
        answer = get_gemini_response(request.question, current_user.id, db, current_user)
        
        # Save to chat history
        chat_history = models.ChatHistory(
            user_id=current_user.id,
            question=request.question,
            answer=answer
        )
        db.add(chat_history)
        db.commit()
        db.refresh(chat_history)
        
        return {"answer": answer, "history_id": chat_history.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/chat/history", response_model=list[schemas.ChatHistoryResponse])
async def get_chat_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get chat history for the current user"""
    history = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).order_by(models.ChatHistory.created_at.desc()).limit(limit).all()
    
    return list(reversed(history))  # Return in chronological order (oldest first)

@router.delete("/chat/history/{history_id}")
async def delete_chat_message(
    history_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific chat message"""
    chat = db.query(models.ChatHistory).filter(
        models.ChatHistory.id == history_id,
        models.ChatHistory.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat message not found")
    
    db.delete(chat)
    db.commit()
    
    return {"message": "Chat message deleted successfully"}

@router.delete("/chat/history")
async def clear_chat_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all chat history for the current user"""
    db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).delete()
    db.commit()
    
    return {"message": "Chat history cleared successfully"}

