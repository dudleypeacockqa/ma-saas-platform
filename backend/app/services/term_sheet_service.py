"""
Term Sheet Service for M&A SaaS Platform
Comprehensive service for managing term sheets with templates and collaboration features
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session
import uuid
import json
from copy import deepcopy

from ..models.negotiations import (
    TermSheet, TermSheetTemplate, Negotiation,
    TermSheetStatus, DealStructureType
)
from ..models.user import User


class TermSheetService:
    """Service for managing term sheets with templates and collaboration features"""

    def __init__(self, db: Session):
        self.db = db

    def create_template(
        self,
        organization_id: str,
        name: str,
        description: Optional[str] = None,
        industry: Optional[str] = None,
        deal_type: Optional[DealStructureType] = None,
        template_structure: Dict[str, Any] = None,
        default_values: Dict[str, Any] = None,
        validation_rules: Dict[str, Any] = None,
        category: Optional[str] = None,
        is_public: bool = False,
        created_by_id: Optional[str] = None
    ) -> TermSheetTemplate:
        """
        Create a new term sheet template

        Args:
            organization_id: Tenant ID
            name: Template name
            description: Template description
            industry: Target industry
            deal_type: Type of deal structure
            template_structure: Template field definitions
            default_values: Default values for fields
            validation_rules: Field validation rules
            category: Template category
            is_public: Available to all organizations
            created_by_id: User creating the template

        Returns:
            Created template instance
        """
        if not template_structure:
            template_structure = self._get_default_template_structure(deal_type)

        template = TermSheetTemplate(
            organization_id=organization_id,
            name=name,
            description=description,
            industry=industry,
            deal_type=deal_type,
            template_structure=template_structure,
            default_values=default_values or {},
            validation_rules=validation_rules or {},
            category=category,
            is_public=is_public,
            created_by=created_by_id
        )

        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)

        return template

    def create_term_sheet_from_template(
        self,
        negotiation_id: str,
        template_id: str,
        title: str,
        custom_terms: Optional[Dict[str, Any]] = None,
        purchase_price: Optional[Decimal] = None,
        currency: str = "USD",
        effective_date: Optional[date] = None,
        expiration_date: Optional[date] = None,
        created_by_id: Optional[str] = None
    ) -> TermSheet:
        """
        Create a term sheet from a template

        Args:
            negotiation_id: Associated negotiation ID
            template_id: Template to use
            title: Term sheet title
            custom_terms: Custom term values to override template defaults
            purchase_price: Purchase price
            currency: Currency code
            effective_date: Effective date
            expiration_date: Expiration date
            created_by_id: User creating the term sheet

        Returns:
            Created term sheet instance
        """
        template = self.get_template_by_id(template_id)
        if not template:
            raise ValueError("Template not found")

        negotiation = (
            self.db.query(Negotiation)
            .filter(Negotiation.id == negotiation_id)
            .first()
        )
        if not negotiation:
            raise ValueError("Negotiation not found")

        # Merge template defaults with custom terms
        terms = deepcopy(template.default_values)
        if custom_terms:
            terms.update(custom_terms)

        # Extract financial terms for easy querying
        cash_consideration = terms.get('cash_consideration')
        stock_consideration = terms.get('stock_consideration')
        earnout_amount = terms.get('earnout_consideration')

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
            cash_consideration=cash_consideration,
            stock_consideration=stock_consideration,
            earnout_amount=earnout_amount,
            effective_date=effective_date,
            expiration_date=expiration_date,
            created_by=created_by_id
        )

        self.db.add(term_sheet)

        # Update template usage
        template.usage_count += 1
        template.last_used_date = datetime.utcnow()

        self.db.commit()
        self.db.refresh(term_sheet)

        return term_sheet

    def update_term_sheet(
        self,
        term_sheet_id: str,
        organization_id: str,
        updates: Dict[str, Any],
        create_new_version: bool = False,
        change_summary: Optional[str] = None,
        updated_by_id: Optional[str] = None
    ) -> TermSheet:
        """
        Update a term sheet with optional versioning

        Args:
            term_sheet_id: Term sheet ID to update
            organization_id: Tenant ID for security
            updates: Dictionary of field updates
            create_new_version: Whether to create a new version
            change_summary: Summary of changes
            updated_by_id: User making the update

        Returns:
            Updated or new term sheet instance
        """
        term_sheet = (
            self.db.query(TermSheet)
            .filter(
                TermSheet.id == term_sheet_id,
                TermSheet.organization_id == organization_id
            )
            .first()
        )

        if not term_sheet:
            raise ValueError("Term sheet not found")

        if create_new_version:
            # Create new version
            new_version_num = self._increment_version(term_sheet.version)

            new_term_sheet = TermSheet(
                organization_id=term_sheet.organization_id,
                negotiation_id=term_sheet.negotiation_id,
                template_id=term_sheet.template_id,
                title=term_sheet.title,
                version=new_version_num,
                terms=deepcopy(term_sheet.terms),
                purchase_price=term_sheet.purchase_price,
                currency=term_sheet.currency,
                cash_consideration=term_sheet.cash_consideration,
                stock_consideration=term_sheet.stock_consideration,
                earnout_amount=term_sheet.earnout_amount,
                effective_date=term_sheet.effective_date,
                expiration_date=term_sheet.expiration_date,
                previous_version_id=term_sheet.id,
                change_summary=change_summary,
                created_by=updated_by_id
            )

            # Apply updates to new version
            for field, value in updates.items():
                if hasattr(new_term_sheet, field):
                    setattr(new_term_sheet, field, value)

            # Update financial fields if terms changed
            if 'terms' in updates:
                terms = new_term_sheet.terms
                new_term_sheet.cash_consideration = terms.get('cash_consideration')
                new_term_sheet.stock_consideration = terms.get('stock_consideration')
                new_term_sheet.earnout_amount = terms.get('earnout_consideration')

            self.db.add(new_term_sheet)

            # Update negotiation to point to new version
            negotiation = new_term_sheet.negotiation
            negotiation.current_term_sheet_id = new_term_sheet.id

            self.db.commit()
            self.db.refresh(new_term_sheet)

            return new_term_sheet
        else:
            # Update existing version
            for field, value in updates.items():
                if hasattr(term_sheet, field):
                    setattr(term_sheet, field, value)

            # Update financial fields if terms changed
            if 'terms' in updates:
                terms = term_sheet.terms
                term_sheet.cash_consideration = terms.get('cash_consideration')
                term_sheet.stock_consideration = terms.get('stock_consideration')
                term_sheet.earnout_amount = terms.get('earnout_consideration')

            term_sheet.updated_by = updated_by_id
            self.db.commit()
            self.db.refresh(term_sheet)

            return term_sheet

    def collaborate_on_term_sheet(
        self,
        term_sheet_id: str,
        organization_id: str,
        field_path: str,
        new_value: Any,
        user_id: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Real-time collaboration on term sheet fields

        Args:
            term_sheet_id: Term sheet ID
            organization_id: Tenant ID for security
            field_path: Dot notation path to field (e.g., 'purchase_price', 'terms.closing_conditions')
            new_value: New value for the field
            user_id: User making the change
            comment: Optional comment about the change

        Returns:
            Dictionary with change details
        """
        term_sheet = (
            self.db.query(TermSheet)
            .filter(
                TermSheet.id == term_sheet_id,
                TermSheet.organization_id == organization_id
            )
            .first()
        )

        if not term_sheet:
            raise ValueError("Term sheet not found")

        # Get old value
        old_value = self._get_field_value(term_sheet, field_path)

        # Set new value
        self._set_field_value(term_sheet, field_path, new_value)

        # Create change record
        change_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'field_path': field_path,
            'old_value': old_value,
            'new_value': new_value,
            'comment': comment
        }

        # Add to custom_fields for change tracking
        if not term_sheet.custom_fields:
            term_sheet.custom_fields = {}
        if 'collaboration_history' not in term_sheet.custom_fields:
            term_sheet.custom_fields['collaboration_history'] = []

        term_sheet.custom_fields['collaboration_history'].append(change_record)

        # Update financial fields if applicable
        if field_path in ['purchase_price', 'terms.cash_consideration', 'terms.stock_consideration']:
            self._update_financial_fields(term_sheet)

        term_sheet.updated_by = user_id
        self.db.commit()

        return change_record

    def compare_term_sheets(
        self,
        term_sheet1_id: str,
        term_sheet2_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Compare two term sheets and highlight differences

        Args:
            term_sheet1_id: First term sheet ID
            term_sheet2_id: Second term sheet ID
            organization_id: Tenant ID for security

        Returns:
            Dictionary with comparison results
        """
        term_sheet1 = (
            self.db.query(TermSheet)
            .filter(
                TermSheet.id == term_sheet1_id,
                TermSheet.organization_id == organization_id
            )
            .first()
        )

        term_sheet2 = (
            self.db.query(TermSheet)
            .filter(
                TermSheet.id == term_sheet2_id,
                TermSheet.organization_id == organization_id
            )
            .first()
        )

        if not term_sheet1 or not term_sheet2:
            raise ValueError("One or both term sheets not found")

        differences = []

        # Compare basic fields
        basic_fields = ['purchase_price', 'currency', 'cash_consideration',
                       'stock_consideration', 'earnout_amount', 'effective_date', 'expiration_date']

        for field in basic_fields:
            value1 = getattr(term_sheet1, field)
            value2 = getattr(term_sheet2, field)
            if value1 != value2:
                differences.append({
                    'field': field,
                    'term_sheet1_value': str(value1) if value1 else None,
                    'term_sheet2_value': str(value2) if value2 else None,
                    'type': 'basic_field'
                })

        # Compare terms (nested comparison)
        term_differences = self._compare_nested_dict(
            term_sheet1.terms or {},
            term_sheet2.terms or {},
            'terms'
        )
        differences.extend(term_differences)

        return {
            'term_sheet1': {
                'id': term_sheet1.id,
                'title': term_sheet1.title,
                'version': term_sheet1.version
            },
            'term_sheet2': {
                'id': term_sheet2.id,
                'title': term_sheet2.title,
                'version': term_sheet2.version
            },
            'differences_count': len(differences),
            'differences': differences,
            'comparison_date': datetime.utcnow().isoformat()
        }

    def validate_term_sheet(
        self,
        term_sheet_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Validate a term sheet against template rules and business logic

        Args:
            term_sheet_id: Term sheet ID
            organization_id: Tenant ID for security

        Returns:
            Dictionary with validation results
        """
        term_sheet = (
            self.db.query(TermSheet)
            .filter(
                TermSheet.id == term_sheet_id,
                TermSheet.organization_id == organization_id
            )
            .first()
        )

        if not term_sheet:
            raise ValueError("Term sheet not found")

        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }

        # Template validation if template exists
        if term_sheet.template_id:
            template = self.get_template_by_id(term_sheet.template_id)
            if template and template.validation_rules:
                template_validation = self._validate_against_template(
                    term_sheet.terms,
                    template.validation_rules
                )
                validation_results['errors'].extend(template_validation.get('errors', []))
                validation_results['warnings'].extend(template_validation.get('warnings', []))

        # Business logic validation
        business_validation = self._validate_business_logic(term_sheet)
        validation_results['errors'].extend(business_validation.get('errors', []))
        validation_results['warnings'].extend(business_validation.get('warnings', []))
        validation_results['suggestions'].extend(business_validation.get('suggestions', []))

        # Set overall validity
        validation_results['is_valid'] = len(validation_results['errors']) == 0

        return validation_results

    def get_term_sheet_analytics(
        self,
        organization_id: str,
        negotiation_id: Optional[str] = None,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """
        Get analytics for term sheets

        Args:
            organization_id: Tenant ID
            negotiation_id: Optional filter by negotiation
            days_back: Days to look back for analytics

        Returns:
            Dictionary with analytics data
        """
        start_date = datetime.utcnow() - timedelta(days=days_back)

        query = (
            self.db.query(TermSheet)
            .filter(
                TermSheet.organization_id == organization_id,
                TermSheet.created_at >= start_date
            )
        )

        if negotiation_id:
            query = query.filter(TermSheet.negotiation_id == negotiation_id)

        term_sheets = query.all()

        # Status breakdown
        status_breakdown = {}
        for status in TermSheetStatus:
            status_breakdown[status.value] = sum(
                1 for ts in term_sheets if ts.status == status
            )

        # Template usage
        template_usage = {}
        for ts in term_sheets:
            if ts.template_id:
                template = self.get_template_by_id(ts.template_id)
                template_name = template.name if template else "Unknown"
                template_usage[template_name] = template_usage.get(template_name, 0) + 1

        # Version analysis
        version_counts = {}
        for ts in term_sheets:
            # Count how many versions exist for each negotiation
            negotiation_id = ts.negotiation_id
            if negotiation_id not in version_counts:
                version_count = (
                    self.db.query(func.count(TermSheet.id))
                    .filter(TermSheet.negotiation_id == negotiation_id)
                    .scalar()
                )
                version_counts[negotiation_id] = version_count

        avg_versions_per_negotiation = (
            sum(version_counts.values()) / len(version_counts)
            if version_counts else 0
        )

        # Financial analysis
        financial_stats = self._calculate_financial_stats(term_sheets)

        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().isoformat(),
                'days': days_back
            },
            'summary': {
                'total_term_sheets': len(term_sheets),
                'active_negotiations': len(set(ts.negotiation_id for ts in term_sheets)),
                'avg_versions_per_negotiation': round(avg_versions_per_negotiation, 1)
            },
            'status_breakdown': status_breakdown,
            'template_usage': template_usage,
            'financial_stats': financial_stats
        }

    def get_template_by_id(
        self,
        template_id: str,
        organization_id: Optional[str] = None
    ) -> Optional[TermSheetTemplate]:
        """Get template by ID with optional tenant filtering"""
        query = self.db.query(TermSheetTemplate).filter(TermSheetTemplate.id == template_id)

        if organization_id:
            # Include public templates and organization-specific templates
            query = query.filter(
                or_(
                    TermSheetTemplate.organization_id == organization_id,
                    TermSheetTemplate.is_public == True
                )
            )

        return query.first()

    def list_templates(
        self,
        organization_id: str,
        industry: Optional[str] = None,
        deal_type: Optional[DealStructureType] = None,
        category: Optional[str] = None,
        include_public: bool = True
    ) -> List[TermSheetTemplate]:
        """
        List available templates with filtering

        Args:
            organization_id: Tenant ID
            industry: Filter by industry
            deal_type: Filter by deal type
            category: Filter by category
            include_public: Include public templates

        Returns:
            List of templates
        """
        query = self.db.query(TermSheetTemplate).filter(
            TermSheetTemplate.is_active == True
        )

        # Filter by organization or public
        if include_public:
            query = query.filter(
                or_(
                    TermSheetTemplate.organization_id == organization_id,
                    TermSheetTemplate.is_public == True
                )
            )
        else:
            query = query.filter(TermSheetTemplate.organization_id == organization_id)

        if industry:
            query = query.filter(TermSheetTemplate.industry == industry)

        if deal_type:
            query = query.filter(TermSheetTemplate.deal_type == deal_type)

        if category:
            query = query.filter(TermSheetTemplate.category == category)

        return query.order_by(TermSheetTemplate.usage_count.desc()).all()

    def _get_default_template_structure(self, deal_type: Optional[DealStructureType]) -> Dict[str, Any]:
        """Get default template structure based on deal type"""
        base_structure = {
            'purchase_price': {'type': 'decimal', 'required': True, 'label': 'Purchase Price'},
            'currency': {'type': 'string', 'required': True, 'default': 'USD', 'label': 'Currency'},
            'closing_date': {'type': 'date', 'required': True, 'label': 'Expected Closing Date'},
            'due_diligence_period': {'type': 'integer', 'default': 45, 'label': 'Due Diligence Period (days)'},
            'financing_contingency': {'type': 'boolean', 'default': True, 'label': 'Financing Contingency'},
            'breakup_fee': {'type': 'decimal', 'label': 'Breakup Fee'},
            'representations_warranties': {'type': 'text', 'label': 'Key Representations & Warranties'},
            'closing_conditions': {'type': 'text', 'label': 'Closing Conditions'}
        }

        if deal_type == DealStructureType.ASSET_PURCHASE:
            base_structure.update({
                'assets_included': {'type': 'text', 'required': True, 'label': 'Assets Included'},
                'liabilities_assumed': {'type': 'text', 'label': 'Liabilities Assumed'},
                'working_capital_adjustment': {'type': 'boolean', 'default': True, 'label': 'Working Capital Adjustment'}
            })
        elif deal_type == DealStructureType.STOCK_PURCHASE:
            base_structure.update({
                'shares_percentage': {'type': 'decimal', 'required': True, 'label': 'Percentage of Shares'},
                'board_representation': {'type': 'text', 'label': 'Board Representation'},
                'drag_along_rights': {'type': 'boolean', 'default': True, 'label': 'Drag-Along Rights'},
                'tag_along_rights': {'type': 'boolean', 'default': True, 'label': 'Tag-Along Rights'}
            })

        return base_structure

    def _increment_version(self, current_version: str) -> str:
        """Increment version number"""
        try:
            major, minor = current_version.split('.')
            return f"{major}.{int(minor) + 1}"
        except:
            return "1.1"

    def _get_field_value(self, term_sheet: TermSheet, field_path: str) -> Any:
        """Get field value using dot notation"""
        if '.' in field_path:
            parts = field_path.split('.')
            if parts[0] == 'terms':
                return term_sheet.terms.get(parts[1]) if term_sheet.terms else None
            else:
                return getattr(term_sheet, parts[0], None)
        else:
            return getattr(term_sheet, field_path, None)

    def _set_field_value(self, term_sheet: TermSheet, field_path: str, value: Any) -> None:
        """Set field value using dot notation"""
        if '.' in field_path:
            parts = field_path.split('.')
            if parts[0] == 'terms':
                if not term_sheet.terms:
                    term_sheet.terms = {}
                term_sheet.terms[parts[1]] = value
            else:
                setattr(term_sheet, parts[0], value)
        else:
            setattr(term_sheet, field_path, value)

    def _update_financial_fields(self, term_sheet: TermSheet) -> None:
        """Update extracted financial fields"""
        if term_sheet.terms:
            term_sheet.cash_consideration = term_sheet.terms.get('cash_consideration')
            term_sheet.stock_consideration = term_sheet.terms.get('stock_consideration')
            term_sheet.earnout_amount = term_sheet.terms.get('earnout_consideration')

    def _compare_nested_dict(self, dict1: Dict, dict2: Dict, prefix: str) -> List[Dict]:
        """Compare nested dictionaries"""
        differences = []
        all_keys = set(dict1.keys()) | set(dict2.keys())

        for key in all_keys:
            field_path = f"{prefix}.{key}"
            value1 = dict1.get(key)
            value2 = dict2.get(key)

            if isinstance(value1, dict) and isinstance(value2, dict):
                differences.extend(self._compare_nested_dict(value1, value2, field_path))
            elif value1 != value2:
                differences.append({
                    'field': field_path,
                    'term_sheet1_value': value1,
                    'term_sheet2_value': value2,
                    'type': 'terms'
                })

        return differences

    def _validate_against_template(self, terms: Dict, validation_rules: Dict) -> Dict[str, List]:
        """Validate terms against template rules"""
        errors = []
        warnings = []

        for field, rules in validation_rules.items():
            value = terms.get(field)

            # Required field validation
            if rules.get('required', False) and not value:
                errors.append(f"Field '{field}' is required")

            # Type validation
            if value and 'type' in rules:
                expected_type = rules['type']
                if expected_type == 'decimal' and not isinstance(value, (int, float, Decimal)):
                    errors.append(f"Field '{field}' must be a number")
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"Field '{field}' must be true or false")

            # Range validation
            if value and isinstance(value, (int, float, Decimal)):
                if 'min' in rules and value < rules['min']:
                    warnings.append(f"Field '{field}' is below recommended minimum of {rules['min']}")
                if 'max' in rules and value > rules['max']:
                    warnings.append(f"Field '{field}' exceeds recommended maximum of {rules['max']}")

        return {'errors': errors, 'warnings': warnings}

    def _validate_business_logic(self, term_sheet: TermSheet) -> Dict[str, List]:
        """Validate business logic"""
        errors = []
        warnings = []
        suggestions = []

        # Check if total consideration adds up
        total_consideration = Decimal('0')
        if term_sheet.cash_consideration:
            total_consideration += term_sheet.cash_consideration
        if term_sheet.stock_consideration:
            total_consideration += term_sheet.stock_consideration
        if term_sheet.earnout_amount:
            total_consideration += term_sheet.earnout_amount

        if term_sheet.purchase_price and total_consideration:
            difference = abs(term_sheet.purchase_price - total_consideration)
            if difference > Decimal('0.01'):  # Allow for small rounding differences
                warnings.append(
                    f"Total consideration ({total_consideration}) doesn't match "
                    f"purchase price ({term_sheet.purchase_price})"
                )

        # Check expiration date
        if term_sheet.expiration_date and term_sheet.expiration_date <= datetime.utcnow().date():
            errors.append("Term sheet has expired")

        # Check if effective date is in the future for new term sheets
        if (term_sheet.effective_date and
            term_sheet.effective_date < datetime.utcnow().date() and
            term_sheet.status == TermSheetStatus.DRAFT):
            warnings.append("Effective date is in the past")

        # Suggest improvements
        if not term_sheet.earnout_amount and term_sheet.purchase_price:
            suggestions.append("Consider adding earnout provisions to share risk")

        return {
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _calculate_financial_stats(self, term_sheets: List[TermSheet]) -> Dict[str, Any]:
        """Calculate financial statistics for term sheets"""
        prices = [ts.purchase_price for ts in term_sheets if ts.purchase_price]

        if not prices:
            return {}

        return {
            'avg_purchase_price': float(sum(prices) / len(prices)),
            'min_purchase_price': float(min(prices)),
            'max_purchase_price': float(max(prices)),
            'total_deal_value': float(sum(prices)),
            'currency_breakdown': self._get_currency_breakdown(term_sheets)
        }

    def _get_currency_breakdown(self, term_sheets: List[TermSheet]) -> Dict[str, int]:
        """Get breakdown of currencies used"""
        currency_counts = {}
        for ts in term_sheets:
            currency = ts.currency or 'USD'
            currency_counts[currency] = currency_counts.get(currency, 0) + 1
        return currency_counts