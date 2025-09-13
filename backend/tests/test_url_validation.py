"""
Tests for URL validation functionality - Updated for refactored services
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.calendar import CalendarService
from app.storage.persistence import PersistentStore
import httpx


@pytest.fixture
def calendar_service():
    """Create a calendar service for testing"""
    store = PersistentStore(data_dir="/tmp/test_store")
    return CalendarService(store)


@pytest.mark.asyncio
async def test_validate_ical_url_valid_format(calendar_service):
    """Test that valid URL format passes basic validation"""
    # Mock successful HTTP response with valid iCal content
    mock_response = AsyncMock()
    mock_response.text = "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nEND:VEVENT\nEND:VCALENDAR"
    mock_response.status_code = 200
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        is_valid, message = await calendar_service.validate_ical_url("https://example.com/calendar.ics")
    
    assert is_valid == True
    assert message == "Valid iCal URL"


@pytest.mark.asyncio 
async def test_validate_ical_url_invalid_format(calendar_service):
    """Test that invalid URL format fails validation"""
    is_valid, message = await calendar_service.validate_ical_url("not-a-url")
    
    assert is_valid == False
    assert "Invalid URL format" in message


@pytest.mark.asyncio
async def test_validate_ical_url_not_ical_content(calendar_service):
    """Test that non-iCal content fails validation"""
    mock_response = AsyncMock()
    mock_response.text = "<html><body>This is not iCal</body></html>"
    mock_response.status_code = 200
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        is_valid, message = await calendar_service.validate_ical_url("https://example.com/calendar.ics")
    
    assert is_valid == False
    assert "Not a valid iCal file" in message


@pytest.mark.asyncio
async def test_validate_ical_url_timeout(calendar_service):
    """Test that request timeout is handled properly"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.TimeoutException("timeout")
        is_valid, message = await calendar_service.validate_ical_url("https://slow-example.com/calendar.ics")
    
    assert is_valid == False
    assert "Request timeout" in message


@pytest.mark.asyncio
async def test_validate_ical_url_http_error(calendar_service):
    """Test that HTTP errors are handled properly"""
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=AsyncMock(), response=mock_response
    )
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        is_valid, message = await calendar_service.validate_ical_url("https://example.com/missing.ics")
    
    assert is_valid == False
    assert "HTTP 404" in message