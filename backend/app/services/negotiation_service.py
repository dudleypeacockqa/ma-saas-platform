"""
Negotiation Service for M&A SaaS Platform
Comprehensive service for managing deal negotiations with workflow automation
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session
import uuid
import json

from ..models.negotiations import (
    Negotiation, NegotiationParticipant, NegotiationPosition, NegotiationMessage,
    TermSheet, TermSheetTemplate, DealStructure,
    NegotiationStatus, ParticipantRole, PositionStatus, MessageType,
    TermSheetStatus, DealStructureType
)
from ..models.deal import Deal
from ..models.user import User


class NegotiationService:
    """Service for managing deal negotiations and workflow automation"""

    def __init__(self, db: Session):
        self.db = db

    def create_negotiation(
        self,
        organization_id: str,
        deal_id: str,
        title: str,
        description: Optional[str] = None,
        buyer_lead_id: Optional[str] = None,
        seller_lead_id: Optional[str] = None,
        target_completion_date: Optional[date] = None,
        created_by_id: Optional[str] = None
    ) -> Negotiation:
        """
        Create a new negotiation session

        Args:
            organization_id: Tenant ID
            deal_id: Associated deal ID
            title: Negotiation title
            description: Optional description
            buyer_lead_id: Lead negotiator for buyer side
            seller_lead_id: Lead negotiator for seller side
            target_completion_date: Target completion date
            created_by_id: User who created the negotiation

        Returns:
            Created negotiation instance
        """
        # Get latest negotiation round for this deal
        latest_round = (
            self.db.query(func.max(Negotiation.negotiation_round))
            .filter(Negotiation.deal_id == deal_id)
            .scalar() or 0
        )

        negotiation = Negotiation(
            organization_id=organization_id,
            deal_id=deal_id,
            negotiation_round=latest_round + 1,
            title=title,
            description=description,
            buyer_lead_id=buyer_lead_id,
            seller_lead_id=seller_lead_id,
            target_completion_date=target_completion_date,
            created_by=created_by_id
        )

        self.db.add(negotiation)
        self.db.commit()
        self.db.refresh(negotiation)

        # Automatically add lead negotiators as participants
        if buyer_lead_id:
            self.add_participant(
                negotiation.id,
                buyer_lead_id,
                ParticipantRole.BUYER,
                can_make_offers=True,
                can_accept_terms=True,
                added_by_id=created_by_id
            )

        if seller_lead_id:
            self.add_participant(
                negotiation.id,
                seller_lead_id,
                ParticipantRole.SELLER,
                can_make_offers=True,
                can_accept_terms=True,
                added_by_id=created_by_id
            )

        return negotiation

    def add_participant(
        self,
        negotiation_id: str,
        user_id: str,
        role: ParticipantRole,
        party_name: Optional[str] = None,
        can_make_offers: bool = False,
        can_accept_terms: bool = False,
        can_view_confidential: bool = False,
        added_by_id: Optional[str] = None
    ) -> NegotiationParticipant:
        """
        Add a participant to a negotiation

        Args:
            negotiation_id: Negotiation ID
            user_id: User to add as participant
            role: Participant role
            party_name: Company/entity they represent
            can_make_offers: Permission to make offers
            can_accept_terms: Permission to accept terms
            can_view_confidential: Permission to view confidential info
            added_by_id: User who added the participant

        Returns:
            Created participant instance
        """
        negotiation = self.get_negotiation_by_id(negotiation_id)
        if not negotiation:
            raise ValueError("Negotiation not found")

        # Check if user is already a participant
        existing = (
            self.db.query(NegotiationParticipant)
            .filter(
                NegotiationParticipant.negotiation_id == negotiation_id,
                NegotiationParticipant.user_id == user_id
            )
            .first()
        )

        if existing:
            raise ValueError("User is already a participant in this negotiation")

        participant = NegotiationParticipant(
            organization_id=negotiation.organization_id,
            negotiation_id=negotiation_id,
            user_id=user_id,
            role=role,
            party_name=party_name,
            can_make_offers=can_make_offers,
            can_accept_terms=can_accept_terms,
            can_view_confidential=can_view_confidential,
            created_by=added_by_id
        )

        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)

        return participant

    def create_position(
        self,
        negotiation_id: str,
        term_category: str,
        term_name: str,
        term_description: Optional[str] = None,
        buyer_position: Optional[str] = None,
        seller_position: Optional[str] = None,
        priority_level: int = 3,
        deal_breaker: bool = False,
        financial_impact: Optional[Decimal] = None,
        assigned_to_id: Optional[str] = None,
        target_resolution_date: Optional[date] = None,
        created_by_id: Optional[str] = None
    ) -> NegotiationPosition:
        """
        Create a new negotiation position

        Args:
            negotiation_id: Negotiation ID
            term_category: Category of the term (e.g., 'purchase_price')
            term_name: Name of the specific term
            term_description: Description of the term
            buyer_position: Buyer's position on this term
            seller_position: Seller's position on this term
            priority_level: Priority (1=critical, 5=nice-to-have)
            deal_breaker: Whether this is a deal-breaking term
            financial_impact: Estimated financial impact
            assigned_to_id: User assigned to resolve this position
            target_resolution_date: Target resolution date
            created_by_id: User who created the position

        Returns:
            Created position instance
        """
        negotiation = self.get_negotiation_by_id(negotiation_id)
        if not negotiation:
            raise ValueError("Negotiation not found")

        position = NegotiationPosition(
            organization_id=negotiation.organization_id,
            negotiation_id=negotiation_id,
            term_category=term_category,
            term_name=term_name,
            term_description=term_description,
            buyer_position=buyer_position,
            seller_position=seller_position,
            priority_level=priority_level,
            deal_breaker=deal_breaker,
            financial_impact=financial_impact,
            assigned_to_id=assigned_to_id,
            target_resolution_date=target_resolution_date,
            created_by=created_by_id
        )

        self.db.add(position)

        # Update negotiation totals
        negotiation.total_positions += 1
        if deal_breaker:
            negotiation.open_issues_count += 1

        self.db.commit()
        self.db.refresh(position)

        return position

    def update_position(
        self,
        position_id: str,
        organization_id: str,
        updates: Dict[str, Any],
        updated_by_id: Optional[str] = None
    ) -> NegotiationPosition:
        """
        Update a negotiation position with history tracking

        Args:
            position_id: Position ID to update
            organization_id: Tenant ID for security
            updates: Dictionary of field updates
            updated_by_id: User making the update

        Returns:
            Updated position instance
        """
        position = (
            self.db.query(NegotiationPosition)
            .filter(
                NegotiationPosition.id == position_id,
                NegotiationPosition.organization_id == organization_id
            )
            .first()
        )

        if not position:
            raise ValueError("Position not found")

        # Track changes in position history
        change_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'updated_by': updated_by_id,
            'changes': {}
        }

        old_status = position.status

        # Update fields and track changes
        for field, new_value in updates.items():
            if hasattr(position, field):
                old_value = getattr(position, field)
                if old_value != new_value:
                    change_record['changes'][field] = {
                        'old_value': str(old_value) if old_value else None,
                        'new_value': str(new_value) if new_value else None
                    }
                    setattr(position, field, new_value)

        # Add to position history if there were changes
        if change_record['changes']:
            if not position.position_history:
                position.position_history = []
            position.position_history.append(change_record)

        # Update negotiation counters if status changed
        if 'status' in updates and old_status != updates['status']:
            negotiation = position.negotiation
            if updates['status'] == PositionStatus.ACCEPTED and old_status != PositionStatus.ACCEPTED:
                negotiation.resolved_positions += 1
            elif old_status == PositionStatus.ACCEPTED and updates['status'] != PositionStatus.ACCEPTED:
                negotiation.resolved_positions -= 1

            # Update completion percentage
            if negotiation.total_positions > 0:
                negotiation.completion_percentage = int(
                    (negotiation.resolved_positions / negotiation.total_positions) * 100
                )

        position.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(position)

        return position

    def send_message(
        self,
        negotiation_id: str,
        sender_id: str,
        content: str,
        message_type: MessageType = MessageType.QUESTION,
        subject: Optional[str] = None,
        parent_message_id: Optional[str] = None,
        related_position_id: Optional[str] = None,
        is_internal: bool = False,
        requires_response: bool = False,
        response_deadline: Optional[datetime] = None
    ) -> NegotiationMessage:
        """
        Send a message in the negotiation

        Args:
            negotiation_id: Negotiation ID
            sender_id: User sending the message
            content: Message content
            message_type: Type of message
            subject: Message subject
            parent_message_id: ID of message being replied to
            related_position_id: Related position if applicable
            is_internal: Whether this is an internal team message
            requires_response: Whether a response is required
            response_deadline: When response is due

        Returns:
            Created message instance
        """
        negotiation = self.get_negotiation_by_id(negotiation_id)
        if not negotiation:
            raise ValueError("Negotiation not found")

        # Generate thread ID for new threads
        thread_id = parent_message_id
        if not thread_id:
            # This is a new thread
            thread_id = str(uuid.uuid4())

        message = NegotiationMessage(
            organization_id=negotiation.organization_id,
            negotiation_id=negotiation_id,
            sender_id=sender_id,
            message_type=message_type,
            subject=subject,
            content=content,
            parent_message_id=parent_message_id,
            thread_id=thread_id,
            related_position_id=related_position_id,
            is_internal=is_internal,
            requires_response=requires_response,
            response_deadline=response_deadline,
            created_by=sender_id
        )

        self.db.add(message)

        # Update negotiation last activity
        negotiation.last_activity_date = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)

        return message

    def create_term_sheet(
        self,
        negotiation_id: str,
        title: str,
        terms: Dict[str, Any],
        template_id: Optional[str] = None,
        purchase_price: Optional[Decimal] = None,
        currency: str = "USD",
        effective_date: Optional[date] = None,
        expiration_date: Optional[date] = None,
        created_by_id: Optional[str] = None
    ) -> TermSheet:
        """
        Create a new term sheet for the negotiation

        Args:
            negotiation_id: Negotiation ID
            title: Term sheet title
            terms: Dictionary of all terms and values
            template_id: Template used (if any)
            purchase_price: Purchase price
            currency: Currency code
            effective_date: Effective date
            expiration_date: Expiration date
            created_by_id: User creating the term sheet

        Returns:
            Created term sheet instance
        """
        negotiation = self.get_negotiation_by_id(negotiation_id)
        if not negotiation:
            raise ValueError("Negotiation not found")

        # Generate version number
        existing_count = (
            self.db.query(func.count(TermSheet.id))
            .filter(TermSheet.negotiation_id == negotiation_id)
            .scalar()
        )
        version = f"{existing_count + 1}.0"

        term_sheet = TermSheet(
            organization_id=negotiation.organization_id,
            negotiation_id=negotiation_id,
            template_id=template_id,
            title=title,
            version=version,
            terms=terms,
            purchase_price=purchase_price,
            currency=currency,
            effective_date=effective_date,
            expiration_date=expiration_date,
            created_by=created_by_id
        )

        self.db.add(term_sheet)

        # Update negotiation to point to this term sheet as current
        negotiation.current_term_sheet_id = term_sheet.id

        self.db.commit()
        self.db.refresh(term_sheet)

        return term_sheet

    def analyze_negotiation_progress(
        self,
        negotiation_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Analyze negotiation progress and generate insights

        Args:
            negotiation_id: Negotiation ID
            organization_id: Tenant ID for security

        Returns:
            Dictionary with progress analysis and insights
        """
        negotiation = (
            self.db.query(Negotiation)
            .filter(
                Negotiation.id == negotiation_id,
                Negotiation.organization_id == organization_id
            )
            .first()
        )

        if not negotiation:
            raise ValueError("Negotiation not found")

        # Get all positions
        positions = (
            self.db.query(NegotiationPosition)
            .filter(NegotiationPosition.negotiation_id == negotiation_id)
            .all()
        )

        # Analyze positions by status
        status_breakdown = {}
        for status in PositionStatus:
            status_breakdown[status.value] = sum(
                1 for p in positions if p.status == status
            )

        # Analyze by priority
        priority_breakdown = {}
        for i in range(1, 6):
            priority_breakdown[f"priority_{i}"] = sum(
                1 for p in positions if p.priority_level == i
            )

        # Deal breakers analysis
        deal_breakers = [p for p in positions if p.deal_breaker]
        unresolved_deal_breakers = [
            p for p in deal_breakers if p.status != PositionStatus.ACCEPTED
        ]

        # Overdue positions
        today = datetime.utcnow().date()
        overdue_positions = [
            p for p in positions
            if p.target_resolution_date and p.target_resolution_date < today
            and p.status not in [PositionStatus.ACCEPTED, PositionStatus.WITHDRAWN]
        ]

        # Recent activity
        recent_messages = (
            self.db.query(NegotiationMessage)
            .filter(NegotiationMessage.negotiation_id == negotiation_id)
            .filter(NegotiationMessage.created_at >= datetime.utcnow() - timedelta(days=7))
            .count()
        )

        # Calculate momentum score (0-100)
        momentum_factors = []

        # Recent activity factor
        if recent_messages > 10:
            momentum_factors.append(100)
        elif recent_messages > 5:
            momentum_factors.append(75)
        elif recent_messages > 1:
            momentum_factors.append(50)
        else:
            momentum_factors.append(25)

        # Progress factor
        if negotiation.completion_percentage >= 80:
            momentum_factors.append(90)
        elif negotiation.completion_percentage >= 60:
            momentum_factors.append(70)
        elif negotiation.completion_percentage >= 40:
            momentum_factors.append(50)
        else:
            momentum_factors.append(30)

        # Deal breaker factor
        if len(unresolved_deal_breakers) == 0:
            momentum_factors.append(100)
        elif len(unresolved_deal_breakers) <= 2:
            momentum_factors.append(60)
        else:
            momentum_factors.append(20)

        momentum_score = sum(momentum_factors) / len(momentum_factors)

        return {
            'negotiation_id': negotiation_id,
            'status': negotiation.status.value,
            'completion_percentage': negotiation.completion_percentage,
            'total_positions': negotiation.total_positions,
            'resolved_positions': negotiation.resolved_positions,
            'open_issues': negotiation.open_issues_count,
            'days_active': negotiation.days_active,
            'is_overdue': negotiation.is_overdue,
            'momentum_score': round(momentum_score, 1),
            'status_breakdown': status_breakdown,
            'priority_breakdown': priority_breakdown,
            'deal_breakers': {
                'total': len(deal_breakers),
                'unresolved': len(unresolved_deal_breakers),
                'positions': [{'id': p.id, 'term_name': p.term_name} for p in unresolved_deal_breakers]
            },
            'overdue_positions': {
                'count': len(overdue_positions),
                'positions': [
                    {
                        'id': p.id,
                        'term_name': p.term_name,
                        'days_overdue': (today - p.target_resolution_date).days
                    }
                    for p in overdue_positions
                ]
            },
            'recent_activity': {
                'messages_last_7_days': recent_messages,
                'last_activity': negotiation.last_activity_date.isoformat() if negotiation.last_activity_date else None
            }
        }

    def get_negotiation_by_id(
        self,
        negotiation_id: str,
        organization_id: Optional[str] = None
    ) -> Optional[Negotiation]:
        """Get negotiation by ID with optional tenant filtering"""
        query = self.db.query(Negotiation).filter(Negotiation.id == negotiation_id)

        if organization_id:
            query = query.filter(Negotiation.organization_id == organization_id)

        return query.first()

    def list_negotiations(
        self,
        organization_id: str,
        deal_id: Optional[str] = None,
        status: Optional[NegotiationStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Negotiation]:
        """
        List negotiations with filtering

        Args:
            organization_id: Tenant ID
            deal_id: Filter by specific deal
            status: Filter by negotiation status
            limit: Maximum results to return
            offset: Results offset for pagination

        Returns:
            List of negotiations
        """
        query = (
            self.db.query(Negotiation)
            .filter(Negotiation.organization_id == organization_id)
            .order_by(desc(Negotiation.last_activity_date))
        )

        if deal_id:
            query = query.filter(Negotiation.deal_id == deal_id)

        if status:
            query = query.filter(Negotiation.status == status)

        return query.offset(offset).limit(limit).all()

    def get_negotiation_positions(
        self,
        negotiation_id: str,
        organization_id: str,
        status: Optional[PositionStatus] = None,
        priority_levels: Optional[List[int]] = None,
        deal_breakers_only: bool = False
    ) -> List[NegotiationPosition]:
        """
        Get positions for a negotiation with filtering

        Args:
            negotiation_id: Negotiation ID
            organization_id: Tenant ID for security
            status: Filter by position status
            priority_levels: Filter by priority levels
            deal_breakers_only: Only return deal-breaking positions

        Returns:
            List of negotiation positions
        """
        query = (
            self.db.query(NegotiationPosition)
            .filter(
                NegotiationPosition.negotiation_id == negotiation_id,
                NegotiationPosition.organization_id == organization_id
            )
            .order_by(
                NegotiationPosition.priority_level,
                NegotiationPosition.created_at
            )
        )

        if status:
            query = query.filter(NegotiationPosition.status == status)

        if priority_levels:
            query = query.filter(NegotiationPosition.priority_level.in_(priority_levels))

        if deal_breakers_only:
            query = query.filter(NegotiationPosition.deal_breaker == True)

        return query.all()

    def get_negotiation_messages(
        self,
        negotiation_id: str,
        organization_id: str,
        thread_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        include_internal: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[NegotiationMessage]:
        """
        Get messages for a negotiation with filtering

        Args:
            negotiation_id: Negotiation ID
            organization_id: Tenant ID for security
            thread_id: Filter by specific thread
            message_type: Filter by message type
            include_internal: Whether to include internal messages
            limit: Maximum results to return
            offset: Results offset for pagination

        Returns:
            List of negotiation messages
        """
        query = (
            self.db.query(NegotiationMessage)
            .filter(
                NegotiationMessage.negotiation_id == negotiation_id,
                NegotiationMessage.organization_id == organization_id
            )
            .order_by(desc(NegotiationMessage.created_at))
        )

        if thread_id:
            query = query.filter(NegotiationMessage.thread_id == thread_id)

        if message_type:
            query = query.filter(NegotiationMessage.message_type == message_type)

        if not include_internal:
            query = query.filter(NegotiationMessage.is_internal == False)

        return query.offset(offset).limit(limit).all()