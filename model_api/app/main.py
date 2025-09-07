from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import mlflow.pyfunc
import logging
from sqlalchemy import create_engine
from datetime import datetime

# Add at the top
from config import settings

# Update MLflow tracking URI
import mlflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="E-Commerce ML API",
    description="API for serving churn prediction and recommendation models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)

# Update database connection
def get_db_connection():
    return create_engine(settings.DB_URL)

# MLflow model loading
def load_model(model_name, stage="Production"):
    try:
        model_uri = f"models:/{model_name}/{stage}"
        model = mlflow.pyfunc.load_model(model_uri)
        logger.info(f"Loaded model {model_name} from {model_uri}")
        return model
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")


# Load models at startup
@app.lifespan("startup")
async def startup_event():
    # These will be loaded on first request to avoid startup failures if models aren't available
    logger.info("API startup completed")


# Pydantic models for request/response validation
class UserData(BaseModel):
    user_id: int = Field(..., description="Unique user identifier")
    age: int = Field(..., ge=18, le=100, description="User age")
    country: str = Field(..., min_length=2, max_length=50, description="User country")
    total_orders: int = Field(..., ge=0, description="Total orders by user")
    total_spent: float = Field(..., ge=0, description="Total amount spent by user")
    days_since_last_order: int = Field(..., ge=0, description="Days since last order")
    avg_order_value: float = Field(..., ge=0, description="Average order value")
    customer_duration_days: int = Field(..., ge=0, description="Customer duration in days")
    order_frequency: float = Field(..., ge=0, description="Order frequency (orders per day)")
    daily_spend: float = Field(..., ge=0, description="Daily spending amount")


class ChurnPredictionRequest(BaseModel):
    users: List[UserData]


class ChurnPredictionResponse(BaseModel):
    user_id: int
    churn_probability: float
    will_churn: bool
    timestamp: datetime


class RecommendationRequest(BaseModel):
    user_id: int = Field(..., description="User ID for recommendations")
    max_recommendations: int = Field(5, ge=1, le=20, description="Maximum number of recommendations")


class ProductRecommendation(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
    score: float


class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[ProductRecommendation]
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    model_status: dict
    timestamp: datetime


# API endpoints
@app.get("/")
async def root():
    return {"message": "E-Commerce ML API", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    model_status = {}

    try:
        # Try to load models to check their status
        load_model("churn_prediction_model", "Production")
        model_status["churn_model"] = "available"
    except Exception as e:
        model_status["churn_model"] = f"error: {str(e)}"

    try:
        load_model("product_recommendation_model", "Production")
        model_status["recommendation_model"] = "available"
    except Exception as e:
        model_status["recommendation_model"] = f"error: {str(e)}"

    return HealthResponse(
        status="healthy",
        model_status=model_status,
        timestamp=datetime.now()
    )


@app.post("/predict/churn", response_model=List[ChurnPredictionResponse])
async def predict_churn(request: ChurnPredictionRequest):
    """Predict churn probability for users"""
    try:
        # Load model
        model = load_model("churn_prediction_model", "Production")

        # Prepare features DataFrame
        user_data = [user.model_dump() for user in request.users]
        features_df = pd.DataFrame(user_data)

        # Make predictions
        predictions = model.predict(features_df)
        probabilities = model.predict_proba(features_df)[:, 1]  # Probability of churn (class 1)


        # Prepare response
        responses = []
        for i, user in enumerate(request.users):
            responses.append(ChurnPredictionResponse(
                user_id=user.user_id,
                churn_probability=float(probabilities[i]),
                will_churn=bool(predictions[i] > 0.5),  # Using 0.5 as threshold
                timestamp=datetime.now()
            ))

        return responses

    except Exception as e:
        logger.error(f"Churn prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/recommend/products", response_model=RecommendationResponse)
async def recommend_products(request: RecommendationRequest):
    """Get product recommendations for a user"""
    try:
        # Load recommendation model
        model = load_model("product_recommendation_model", "Production")

        # Get database connection
        db_engine = get_db_connection()

        # Get user interaction history
        user_interactions_query = f"""
            SELECT product_id, COUNT(*) as interaction_count
            FROM sales 
            WHERE user_id = {request.user_id}
            GROUP BY product_id
        """
        user_interactions = pd.read_sql_query(user_interactions_query, db_engine)
        interacted_products = user_interactions['product_id'].tolist()

        # Get all products
        products_query = "SELECT product_id, name, category, price FROM products"
        products_df = pd.read_sql_query(products_query, db_engine)

        # Generate recommendations
        recommendations = []
        for _, product in products_df.iterrows():
            if product['product_id'] not in interacted_products:
                # Predict rating for this user-product pair
                prediction = model.predict(request.user_id, product['product_id'])
                recommendations.append({
                    'product_id': product['product_id'],
                    'name': product['name'],
                    'category': product['category'],
                    'price': float(product['price']),
                    'score': prediction.est
                })

        # Sort by score and get top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        top_recommendations = recommendations[:request.max_recommendations]

        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=top_recommendations,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@app.get("/users/{user_id}/features")
async def get_user_features(user_id: int):
    """Get pre-calculated features for a specific user"""
    try:
        db_engine = get_db_connection()

        query = f"""
        WITH user_metrics AS (
            SELECT 
                u.user_id,
                u.country,
                u.age,
                COUNT(s.sale_id) AS total_orders,
                COALESCE(SUM(s.sale_amount), 0) AS total_spent,
                MIN(s.sale_date) AS first_order_date,
                MAX(s.sale_date) AS last_order_date,
                EXTRACT(DAY FROM NOW() - MAX(s.sale_date)) AS days_since_last_order,
                COALESCE(AVG(s.sale_amount), 0) AS avg_order_value,
                EXTRACT(DAY FROM NOW() - MIN(s.sale_date)) AS customer_duration_days,
                CASE 
                    WHEN EXTRACT(DAY FROM NOW() - MIN(s.sale_date)) > 0 
                    THEN COUNT(s.sale_id) / EXTRACT(DAY FROM NOW() - MIN(s.sale_date)) 
                    ELSE 0 
                END AS order_frequency,
                CASE 
                    WHEN EXTRACT(DAY FROM NOW() - MIN(s.sale_date)) > 0 
                    THEN COALESCE(SUM(s.sale_amount), 0) / EXTRACT(DAY FROM NOW() - MIN(s.sale_date)) 
                    ELSE 0 
                END AS daily_spend
            FROM users u
            LEFT JOIN sales s ON u.user_id = s.user_id
            WHERE u.user_id = {user_id}
            GROUP BY u.user_id, u.country, u.age
        )
        SELECT * FROM user_metrics
        """

        user_features = pd.read_sql_query(query, db_engine)

        if user_features.empty:
            raise HTTPException(status_code=404, detail="User not found")

        return user_features.iloc[0].to_dict()

    except Exception as e:
        logger.error(f"Error getting user features: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user features: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)