"""
Tests for URL validation functionality
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.main import validate_ical_url
import httpx


@pytest.mark.asyncio
async def test_validate_ical_url_valid_format():
    """Test that valid URL format passes basic validation"""
    # Mock successful HTTP response with valid iCal content
    mock_response = AsyncMock()
    mock_response.text = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    mock_response.raise_for_status.return_value = None
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        with patch('icalendar.Calendar.from_ical'):
            is_valid, error = await validate_ical_url("https://example.com/calendar.ics")
    
    assert is_valid == True
    assert error == ""


@pytest.mark.asyncio 
async def test_validate_ical_url_invalid_format():
    """Test that invalid URL format fails validation"""
    is_valid, error = await validate_ical_url("not-a-url")
    
    assert is_valid == False
    assert "Invalid URL format" in error


@pytest.mark.asyncio
async def test_validate_ical_url_not_ical_content():
    """Test that non-iCal content fails validation"""
    mock_response = AsyncMock()
    mock_response.text = "<html><body>This is not iCal</body></html>"
    mock_response.raise_for_status.return_value = None
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        is_valid, error = await validate_ical_url("https://example.com/calendar.ics")
    
    assert is_valid == False
    assert "does not return valid iCal content" in error


@pytest.mark.asyncio
async def test_validate_ical_url_timeout():
    """Test that request timeout is handled properly"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.TimeoutException("timeout")
        is_valid, error = await validate_ical_url("https://slow-example.com/calendar.ics")
    
    assert is_valid == False
    assert "timed out" in error


@pytest.mark.asyncio
async def test_validate_ical_url_http_error():
    """Test that HTTP errors are handled properly"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.HTTPStatusError(
            "404", request=None, response=mock_response
        )
        is_valid, error = await validate_ical_url("https://example.com/missing.ics")
    
    assert is_valid == False
    assert "HTTP error 404" in error


@pytest.mark.asyncio
async def test_validate_ical_url_malformed_ical():
    """Test that malformed iCal content fails validation"""
    mock_response = AsyncMock()
    mock_response.text = "BEGIN:VCALENDAR\nINVALID:CONTENT\nEND:VCALENDAR"
    mock_response.raise_for_status.return_value = None
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        with patch('icalendar.Calendar.from_ical', side_effect=Exception("Invalid iCal")):
            is_valid, error = await validate_ical_url("https://example.com/bad.ics")
    
    assert is_valid == False
    assert "Invalid iCal format" in error