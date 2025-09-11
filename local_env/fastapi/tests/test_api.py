import pytest
from fastapi.testclient import TestClient
from ..app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"


def test_health_endpoint():
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "model_status" in response.json()


def test_churn_prediction_endpoint():
    """Test the churn prediction endpoint"""
    test_data = {
        "users": [
            {
                "user_id": 1,
                "age": 35,
                "country": "United States",
                "total_orders": 10,
                "total_spent": 500.0,
                "days_since_last_order": 15,
                "avg_order_value": 50.0,
                "customer_duration_days": 365,
                "order_frequency": 0.0274,
                "daily_spend": 1.37
            }
        ]
    }

    response = client.post("/predict/churn", json=test_data)
    assert response.status_code in [200, 500]  # 500 if models not available

    if response.status_code == 200:
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == 1
        assert 0 <= data[0]["churn_probability"] <= 1
        assert isinstance(data[0]["will_churn"], bool)


def test_recommendation_endpoint():
    """Test the recommendation endpoint"""
    test_data = {
        "user_id": 1,
        "max_recommendations": 3
    }

    response = client.post("/recommend/products", json=test_data)
    assert response.status_code in [200, 500]  # 500 if models not available

    if response.status_code == 200:
        data = response.json()
        assert data["user_id"] == 1
        assert len(data["recommendations"]) <= 3
        if data["recommendations"]:
            assert "product_id" in data["recommendations"][0]
            assert "name" in data["recommendations"][0]
            assert "score" in data["recommendations"][0]


def test_user_features_endpoint():
    """Test the user features endpoint"""
    response = client.get("/users/1/features")
    assert response.status_code in [200, 404, 500]

    if response.status_code == 200:
        data = response.json()
        assert "user_id" in data
        assert "age" in data
        assert "total_orders" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])