"""
Tests for Query Tagger service.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import FinancialTag, TagRequest
from app.tagger.prompts import build_messages, is_valid_tag


client = TestClient(app)


class TestAPI:
    """Test API endpoints."""
    
    def test_tag_endpoint_exists(self):
        """Test that /tag endpoint exists."""
        response = client.post("/tag", json={"query": "test"})
        # Should not return 404
        assert response.status_code != 404


class TestModels:
    """Test Pydantic models."""
    
    def test_financial_tag_values(self):
        assert FinancialTag.LOAN.value == "loan"
        assert len(FinancialTag.valid_tags()) == 7
    
    def test_tag_request_validation(self):
        req = TagRequest(query="I need a loan")
        assert req.query == "I need a loan"
        assert req.include_reasoning is False


class TestPrompts:
    """Test prompt building."""
    
    def test_build_messages(self):
        messages = build_messages("I need a home loan")
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "I need a home loan" in messages[1]["content"]
    
    def test_is_valid_tag(self):
        assert is_valid_tag("loan") is True
        assert is_valid_tag("investment") is True
        assert is_valid_tag("invalid") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])