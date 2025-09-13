"""
Tests for URL validation functionality - Functional approach
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.data.http import validate_ical_url_http
from app.data.calendar import is_valid_url_format, is_valid_ical_content
import httpx


@pytest.mark.asyncio
async def test_validate_ical_url_valid_format():
    """Test that valid URL format passes basic validation"""
    # Mock successful HTTP response with valid iCal content
    mock_response = AsyncMock()
    mock_response.text = "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nEND:VEVENT\nEND:VCALENDAR"
    mock_response.status_code = 200
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        is_valid, message = await validate_ical_url_http("https://example.com/calendar.ics")
    
    assert is_valid == True
    assert message == "Valid iCal URL"


@pytest.mark.asyncio 
async def test_validate_ical_url_invalid_format():
    """Test that invalid URL format fails validation"""
    is_valid, message = await validate_ical_url_http("not-a-url")
    
    assert is_valid == False
    assert "Invalid URL format" in message


@pytest.mark.asyncio
async def test_validate_ical_url_not_ical_content():
    """Test that non-iCal content fails validation"""
    mock_response = AsyncMock()
    mock_response.text = "<html><body>This is not iCal</body></html>"
    mock_response.status_code = 200
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        is_valid, message = await validate_ical_url_http("https://example.com/calendar.ics")
    
    assert is_valid == False
    assert "Not a valid iCal file" in message


@pytest.mark.asyncio
async def test_validate_ical_url_timeout():
    """Test that request timeout is handled properly"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.TimeoutException("timeout")
        is_valid, message = await validate_ical_url_http("https://slow-example.com/calendar.ics")
    
    assert is_valid == False
    assert "Request timeout" in message


@pytest.mark.asyncio
async def test_validate_ical_url_http_error():
    """Test that HTTP errors are handled properly"""
    mock_response = AsyncMock()
    mock_response.status_code = 404
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        is_valid, message = await validate_ical_url_http("https://example.com/missing.ics")
    
    assert is_valid == False
    assert "HTTP 404" in message