"""
iCal router - Generic endpoints for iCal operations.

Provides reusable iCal functionality across the application.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx

from ..data.ical_parser import parse_ical_content

router = APIRouter()


class ICalPreviewRequest(BaseModel):
    """Request body for iCal preview."""
    calendar_url: str = Field(..., min_length=10, max_length=2000)


class EventPreview(BaseModel):
    """Preview of a single event."""
    title: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None


class ICalPreviewResponse(BaseModel):
    """Response for iCal preview."""
    event_count: int
    events: List[EventPreview]
    error: Optional[str] = None


@router.post(
    "/ical/preview",
    response_model=ICalPreviewResponse,
    summary="Preview events from an iCal URL",
    description="Fetch and parse an iCal URL to preview events. Returns up to 10 events for preview."
)
async def preview_ical(request: ICalPreviewRequest) -> ICalPreviewResponse:
    """
    Generic endpoint to preview events from any iCal URL.

    Reusable across the application:
    - Domain request validation
    - Calendar URL testing
    - Any future iCal preview needs
    """
    try:
        # Fetch iCal content
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(request.calendar_url)
            response.raise_for_status()
            ical_content = response.text

        # Parse iCal content
        parse_result = parse_ical_content(ical_content)

        if not parse_result.is_success:
            return ICalPreviewResponse(
                event_count=0,
                events=[],
                error=f"Failed to parse iCal: {parse_result.error}"
            )

        events = parse_result.value
        if not events:
            return ICalPreviewResponse(
                event_count=0,
                events=[],
                error="No events found in calendar"
            )

        # Convert to preview format (limit to first 10 events)
        preview_events = []
        for event in events[:10]:
            preview_events.append(EventPreview(
                title=event.get('title', 'Untitled Event'),
                start_time=event.get('start'),
                end_time=event.get('end'),
                location=event.get('location')
            ))

        return ICalPreviewResponse(
            event_count=len(events),
            events=preview_events,
            error=None
        )

    except httpx.HTTPStatusError as e:
        return ICalPreviewResponse(
            event_count=0,
            events=[],
            error=f"Failed to fetch calendar: HTTP {e.response.status_code}"
        )
    except httpx.TimeoutException:
        return ICalPreviewResponse(
            event_count=0,
            events=[],
            error="Request timed out - calendar URL took too long to respond"
        )
    except httpx.RequestError as e:
        return ICalPreviewResponse(
            event_count=0,
            events=[],
            error=f"Failed to fetch calendar: {str(e)}"
        )
    except Exception as e:
        return ICalPreviewResponse(
            event_count=0,
            events=[],
            error=f"Unexpected error: {str(e)}"
        )
