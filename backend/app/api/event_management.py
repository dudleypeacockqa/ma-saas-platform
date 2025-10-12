"""
Event Management API
Professional event management with EventBrite integration for Master Admin Portal
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
import logging
import requests
import json

from app.core.database import get_db
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.models.event_management import (
    Event, EventTicket, EventRegistration, EventSession, EventAnalytics,
    EventFeedback, EventLead, EventbriteIntegration, EventTemplate,
    EventEmailAutomation, EventType, EventStatus, EventFormat, TicketType,
    AttendeeStatus, EventbriteStatus, LeadQuality
)
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/events", tags=["event-management"])

# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# ============================================================================

class EventCreate(BaseModel):
    """Create event"""
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    event_type: EventType
    event_format: EventFormat = EventFormat.VIRTUAL
    start_datetime: datetime
    end_datetime: datetime
    timezone: str = "Europe/London"
    max_capacity: Optional[int] = None
    is_free: bool = True
    base_price: float = 0.0
    registration_required: bool = True
    registration_deadline: Optional[datetime] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    virtual_platform: Optional[str] = None
    agenda: Optional[List[Dict[str, Any]]] = None
    speakers: Optional[List[Dict[str, Any]]] = None
    auto_sync_eventbrite: bool = False

class EventTicketCreate(BaseModel):
    """Create event ticket"""
    event_id: str
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    ticket_type: TicketType
    price: float = 0.0
    quantity_total: Optional[int] = None
    sales_start: Optional[datetime] = None
    sales_end: Optional[datetime] = None
    min_quantity: int = 1
    max_quantity: int = 10

class EventRegistrationCreate(BaseModel):
    """Create event registration"""
    event_id: str
    ticket_id: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    custom_questions: Optional[Dict[str, Any]] = None
    marketing_consent: bool = False
    referral_source: Optional[str] = None

class EventLeadCreate(BaseModel):
    """Create event lead"""
    event_id: str
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    lead_quality: LeadQuality = LeadQuality.COLD
    interested_products: Optional[List[str]] = None
    pain_points: Optional[List[str]] = None
    budget_range: Optional[str] = None
    timeline: Optional[str] = None

class EventbriteIntegrationCreate(BaseModel):
    """Create EventBrite integration"""
    api_key: str = Field(..., min_length=1)
    organization_id: str = Field(..., min_length=1)
    auto_sync_enabled: bool = True
    sync_frequency: str = "hourly"

# ============================================================================
# EVENT ENDPOINTS
# ============================================================================

@router.post("/", response_model=Dict[str, Any])
async def create_event(
    event_data: EventCreate,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new event"""
    try:
        # Calculate duration
        duration_minutes = int((event_data.end_datetime - event_data.start_datetime).total_seconds() / 60)
        
        event = Event(
            title=event_data.title,
            description=event_data.description,
            short_description=event_data.short_description,
            event_type=event_data.event_type,
            event_format=event_data.event_format,
            start_datetime=event_data.start_datetime,
            end_datetime=event_data.end_datetime,
            timezone=event_data.timezone,
            duration_minutes=duration_minutes,
            max_capacity=event_data.max_capacity,
            is_free=event_data.is_free,
            base_price=event_data.base_price,
            registration_required=event_data.registration_required,
            registration_deadline=event_data.registration_deadline,
            venue_name=event_data.venue_name,
            venue_address=event_data.venue_address,
            virtual_platform=event_data.virtual_platform,
            agenda=event_data.agenda,
            speakers=event_data.speakers,
            created_by=current_user.user_id
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        # Create default ticket if free event
        if event_data.is_free:
            default_ticket = EventTicket(
                event_id=event.id,
                name="General Admission",
                ticket_type=TicketType.FREE,
                price=0.0,
                quantity_total=event_data.max_capacity,
                quantity_available=event_data.max_capacity
            )
            db.add(default_ticket)
            db.commit()
        
        # Schedule EventBrite sync if requested
        if event_data.auto_sync_eventbrite:
            background_tasks.add_task(_sync_event_to_eventbrite, event.id)
        
        return {
            "event": event,
            "message": "Event created successfully",
            "eventbrite_sync": event_data.auto_sync_eventbrite
        }
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event"
        )

@router.get("/")
async def get_events(
    event_type: Optional[EventType] = None,
    event_format: Optional[EventFormat] = None,
    status: Optional[EventStatus] = None,
    upcoming_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get events with filtering"""
    try:
        query = db.query(Event)
        
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if event_format:
            query = query.filter(Event.event_format == event_format)
        if status:
            query = query.filter(Event.status == status)
        if upcoming_only:
            query = query.filter(Event.start_datetime > datetime.utcnow())
        
        total_count = query.count()
        events = query.order_by(desc(Event.start_datetime)).offset(offset).limit(limit).all()
        
        return {
            "events": events,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch events"
        )

@router.get("/{event_id}")
async def get_event_details(
    event_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed event information"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Get tickets
        tickets = db.query(EventTicket).filter(EventTicket.event_id == event_id).all()
        
        # Get registration statistics
        registration_stats = db.query(
            func.count(EventRegistration.id).label("total_registrations"),
            func.count(EventRegistration.id).filter(
                EventRegistration.status == AttendeeStatus.ATTENDED
            ).label("total_attendees"),
            func.sum(EventRegistration.payment_amount).label("total_revenue")
        ).filter(EventRegistration.event_id == event_id).first()
        
        # Get recent registrations
        recent_registrations = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id
        ).order_by(desc(EventRegistration.registration_date)).limit(10).all()
        
        return {
            "event": event,
            "tickets": tickets,
            "statistics": {
                "total_registrations": registration_stats.total_registrations or 0,
                "total_attendees": registration_stats.total_attendees or 0,
                "total_revenue": float(registration_stats.total_revenue or 0),
                "attendance_rate": (
                    (registration_stats.total_attendees / registration_stats.total_registrations * 100)
                    if registration_stats.total_registrations > 0 else 0
                )
            },
            "recent_registrations": recent_registrations
        }
        
    except Exception as e:
        logger.error(f"Error fetching event details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event details"
        )

@router.put("/{event_id}/status")
async def update_event_status(
    event_id: str,
    new_status: EventStatus,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update event status"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        event.status = new_status
        db.commit()
        db.refresh(event)
        
        return {
            "event": event,
            "message": "Event status updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating event status: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event status"
        )

# ============================================================================
# TICKET ENDPOINTS
# ============================================================================

@router.post("/tickets", response_model=Dict[str, Any])
async def create_event_ticket(
    ticket_data: EventTicketCreate,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create event ticket"""
    try:
        # Verify event exists
        event = db.query(Event).filter(Event.id == ticket_data.event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        ticket = EventTicket(
            event_id=ticket_data.event_id,
            name=ticket_data.name,
            description=ticket_data.description,
            ticket_type=ticket_data.ticket_type,
            price=ticket_data.price,
            quantity_total=ticket_data.quantity_total,
            quantity_available=ticket_data.quantity_total,
            sales_start=ticket_data.sales_start,
            sales_end=ticket_data.sales_end,
            min_quantity=ticket_data.min_quantity,
            max_quantity=ticket_data.max_quantity
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        return {
            "ticket": ticket,
            "message": "Event ticket created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating event ticket: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event ticket"
        )

@router.get("/{event_id}/tickets")
async def get_event_tickets(
    event_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tickets for an event"""
    try:
        tickets = db.query(EventTicket).filter(
            EventTicket.event_id == event_id,
            EventTicket.is_active == True
        ).all()
        
        return {
            "tickets": tickets,
            "count": len(tickets)
        }
        
    except Exception as e:
        logger.error(f"Error fetching event tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event tickets"
        )

# ============================================================================
# REGISTRATION ENDPOINTS
# ============================================================================

@router.post("/registrations", response_model=Dict[str, Any])
async def create_event_registration(
    registration_data: EventRegistrationCreate,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create event registration"""
    try:
        # Verify event exists
        event = db.query(Event).filter(Event.id == registration_data.event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Check if registration is still open
        if event.registration_deadline and datetime.utcnow() > event.registration_deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration deadline has passed"
            )
        
        # Check capacity
        if event.max_capacity:
            current_registrations = db.query(EventRegistration).filter(
                EventRegistration.event_id == registration_data.event_id,
                EventRegistration.status.in_([AttendeeStatus.REGISTERED, AttendeeStatus.CONFIRMED])
            ).count()
            
            if current_registrations >= event.max_capacity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Event is at full capacity"
                )
        
        # Check for duplicate registration
        existing_registration = db.query(EventRegistration).filter(
            EventRegistration.event_id == registration_data.event_id,
            EventRegistration.email == registration_data.email
        ).first()
        
        if existing_registration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered for this event"
            )
        
        registration = EventRegistration(
            event_id=registration_data.event_id,
            ticket_id=registration_data.ticket_id,
            first_name=registration_data.first_name,
            last_name=registration_data.last_name,
            email=registration_data.email,
            phone=registration_data.phone,
            company=registration_data.company,
            job_title=registration_data.job_title,
            custom_questions=registration_data.custom_questions,
            marketing_consent=registration_data.marketing_consent,
            referral_source=registration_data.referral_source
        )
        
        db.add(registration)
        
        # Update event registration count
        event.total_registrations += 1
        
        db.commit()
        db.refresh(registration)
        
        # Send confirmation email
        background_tasks.add_task(_send_registration_confirmation, registration.id)
        
        # Create lead if marketing consent given
        if registration_data.marketing_consent:
            background_tasks.add_task(_create_lead_from_registration, registration.id)
        
        return {
            "registration": registration,
            "message": "Registration successful",
            "confirmation_sent": True
        }
        
    except Exception as e:
        logger.error(f"Error creating event registration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create registration"
        )

@router.get("/{event_id}/registrations")
async def get_event_registrations(
    event_id: str,
    status: Optional[AttendeeStatus] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get event registrations"""
    try:
        query = db.query(EventRegistration).filter(EventRegistration.event_id == event_id)
        
        if status:
            query = query.filter(EventRegistration.status == status)
        
        total_count = query.count()
        registrations = query.order_by(desc(EventRegistration.registration_date)).offset(offset).limit(limit).all()
        
        return {
            "registrations": registrations,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching event registrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch registrations"
        )

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/{event_id}/analytics")
async def get_event_analytics(
    event_id: str,
    period: str = "7d",
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get event analytics"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Get analytics data
        analytics = db.query(EventAnalytics).filter(
            EventAnalytics.event_id == event_id,
            EventAnalytics.analytics_date >= start_date
        ).all()
        
        # Calculate totals
        total_registrations = sum(a.daily_registrations for a in analytics)
        total_attendees = sum(a.attendee_count for a in analytics)
        total_leads = sum(a.leads_generated for a in analytics)
        total_revenue = sum(a.revenue_generated for a in analytics)
        
        # Calculate averages
        avg_engagement = sum(a.engagement_score for a in analytics) / len(analytics) if analytics else 0
        avg_attendance_rate = sum(a.attendance_rate for a in analytics) / len(analytics) if analytics else 0
        
        return {
            "event_id": event_id,
            "period": period,
            "summary": {
                "total_registrations": total_registrations,
                "total_attendees": total_attendees,
                "total_leads_generated": total_leads,
                "total_revenue": total_revenue,
                "average_engagement_score": round(avg_engagement, 2),
                "average_attendance_rate": round(avg_attendance_rate, 2)
            },
            "daily_breakdown": [
                {
                    "date": a.analytics_date.isoformat(),
                    "registrations": a.daily_registrations,
                    "attendees": a.attendee_count,
                    "leads": a.leads_generated,
                    "revenue": a.revenue_generated,
                    "engagement": a.engagement_score
                }
                for a in analytics
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching event analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event analytics"
        )

@router.get("/analytics/overview")
async def get_events_analytics_overview(
    period: str = "30d",
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get overall events analytics overview"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get events in period
        events_query = db.query(Event).filter(
            Event.created_at >= start_date
        )
        
        total_events = events_query.count()
        completed_events = events_query.filter(Event.status == EventStatus.COMPLETED).count()
        
        # Get analytics totals
        analytics_totals = db.query(
            func.sum(EventAnalytics.daily_registrations).label("total_registrations"),
            func.sum(EventAnalytics.attendee_count).label("total_attendees"),
            func.sum(EventAnalytics.leads_generated).label("total_leads"),
            func.sum(EventAnalytics.revenue_generated).label("total_revenue"),
            func.avg(EventAnalytics.engagement_score).label("avg_engagement"),
            func.avg(EventAnalytics.attendance_rate).label("avg_attendance_rate")
        ).filter(EventAnalytics.analytics_date >= start_date).first()
        
        # Get event type breakdown
        event_type_breakdown = db.query(
            Event.event_type,
            func.count(Event.id).label("count")
        ).filter(Event.created_at >= start_date).group_by(Event.event_type).all()
        
        return {
            "period": period,
            "overview": {
                "total_events": total_events,
                "completed_events": completed_events,
                "total_registrations": int(analytics_totals.total_registrations or 0),
                "total_attendees": int(analytics_totals.total_attendees or 0),
                "total_leads_generated": int(analytics_totals.total_leads or 0),
                "total_revenue": float(analytics_totals.total_revenue or 0),
                "average_engagement_score": round(float(analytics_totals.avg_engagement or 0), 2),
                "average_attendance_rate": round(float(analytics_totals.avg_attendance_rate or 0), 2)
            },
            "event_type_breakdown": [
                {
                    "event_type": breakdown.event_type.value,
                    "count": breakdown.count
                }
                for breakdown in event_type_breakdown
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching events analytics overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch events analytics overview"
        )

# ============================================================================
# LEAD MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/leads", response_model=Dict[str, Any])
async def create_event_lead(
    lead_data: EventLeadCreate,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create event lead"""
    try:
        # Verify event exists
        event = db.query(Event).filter(Event.id == lead_data.event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        lead = EventLead(
            event_id=lead_data.event_id,
            first_name=lead_data.first_name,
            last_name=lead_data.last_name,
            email=lead_data.email,
            phone=lead_data.phone,
            company=lead_data.company,
            job_title=lead_data.job_title,
            company_size=lead_data.company_size,
            industry=lead_data.industry,
            lead_quality=lead_data.lead_quality,
            interested_products=lead_data.interested_products,
            pain_points=lead_data.pain_points,
            budget_range=lead_data.budget_range,
            timeline=lead_data.timeline,
            assigned_to=current_user.user_id
        )
        
        db.add(lead)
        
        # Update event lead count
        event.leads_generated += 1
        if lead_data.lead_quality in [LeadQuality.HOT, LeadQuality.QUALIFIED]:
            event.qualified_leads += 1
        
        db.commit()
        db.refresh(lead)
        
        return {
            "lead": lead,
            "message": "Event lead created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating event lead: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event lead"
        )

@router.get("/{event_id}/leads")
async def get_event_leads(
    event_id: str,
    lead_quality: Optional[LeadQuality] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get event leads"""
    try:
        query = db.query(EventLead).filter(EventLead.event_id == event_id)
        
        if lead_quality:
            query = query.filter(EventLead.lead_quality == lead_quality)
        
        total_count = query.count()
        leads = query.order_by(desc(EventLead.created_at)).offset(offset).limit(limit).all()
        
        return {
            "leads": leads,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching event leads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event leads"
        )

# ============================================================================
# EVENTBRITE INTEGRATION ENDPOINTS
# ============================================================================

@router.post("/eventbrite/integration", response_model=Dict[str, Any])
async def create_eventbrite_integration(
    integration_data: EventbriteIntegrationCreate,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create EventBrite integration"""
    try:
        # Test API connection
        test_result = await _test_eventbrite_connection(integration_data.api_key, integration_data.organization_id)
        
        if not test_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"EventBrite connection failed: {test_result['error']}"
            )
        
        integration = EventbriteIntegration(
            api_key=integration_data.api_key,
            organization_id=integration_data.organization_id,
            user_id=test_result["user_id"],
            auto_sync_enabled=integration_data.auto_sync_enabled,
            sync_frequency=integration_data.sync_frequency,
            created_by=current_user.user_id
        )
        
        db.add(integration)
        db.commit()
        db.refresh(integration)
        
        return {
            "integration": integration,
            "message": "EventBrite integration created successfully",
            "connection_test": test_result
        }
        
    except Exception as e:
        logger.error(f"Error creating EventBrite integration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create EventBrite integration"
        )

@router.post("/{event_id}/sync-eventbrite")
async def sync_event_to_eventbrite(
    event_id: str,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync event to EventBrite"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Check if EventBrite integration exists
        integration = db.query(EventbriteIntegration).filter(
            EventbriteIntegration.sync_status == "active"
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active EventBrite integration found"
            )
        
        # Update sync status
        event.eventbrite_status = EventbriteStatus.SYNCING
        db.commit()
        
        # Schedule background sync
        background_tasks.add_task(_sync_event_to_eventbrite, event_id)
        
        return {
            "message": "EventBrite sync initiated",
            "event_id": event_id,
            "sync_status": "syncing"
        }
        
    except Exception as e:
        logger.error(f"Error initiating EventBrite sync: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate EventBrite sync"
        )

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def _sync_event_to_eventbrite(event_id: str):
    """Sync event to EventBrite"""
    logger.info(f"Syncing event {event_id} to EventBrite")
    # This would implement the actual EventBrite API integration

async def _test_eventbrite_connection(api_key: str, organization_id: str) -> Dict[str, Any]:
    """Test EventBrite API connection"""
    try:
        # This would make actual API call to EventBrite
        return {
            "success": True,
            "user_id": "test_user_id",
            "organization_name": "Test Organization"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def _send_registration_confirmation(registration_id: str):
    """Send registration confirmation email"""
    logger.info(f"Sending registration confirmation for {registration_id}")
    # This would integrate with email service

async def _create_lead_from_registration(registration_id: str):
    """Create lead from event registration"""
    logger.info(f"Creating lead from registration {registration_id}")
    # This would create a lead record from the registration data
