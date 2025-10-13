"""
Advanced Platform Service
Unified orchestration layer for AI intelligence, document automation, real-time collaboration,
integration monitoring, and analytics capabilities specific to M&A workflows.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.deal_intelligence.deal_intelligence_engine import (
    DealProfile,
    DealStage,
    DealType,
    IndustryVertical,
    get_deal_intelligence_engine,
)
from app.deal_intelligence.due_diligence_automation import (
    DataRoomAccess,
    DataRoomUser,
    DocumentMetadata,
    DocumentType,
    get_due_diligence_automation,
)
from app.deal_intelligence.predictive_analytics import get_predictive_analytics
from app.services.due_diligence import DueDiligenceService
from app.analytics.real_time_analytics import (
    Alert,
    KPI,
    RealTimeAnalyticsEngine,
    RealtimeInsight,
    get_real_time_analytics_engine,
)
from app.analytics.reporting_engine import ReportType, TemplateManager
from app.realtime.collaboration import document_manager
from app.realtime.task_automation import (
    TaskAutomationEngine,
    WorkflowTrigger,
    get_task_engine,
)
from app.utils.collaboration import (
    AnalyticsHelper,
    CollaborationManager,
    MeetingInvite,
)
from app.integrations.core.integration_manager import get_integration_manager


class _AdvancedCollaborationState:
    """In-memory collaboration state for comment threads and audit trails."""

    def __init__(self) -> None:
        self.comment_threads: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()

    async def add_comment(
        self,
        thread_key: str,
        comment: Dict[str, Any],
    ) -> Dict[str, Any]:
        async with self._lock:
            if thread_key not in self.comment_threads:
                self.comment_threads[thread_key] = []
            self.comment_threads[thread_key].append(comment)
            return comment

    async def resolve_comment(
        self,
        thread_key: str,
        comment_id: str,
        resolved_by: str,
    ) -> Optional[Dict[str, Any]]:
        async with self._lock:
            comments = self.comment_threads.get(thread_key)
            if not comments:
                return None

            for existing in comments:
                if existing["comment_id"] == comment_id:
                    existing["resolved_at"] = datetime.utcnow().isoformat()
                    existing["resolved_by"] = resolved_by
                    existing["status"] = "resolved"
                    return existing

            return None

    async def list_comments(self, thread_key: str) -> List[Dict[str, Any]]:
        async with self._lock:
            return list(self.comment_threads.get(thread_key, []))


_collaboration_manager = CollaborationManager()
_collaboration_state = _AdvancedCollaborationState()
_collaboration_analytics = AnalyticsHelper()
_template_manager = TemplateManager()


class AdvancedPlatformService:
    """High-level service that composes advanced platform capabilities."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.deal_intelligence_engine = get_deal_intelligence_engine()
        self.predictive_engine = get_predictive_analytics()
        self.due_diligence_automation = get_due_diligence_automation()
        self.due_diligence_service = DueDiligenceService(db)
        self.analytics_engine: RealTimeAnalyticsEngine = get_real_time_analytics_engine()
        self.task_engine: TaskAutomationEngine = get_task_engine()

    # ---------------------------------------------------------------------
    # AI-powered deal intelligence
    # ---------------------------------------------------------------------
    async def generate_deal_intelligence(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run end-to-end AI-powered deal intelligence workflow."""

        deal_profile = self._build_deal_profile(payload)
        analysis_result = await self.deal_intelligence_engine.analyze_deal_opportunity(
            deal_profile
        )

        predictive_insights = await self.predictive_engine.comprehensive_deal_analysis(
            deal_profile.deal_id,
            {
                "deal_value": deal_profile.deal_value,
                "industry": deal_profile.industry.value,
                "stage": deal_profile.stage.value,
                **(payload.get("predictive_features") or {}),
            },
        )

        checklist_result: Optional[Dict[str, Any]] = None
        if payload.get("generate_checklist"):
            checklist_result = await self._generate_due_diligence_checklist(
                deal_profile,
                payload.get("industry_details", deal_profile.industry.value),
            )

        due_diligence_summary: Optional[Dict[str, Any]] = None
        try:
            due_diligence_summary = await self.due_diligence_automation.generate_due_diligence_summary(
                deal_profile.deal_id
            )
        except Exception:
            # Summary is optional; continue gracefully if not available yet.
            due_diligence_summary = None

        financial_validation = self._validate_financial_model(
            payload.get("financials") or {},
            deal_profile.deal_value,
        )

        return {
            "deal_id": deal_profile.deal_id,
            "analysis_timestamp": analysis_result.get("analysis_timestamp"),
            "deal_score": analysis_result.get("deal_score"),
            "market_context": analysis_result.get("market_context"),
            "strategic_fit": analysis_result.get("strategic_fit"),
            "transaction_probability": analysis_result.get("transaction_probability"),
            "executive_summary": analysis_result.get("executive_summary"),
            "next_steps": analysis_result.get("next_steps", []),
            "predictive_insights": predictive_insights,
            "due_diligence_checklist": checklist_result,
            "due_diligence_summary": due_diligence_summary,
            "financial_validation": financial_validation,
        }

    # ---------------------------------------------------------------------
    # Advanced document management
    # ---------------------------------------------------------------------
    async def process_document(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Perform OCR, analysis, version tracking, and secure data room operations."""

        document_id = payload["document_id"]
        deal_id = payload["deal_id"]
        data_room_id = payload.get("data_room_id") or f"dataroom_{deal_id}"
        folder_path = payload.get("folder_path", "General")
        uploader_id = payload.get("uploaded_by", "system")

        document_type = self._safe_enum(
            payload.get("document_type"),
            DocumentType,
            DocumentType.FINANCIAL_STATEMENT,
        )

        data_room_result = await self._ensure_data_room(
            data_room_id=data_room_id,
            deal_id=deal_id,
            uploader_id=uploader_id,
            access_level=payload.get("access_level", DataRoomAccess.UPLOAD.value),
            permitted_folders=payload.get("permitted_folders") or [folder_path],
        )

        document_metadata = DocumentMetadata(
            document_id=document_id,
            filename=payload.get("filename", f"document_{document_id}.pdf"),
            document_type=document_type,
            file_size=payload.get("file_size", len(payload.get("content", ""))),
            upload_date=datetime.utcnow(),
            uploaded_by=uploader_id,
            version=payload.get("version", 1),
            tags=payload.get("tags", []),
            security_classification=payload.get("security_classification", "confidential"),
        )

        # Persist metadata inside the virtual data room
        self.due_diligence_automation.data_room_manager.upload_document(
            data_room_id=data_room_id,
            user_id=uploader_id,
            document_metadata=document_metadata,
            folder_path=folder_path,
        )

        document_analysis = self.due_diligence_automation.document_analysis_engine.analyze_document(
            document_id=document_id,
            document_content=payload.get("content", ""),
            document_type=document_type,
            ai_models=payload.get("analysis_options") or {},
        )

        # Track audit activity
        self.due_diligence_automation.data_room_manager.track_document_access(
            data_room_id=data_room_id,
            user_id=uploader_id,
            document_id=document_id,
            action="uploaded",
        )

        change_id = _collaboration_manager.document_manager.track_document_change(
            document_id=document_id,
            user_id=uploader_id,
            change_type="upload",
            change_data={
                "version": document_metadata.version,
                "folder_path": folder_path,
                "filename": document_metadata.filename,
            },
        )

        audit_trail = [
            {
                **entry,
                "timestamp": entry["timestamp"].isoformat(),
            }
            for entry in self.due_diligence_automation.data_room_manager.access_logs.get(
                data_room_id, []
            )
        ]

        return {
            "document_id": document_id,
            "deal_id": deal_id,
            "data_room_id": data_room_id,
            "analysis": asdict(document_analysis),
            "data_room": data_room_result,
            "version": {
                "change_id": change_id,
                "version": document_metadata.version,
                "updated_at": datetime.utcnow().isoformat(),
            },
            "audit_trail": audit_trail,
        }

    # ---------------------------------------------------------------------
    # Real-time collaboration
    # ---------------------------------------------------------------------
    async def start_collaboration_session(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Initiate collaborative editing session and return realtime context."""

        document_id = payload["document_id"]
        user_id = payload["user_id"]
        organization_id = payload.get("organization_id", "org")

        session = _collaboration_manager.document_manager.start_collaboration_session(
            document_id=document_id,
            user_id=user_id,
            permissions=payload.get("permissions", "write"),
        )

        state = await document_manager.join_document(
            document_id=document_id,
            user_id=user_id,
            user_info={
                "name": payload.get("user_name"),
                "role": payload.get("user_role"),
            },
            organization_id=organization_id,
        )

        channel = f"doc_{document_id}"

        return {
            "session": session,
            "realtime_channel": channel,
            "websocket_endpoint": "/socket.io",
            "document_state": {
                "version": state.version,
                "last_modified": state.last_modified.isoformat(),
                "active_users": list(state.active_users.keys()),
            },
        }

    async def add_comment(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        thread_key = self._comment_thread_key(
            payload.get("entity_type", "document"),
            payload.get("entity_id"),
        )
        comment = {
            "comment_id": f"cmt_{datetime.utcnow().timestamp():.0f}",
            "user_id": payload["user_id"],
            "body": payload.get("body", ""),
            "created_at": datetime.utcnow().isoformat(),
            "status": "open",
            "metadata": payload.get("metadata", {}),
        }
        await _collaboration_state.add_comment(thread_key, comment)
        return comment

    async def resolve_comment(
        self,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        thread_key = self._comment_thread_key(
            payload.get("entity_type", "document"),
            payload.get("entity_id"),
        )
        return await _collaboration_state.resolve_comment(
            thread_key=thread_key,
            comment_id=payload["comment_id"],
            resolved_by=payload["resolved_by"],
        )

    async def trigger_task_workflow(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        trigger_value = payload.get("trigger", WorkflowTrigger.DOCUMENT_UPLOADED.value)
        trigger = self._safe_enum(trigger_value, WorkflowTrigger, WorkflowTrigger.DOCUMENT_UPLOADED)

        workflow_id = await self.task_engine.trigger_workflow(
            trigger=trigger,
            context=payload.get("context", {}),
            organization_id=payload.get("organization_id", "org"),
            deal_id=payload.get("deal_id"),
        )

        return {
            "workflow_id": workflow_id,
            "trigger": trigger.value,
            "status": "queued" if workflow_id else "ignored",
        }

    async def schedule_video_meeting(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        meeting = MeetingInvite(
            meeting_id=payload.get("meeting_id", f"meet_{datetime.utcnow().timestamp():.0f}"),
            title=payload.get("title", "M&A Working Session"),
            description=payload.get("description", ""),
            start_time=payload.get("start_time", datetime.utcnow()),
            end_time=payload.get("end_time", datetime.utcnow()),
            organizer_email=payload.get("organizer_email", "organizer@example.com"),
            attendee_emails=payload.get("attendee_emails", []),
            meeting_url=payload.get("meeting_url"),
            location=payload.get("location"),
        )

        result = await _collaboration_manager.schedule_meeting(meeting)
        result["meeting_url"] = meeting.meeting_url or payload.get(
            "meeting_url", "https://meet.example.com/session"
        )
        return result

    # ---------------------------------------------------------------------
    # Enterprise integrations
    # ---------------------------------------------------------------------
    async def get_integration_status(self) -> Dict[str, Any]:
        manager = await get_integration_manager()
        integrations = await manager.list_integrations()
        return {
            "retrieved_at": datetime.utcnow().isoformat(),
            "integrations": integrations,
        }

    # ---------------------------------------------------------------------
    # Advanced analytics
    # ---------------------------------------------------------------------
    async def get_analytics_overview(
        self,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = payload or {}

        kpis = await self.analytics_engine.get_realtime_kpis()
        insights = await self.analytics_engine.get_realtime_insights(limit=5)
        alerts = await self.analytics_engine.get_active_alerts()
        processing_stats = self.analytics_engine.get_processing_stats()

        team_metrics = {}
        for team_id in payload.get("team_ids", []):
            team_metrics[team_id] = _collaboration_analytics.calculate_team_collaboration_score(
                team_id=team_id,
                period_days=payload.get("period_days", 30),
            )

        available_templates = _template_manager.list_templates(ReportType.EXECUTIVE_SUMMARY)
        report_preview = None
        if available_templates:
            template = available_templates[0]
            report_preview = {
                "template_id": template.template_id,
                "name": template.name,
                "sections": [section.section_id for section in template.sections],
                "format": template.format.value,
            }

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "kpis": [self._serialize_dataclass(item) for item in kpis],
            "insights": [self._serialize_dataclass(item) for item in insights],
            "active_alerts": [self._serialize_dataclass(item) for item in alerts],
            "processing_stats": processing_stats,
            "team_performance": team_metrics,
            "report_preview": report_preview,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_deal_profile(self, payload: Dict[str, Any]) -> DealProfile:
        return DealProfile(
            deal_id=payload["deal_id"],
            deal_type=self._safe_enum(
                payload.get("deal_type"),
                DealType,
                DealType.ACQUISITION,
            ),
            target_company=payload.get("target_company", ""),
            acquirer_company=payload.get("acquirer_company", ""),
            industry=self._safe_enum(
                payload.get("industry"),
                IndustryVertical,
                IndustryVertical.TECHNOLOGY,
            ),
            deal_value=float(payload.get("deal_value", 0)),
            currency=payload.get("currency", "USD"),
            stage=self._safe_enum(
                payload.get("stage"),
                DealStage,
                DealStage.ORIGINATION,
            ),
            expected_close_date=payload.get("expected_close_date"),
            key_metrics=payload.get("key_metrics", {}),
            strategic_rationale=payload.get("strategic_rationale", ""),
        )

    async def _generate_due_diligence_checklist(
        self,
        deal_profile: DealProfile,
        industry: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            checklist = await self.due_diligence_service.generate_checklist(
                deal_id=deal_profile.deal_id,
                deal_type=deal_profile.deal_type,
                industry=industry,
            )
            return {
                "checklist_id": str(getattr(checklist, "id", "")),
                "name": getattr(checklist, "name", ""),
                "categories": getattr(checklist, "categories", []),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "error": str(exc),
                "checklist_id": None,
            }

    async def _ensure_data_room(
        self,
        data_room_id: str,
        deal_id: str,
        uploader_id: str,
        access_level: str,
        permitted_folders: List[str],
    ) -> Dict[str, Any]:
        manager = self.due_diligence_automation.data_room_manager
        if data_room_id not in manager.data_rooms:
            manager.create_data_room(
                data_room_id=data_room_id,
                name=f"Data Room - {deal_id}",
                deal_id=deal_id,
                administrator=uploader_id,
            )

        access = self._safe_enum(access_level, DataRoomAccess, DataRoomAccess.UPLOAD)
        user = DataRoomUser(
            user_id=uploader_id,
            name=uploader_id,
            organization="",
            email=f"{uploader_id}@example.com",
            access_level=access,
            permitted_folders=permitted_folders,
            access_granted_date=datetime.utcnow(),
        )
        manager.add_user(data_room_id, user)
        return manager.data_rooms[data_room_id]

    def _validate_financial_model(
        self,
        financials: Dict[str, Any],
        deal_value: float,
    ) -> Dict[str, Any]:
        required_metrics = ["revenue", "ebitda", "growth_rate", "margin"]
        missing = [metric for metric in required_metrics if metric not in financials]

        recommendations = []
        if missing:
            recommendations.append(
                f"Add missing financial metrics: {', '.join(missing)}"
            )

        if financials.get("ebitda", 0) <= 0:
            recommendations.append("EBITDA is non-positive. Verify profitability assumptions.")

        if financials.get("growth_rate") and financials["growth_rate"] < 0:
            recommendations.append("Negative growth rate detected. Review market trends and projections.")

        leverage_ratio = financials.get("net_debt") and financials.get("ebitda")
        if leverage_ratio:
            leverage = financials["net_debt"] / max(financials["ebitda"], 1e-6)
            if leverage > 5:
                recommendations.append("Leverage exceeds typical thresholds. Consider refinancing strategy.")

        valuation_gap = None
        if financials.get("implied_enterprise_value"):
            valuation_gap = financials["implied_enterprise_value"] - deal_value

        return {
            "missing_metrics": missing,
            "valuation_gap": valuation_gap,
            "recommendations": recommendations,
            "model_health": "attention" if recommendations else "healthy",
        }

    def _safe_enum(self, value: Any, enum_cls, default):
        if isinstance(value, enum_cls):
            return value
        if isinstance(value, str):
            try:
                return enum_cls(value)
            except ValueError:
                normalized = value.upper().replace("-", "_")
                try:
                    return enum_cls[normalized]
                except KeyError:
                    return default
        return default

    def _comment_thread_key(self, entity_type: str, entity_id: str) -> str:
        return f"{entity_type}:{entity_id}"

    def _serialize_dataclass(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, (KPI, RealtimeInsight, Alert)):
            data = asdict(value)
            for key, val in list(data.items()):
                if isinstance(val, datetime):
                    data[key] = val.isoformat()
            return data
        if isinstance(value, dict):
            return value
        return {"value": value}
