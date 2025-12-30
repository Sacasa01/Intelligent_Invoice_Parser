"""
API Tests
Unit tests for Document Intelligence API endpoints
"""

from fastapi.testclient import TestClient
from main import app
import pytest
from io import BytesIO

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Document Intelligence API" in response.json()["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_docs_available():
    """Test that Swagger docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_invoice_endpoint_without_file():
    """Test invoice endpoint rejects requests without file"""
    response = client.post("/api/v1/extract/invoice")
    assert response.status_code == 422  # Validation error


def test_invoice_endpoint_wrong_format():
    """Test invoice endpoint rejects non-PDF files"""
    fake_file = BytesIO(b"fake content")
    files = {"file": ("test.txt", fake_file, "text/plain")}
    response = client.post("/api/v1/extract/invoice", files=files)
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_receipt_endpoint_exists():
    """Test receipt endpoint is available"""
    fake_file = BytesIO(b"fake content")
    files = {"file": ("test.txt", fake_file, "text/plain")}
    response = client.post("/api/v1/extract/receipt", files=files)
    # Should return 400 (wrong format), not 404 (not found)
    assert response.status_code == 400


def test_batch_endpoint_exists():
    """Test batch endpoint is available"""
    response = client.post("/api/v1/extract/batch")
    # Should return 422 (validation error), not 404
    assert response.status_code == 422


def test_batch_endpoint_limit():
    """Test batch endpoint enforces file limit"""
    # Create 11 fake files (exceeds limit of 10)
    files = []
    for i in range(11):
        fake_file = BytesIO(b"fake")
        files.append(("files", (f"test{i}.pdf", fake_file, "application/pdf")))
    
    response = client.post("/api/v1/extract/batch", files=files)
    assert response.status_code == 400
    assert "Maximum 10 files" in response.json()["detail"]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])


