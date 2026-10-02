from http.client import responses
from fastapi.testclient import TestClient
from src.api.main import app
client=TestClient(app)
def test_root():
    response=client.get("/")
    assert response.status_code==200
    assert response.json()=={"message":"Demand Forecasting API is running"}

def test_forecast():
    response=client.post(
        "/forecast",
        json={
            "item_id":"HOBBIES_1_001",
            "store_id":"CA_1",
            "start_date":"2016-04-01"
        }
    )
    assert response.status_code == 200

    data = response.json()

    assert data["item_id"] == "HOBBIES_1_001"
    assert data["store_id"] == "CA_1"
    assert data["forecast_next_7_days"] >= 0
    assert data["safety_stock"] >= 0
    assert data["reorder_point"] >= 0

# def test_invalid_date():
#     response = client.post(
#         "/forecast",
#         json={
#             "item_id": "HOBBIES_1_001",
#             "store_id": "CA_1",
#             "start_date": "banana"
#         }
#     )

#     assert response.status_code == 422


def test_forecast_invalid_date_range():
    response = client.post(
        "/forecast",
        json={
            "item_id": "HOBBIES_1_001",
            "store_id": "CA_1",
            "start_date": "2025-01-01"
        }
    )

    assert response.status_code == 400


def test_invalid_item_store():
    response = client.post(
        "/forecast",
        json={
            "item_id": "HOBBIES_1_001",
            "store_id": "INVALID",
            "start_date": "2016-04-01"
        }
    )

    assert response.status_code == 404

def test_empty_item_id():
    response = client.post(
        "/forecast",
        json={
            "item_id": "",
            "store_id": "CA_1",
            "start_date": "2016-04-01"
        }
    )

    assert response.status_code == 422