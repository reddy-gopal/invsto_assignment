# tests/test_api_validation.py
import unittest
from app.schemas import StockDataSchema
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

class TestAPISchemaAndValidation(unittest.TestCase):
    def test_pydantic_validation_fail(self):
        # invalid types: open is string -> should raise
        with self.assertRaises(ValidationError):
            StockDataSchema(
                datetime="2025-10-15T09:45:00",
                open="not-a-number",
                high=10.0,
                low=9.0,
                close=9.5,
                volume=100
            )

    @patch("app.main.db")
    def test_post_data_endpoint_validation(self, mock_db):
        # mock the DB create to be an async function returning sample
        mock_db.stockdata.create = AsyncMock(return_value={"id": 999, "datetime": "2025-10-15T09:45:00", "open": 1.0, "high":2.0, "low":0.9, "close":1.5, "volume":100})
        payload = {
            "datetime": "2025-10-15T09:45:00",
            "open": 1.0,
            "high": 2.0,
            "low": 0.9,
            "close": 1.5,
            "volume": 100
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("message", body)
        self.assertEqual(body["message"], "Record added successfully")
        self.assertIn("data", body)

if __name__ == "__main__":
    unittest.main()
