# WHAT DOES THIS FILE DO: Integration tests checking API endpoints for queries streaming, validation, authentication, and health checks.

# ================== IMPORTS ==================
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from app.models.report import StructuredReport
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Verify that research query endpoint returns a valid text/event-stream response.
@pytest.mark.asyncio
async def test_research_endpoint_returns_stream(app_client, test_db, mock_openai):
    """ Verifies successful query triggers text/event-stream SSE output. """
    
    # FLOW-1: Setup Authorization headers and valid search query payload
    headers = {"Authorization": "Bearer test-secret-key"}  # USE: Mock API key header dict
    payload = {"query": "explain artificial intelligence in detail"}  # USE: Valid query > 10 chars
    
    # FLOW-2: Make request using stream context manager and assert response properties
    async with app_client.stream("POST", "/api/v1/research/query", json=payload, headers=headers) as response:  # USE: Context manager for streaming response
        assert response.status_code == 200      # USE: Validate success status
        assert "text/event-stream" in response.headers.get("content-type", "")  # USE: Validate SSE content type
        
        # FLOW-3: Read streaming lines to verify content output is not empty
        lines = []
        async for line in response.aiter_lines():  # USE: Loop over streamed response lines
            if line:
                lines.append(line)
                break
                
        assert len(lines) > 0                   # USE: Verify at least one line was received
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verify that query endpoint rejects requests missing the Authorization header.
@pytest.mark.asyncio
async def test_research_endpoint_requires_auth(app_client):
    """ Verifies request without API key returns 401 Unauthorized status. """
    
    # FLOW-1: Call POST endpoint without any headers and assert 401 response code
    payload = {"query": "explain artificial intelligence"}  # USE: Valid query payload
    response = await app_client.post("/api/v1/research/query", json=payload)  # USE: Trigger post request
    
    assert response.status_code == 401          # USE: Assert unauthorized status code
    assert response.json()["error_code"] == "MISSING_AUTH"  # USE: Assert error code detail
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verify that query endpoint rejects query strings shorter than 10 characters.
@pytest.mark.asyncio
async def test_research_endpoint_validates_query_length(app_client):
    """ Verifies short query validation failure returns 422 status. """
    
    # FLOW-1: Configure valid auth header and a short query payload
    headers = {"Authorization": "Bearer test-secret-key"}  # USE: Mock API key header dict
    payload = {"query": "short"}                # USE: Invalid short query payload
    
    # FLOW-2: Send POST request and assert validation error status
    response = await app_client.post("/api/v1/research/query", json=payload, headers=headers)  # USE: Trigger post request
    
    assert response.status_code == 422          # USE: Assert request validation error status code
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verify that health check liveness probe returns success status metadata.
@pytest.mark.asyncio
async def test_health_endpoint(app_client):
    """ Verifies health check returns 200 OK and status metadata. """
    
    # FLOW-1: Trigger GET check on health endpoint and validate 200 status
    response = await app_client.get("/api/v1/health")  # USE: Request health check
    
    assert response.status_code == 200          # USE: Assert successful response code
    assert response.json()["status"] == "ok"    # USE: Assert status string payload value
# =========== FUNCTION ===========