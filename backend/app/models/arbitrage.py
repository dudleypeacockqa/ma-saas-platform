"""
M&A Arbitrage & Investment Strategy Models
Handles arbitrage opportunities, investment strategies, and portfolio optimization
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
from sqlalchemy import (
    Column, String, Boolean, ForeignKey, DateTime, Integer,
    Numeric, Date, Text, JSON, Float, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from .base import BaseModel, SoftDeleteMixin, MetadataMixin, AuditableMixin, generate_uuid


class DealStatus(str, Enum):
    """Status of announced M&A deal"""
    ANNOUNCED = "announced"
    REGULATORY_REVIEW = "regulatory_review"
    SHAREHOLDER_APPROVAL = "shareholder_approval"
    CLOSING_CONDITIONS = "closing_conditions"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    WITHDRAWN = "withdrawn"


class ArbitrageStrategy(str, Enum):
    """Type of arbitrage strategy"""
    MERGER_ARBITRAGE = "merger_arbitrage"
    CASH_DEAL = "cash_deal"
    STOCK_DEAL = "stock_deal"
    COLLAR_DEAL = "collar_deal"
    SPIN_OFF_ARBITRAGE = "spin_off_arbitrage"
    RISK_ARBITRAGE = "risk_arbitrage"
    PAIR_TRADING = "pair_trading"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PortfolioStrategy(str, Enum):
    """Portfolio allocation strategies"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    MARKET_NEUTRAL = "market_neutral"
    LONG_SHORT = "long_short"


class AnnouncedDeal(BaseModel, SoftDeleteMixin, MetadataMixin, AuditableMixin):
    """
    Tracks announced M&A deals for arbitrage analysis
    Integrates with opportunities system for deal sourcing
    """
    __tablename__ = "announced_deals"

    # Core Deal Information
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False)
    opportunity_id = Column(UUID(as_uuid=False), ForeignKey("market_opportunities.id"), nullable=True)

    # Deal Parties
    target_company = Column(String(255), nullable=False, comment="Target company name")
    acquirer_company = Column(String(255), nullable=False, comment="Acquiring company name")
    target_ticker = Column(String(20), nullable=True, comment="Target company ticker symbol")
    acquirer_ticker = Column(String(20), nullable=True, comment="Acquirer company ticker symbol")

    # Deal Terms
    deal_value = Column(Numeric(20, 2), nullable=True, comment="Total deal value in USD")
    price_per_share = Column(Numeric(10, 2), nullable=True, comment="Offer price per share")
    currency = Column(String(3), default="USD", comment="Deal currency")

    # Deal Structure
    deal_type = Column(String(50), nullable=False, comment="Cash, stock, or mixed deal")
    cash_component = Column(Numeric(5, 4), nullable=True, comment="Percentage of cash in deal")
    stock_component = Column(Numeric(5, 4), nullable=True, comment="Percentage of stock in deal")
    exchange_ratio = Column(Numeric(10, 6), nullable=True, comment="Stock exchange ratio")

    # Deal Timeline
    announcement_date = Column(Date, nullable=False, comment="Deal announcement date")
    expected_close_date = Column(Date, nullable=True, comment="Expected closing date")
    actual_close_date = Column(Date, nullable=True, comment="Actual closing date")
    deadline_date = Column(Date, nullable=True, comment="Deal deadline date")

    # Deal Status & Progress
    current_status = Column(String(50), nullable=False, default=DealStatus.ANNOUNCED)
    completion_probability = Column(Float, nullable=True, comment="Estimated probability of completion (0-1)")
    regulatory_approvals_required = Column(JSON, nullable=True, comment="List of required approvals")
    approvals_received = Column(JSON, nullable=True, comment="List of received approvals")

    # Market Data
    target_price_at_announcement = Column(Numeric(10, 2), nullable=True)
    current_target_price = Column(Numeric(10, 2), nullable=True)
    acquirer_price_at_announcement = Column(Numeric(10, 2), nullable=True)
    current_acquirer_price = Column(Numeric(10, 2), nullable=True)

    # Spread Analysis
    gross_spread = Column(Numeric(10, 2), nullable=True, comment="Gross arbitrage spread")
    gross_spread_percentage = Column(Numeric(5, 4), nullable=True, comment="Gross spread as percentage")
    risk_adjusted_spread = Column(Numeric(10, 2), nullable=True, comment="Risk-adjusted spread")
    annualized_return = Column(Numeric(5, 4), nullable=True, comment="Annualized expected return")

    # Risk Metrics
    deal_break_risk = Column(String(20), default=RiskLevel.MEDIUM)
    regulatory_risk = Column(String(20), default=RiskLevel.MEDIUM)
    financing_risk = Column(String(20), default=RiskLevel.LOW)
    market_risk = Column(String(20), default=RiskLevel.MEDIUM)
    overall_risk_score = Column(Float, nullable=True, comment="Overall risk score (0-100)")

    # External References
    sec_filing_urls = Column(JSON, nullable=True, comment="SEC filing URLs")
    press_release_url = Column(String(500), nullable=True)
    deal_description = Column(Text, nullable=True)

    # Data Sources
    data_source = Column(String(100), nullable=True, comment="Primary data source")
    last_updated_market_data = Column(DateTime, nullable=True)

    # Relationships
    arbitrage_positions = relationship("ArbitragePosition", back_populates="announced_deal")
    deal_updates = relationship("DealUpdate", back_populates="announced_deal")

    # Indexes
    __table_args__ = (
        Index("idx_announced_deals_org_status", "organization_id", "current_status"),
        Index("idx_announced_deals_tickers", "target_ticker", "acquirer_ticker"),
        Index("idx_announced_deals_timeline", "announcement_date", "expected_close_date"),
        Index("idx_announced_deals_spread", "gross_spread_percentage", "annualized_return"),
    )

    @validates('completion_probability')
    def validate_probability(self, key, value):
        if value is not None and (value < 0 or value > 1):
            raise ValueError("Completion probability must be between 0 and 1")
        return value

    @property
    def days_to_close(self) -> Optional[int]:
        """Calculate days until expected close"""
        if self.expected_close_date:
            return (self.expected_close_date - date.today()).days
        return None

    @property
    def days_since_announcement(self) -> int:
        """Calculate days since announcement"""
        return (date.today() - self.announcement_date).days

    def __repr__(self):
        return f"<AnnouncedDeal {self.target_company} <- {self.acquirer_company} ({self.current_status})>"


class ArbitragePosition(BaseModel, SoftDeleteMixin, MetadataMixin, AuditableMixin):
    """
    Tracks arbitrage positions in announced deals
    Links to portfolio management and performance tracking
    """
    __tablename__ = "arbitrage_positions"

    # Position Identifiers
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False)
    announced_deal_id = Column(UUID(as_uuid=False), ForeignKey("announced_deals.id"), nullable=False)
    portfolio_id = Column(UUID(as_uuid=False), ForeignKey("investment_portfolios.id"), nullable=True)

    # Position Details
    strategy = Column(String(50), nullable=False, default=ArbitrageStrategy.MERGER_ARBITRAGE)
    position_name = Column(String(255), nullable=False, comment="Internal position name")

    # Position Sizing
    target_shares = Column(Integer, nullable=True, comment="Long position in target shares")
    acquirer_shares = Column(Integer, nullable=True, comment="Short position in acquirer shares")
    notional_value = Column(Numeric(15, 2), nullable=False, comment="Total position notional value")
    capital_allocated = Column(Numeric(15, 2), nullable=False, comment="Capital allocated to position")

    # Entry Details
    entry_date = Column(Date, nullable=False, comment="Position entry date")
    target_entry_price = Column(Numeric(10, 2), nullable=True)
    acquirer_entry_price = Column(Numeric(10, 2), nullable=True)
    entry_spread = Column(Numeric(10, 2), nullable=True, comment="Spread at entry")
    entry_spread_percentage = Column(Numeric(5, 4), nullable=True)

    # Current Position
    current_target_price = Column(Numeric(10, 2), nullable=True)
    current_acquirer_price = Column(Numeric(10, 2), nullable=True)
    current_spread = Column(Numeric(10, 2), nullable=True)
    current_spread_percentage = Column(Numeric(5, 4), nullable=True)

    # P&L Tracking
    unrealized_pnl = Column(Numeric(15, 2), nullable=True, comment="Unrealized P&L")
    realized_pnl = Column(Numeric(15, 2), default=0, comment="Realized P&L")
    total_pnl = Column(Numeric(15, 2), nullable=True, comment="Total P&L")
    pnl_percentage = Column(Numeric(5, 4), nullable=True, comment="P&L as percentage of capital")

    # Risk Management
    stop_loss_level = Column(Numeric(10, 2), nullable=True, comment="Stop loss price level")
    max_loss_limit = Column(Numeric(15, 2), nullable=True, comment="Maximum loss limit")
    position_risk_score = Column(Float, nullable=True, comment="Position risk score")

    # Position Status
    is_active = Column(Boolean, default=True, comment="Position is currently active")
    exit_date = Column(Date, nullable=True, comment="Position exit date")
    exit_reason = Column(String(100), nullable=True, comment="Reason for position exit")

    # Hedging
    is_hedged = Column(Boolean, default=False, comment="Position is hedged")
    hedge_ratio = Column(Numeric(5, 4), nullable=True, comment="Hedge ratio")
    hedge_instruments = Column(JSON, nullable=True, comment="Hedging instruments used")

    # Performance Metrics
    holding_period_return = Column(Numeric(5, 4), nullable=True)
    annualized_return = Column(Numeric(5, 4), nullable=True)
    sharpe_ratio = Column(Numeric(5, 4), nullable=True)
    max_drawdown = Column(Numeric(5, 4), nullable=True)

    # Trade Execution
    execution_notes = Column(Text, nullable=True)
    broker_commissions = Column(Numeric(10, 2), default=0, comment="Total broker commissions")
    other_costs = Column(Numeric(10, 2), default=0, comment="Other transaction costs")

    # Relationships
    announced_deal = relationship("AnnouncedDeal", back_populates="arbitrage_positions")
    portfolio = relationship("InvestmentPortfolio", back_populates="arbitrage_positions")
    trade_executions = relationship("TradeExecution", back_populates="arbitrage_position")

    # Indexes
    __table_args__ = (
        Index("idx_arbitrage_positions_org_active", "organization_id", "is_active"),
        Index("idx_arbitrage_positions_deal", "announced_deal_id"),
        Index("idx_arbitrage_positions_portfolio", "portfolio_id"),
        Index("idx_arbitrage_positions_entry_date", "entry_date"),
        Index("idx_arbitrage_positions_pnl", "total_pnl", "pnl_percentage"),
    )

    @property
    def days_held(self) -> int:
        """Calculate days position has been held"""
        end_date = self.exit_date or date.today()
        return (end_date - self.entry_date).days

    def update_pnl(self):
        """Update P&L calculations based on current prices"""
        if self.current_target_price and self.target_entry_price and self.target_shares:
            target_pnl = (self.current_target_price - self.target_entry_price) * self.target_shares
        else:
            target_pnl = 0

        if self.current_acquirer_price and self.acquirer_entry_price and self.acquirer_shares:
            acquirer_pnl = (self.acquirer_entry_price - self.current_acquirer_price) * self.acquirer_shares
        else:
            acquirer_pnl = 0

        self.unrealized_pnl = target_pnl + acquirer_pnl
        self.total_pnl = self.unrealized_pnl + self.realized_pnl

        if self.capital_allocated:
            self.pnl_percentage = self.total_pnl / self.capital_allocated

    def __repr__(self):
        return f"<ArbitragePosition {self.position_name} ({self.strategy})>"


class InvestmentPortfolio(BaseModel, SoftDeleteMixin, MetadataMixin, AuditableMixin):
    """
    Investment portfolio for M&A arbitrage strategies
    Manages allocation, risk, and performance across positions
    """
    __tablename__ = "investment_portfolios"

    # Portfolio Identifiers
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False)
    portfolio_name = Column(String(255), nullable=False, comment="Portfolio name")
    portfolio_description = Column(Text, nullable=True)

    # Portfolio Strategy
    strategy_type = Column(String(50), nullable=False, default=PortfolioStrategy.BALANCED)
    investment_objective = Column(Text, nullable=True)
    benchmark_index = Column(String(50), nullable=True, comment="Benchmark for comparison")

    # Capital Management
    initial_capital = Column(Numeric(20, 2), nullable=False, comment="Initial portfolio capital")
    current_capital = Column(Numeric(20, 2), nullable=False, comment="Current portfolio capital")
    available_capital = Column(Numeric(20, 2), nullable=False, comment="Available for new positions")
    committed_capital = Column(Numeric(20, 2), nullable=False, comment="Capital in active positions")

    # Risk Management
    max_position_size = Column(Numeric(5, 4), default=0.1, comment="Max position size as % of portfolio")
    max_sector_exposure = Column(Numeric(5, 4), default=0.3, comment="Max sector exposure")
    max_single_deal_exposure = Column(Numeric(5, 4), default=0.05, comment="Max exposure to single deal")
    risk_tolerance = Column(String(20), default=RiskLevel.MEDIUM)

    # Performance Tracking
    total_return = Column(Numeric(5, 4), nullable=True, comment="Total portfolio return")
    annualized_return = Column(Numeric(5, 4), nullable=True, comment="Annualized return")
    sharpe_ratio = Column(Numeric(5, 4), nullable=True, comment="Risk-adjusted return metric")
    max_drawdown = Column(Numeric(5, 4), nullable=True, comment="Maximum drawdown")
    win_rate = Column(Numeric(5, 4), nullable=True, comment="Percentage of winning positions")

    # Portfolio Metrics
    number_of_positions = Column(Integer, default=0, comment="Current number of positions")
    average_position_size = Column(Numeric(15, 2), nullable=True)
    portfolio_beta = Column(Numeric(5, 4), nullable=True, comment="Portfolio beta to market")
    correlation_to_market = Column(Numeric(5, 4), nullable=True)

    # Sector Allocation
    sector_allocation = Column(JSON, nullable=True, comment="Current sector allocation")
    geographic_allocation = Column(JSON, nullable=True, comment="Geographic allocation")
    strategy_allocation = Column(JSON, nullable=True, comment="Allocation by arbitrage strategy")

    # Portfolio Status
    is_active = Column(Boolean, default=True, comment="Portfolio is active")
    inception_date = Column(Date, nullable=False, comment="Portfolio inception date")
    last_rebalance_date = Column(Date, nullable=True)

    # Risk Monitoring
    var_95 = Column(Numeric(15, 2), nullable=True, comment="Value at Risk (95%)")
    expected_shortfall = Column(Numeric(15, 2), nullable=True, comment="Expected shortfall")
    risk_budget_utilization = Column(Numeric(5, 4), nullable=True)

    # Performance Attribution
    alpha_generation = Column(Numeric(5, 4), nullable=True, comment="Alpha generated")
    beta_exposure = Column(Numeric(5, 4), nullable=True, comment="Beta exposure")
    idiosyncratic_risk = Column(Numeric(5, 4), nullable=True)

    # Relationships
    arbitrage_positions = relationship("ArbitragePosition", back_populates="portfolio")
    portfolio_snapshots = relationship("PortfolioSnapshot", back_populates="portfolio")
    rebalancing_actions = relationship("PortfolioRebalancing", back_populates="portfolio")

    # Indexes
    __table_args__ = (
        Index("idx_investment_portfolios_org", "organization_id"),
        Index("idx_investment_portfolios_strategy", "strategy_type"),
        Index("idx_investment_portfolios_performance", "total_return", "sharpe_ratio"),
        Index("idx_investment_portfolios_active", "is_active", "inception_date"),
    )

    def calculate_metrics(self):
        """Calculate portfolio performance metrics"""
        # Implementation would calculate various portfolio metrics
        # based on current positions and historical performance
        pass

    def check_risk_limits(self) -> Dict[str, bool]:
        """Check if portfolio is within risk limits"""
        risk_checks = {
            "position_size_limit": True,  # Check max position size
            "sector_exposure_limit": True,  # Check sector limits
            "single_deal_limit": True,  # Check single deal exposure
            "overall_risk_limit": True  # Check overall risk metrics
        }
        return risk_checks

    def __repr__(self):
        return f"<InvestmentPortfolio {self.portfolio_name} ({self.strategy_type})>"


class DealUpdate(BaseModel, MetadataMixin):
    """
    Tracks updates and news for announced deals
    Feeds into risk assessment and completion probability models
    """
    __tablename__ = "deal_updates"

    # Update Identifiers
    announced_deal_id = Column(UUID(as_uuid=False), ForeignKey("announced_deals.id"), nullable=False)

    # Update Details
    update_type = Column(String(50), nullable=False, comment="Type of update")
    update_title = Column(String(500), nullable=False)
    update_content = Column(Text, nullable=False)
    update_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Impact Assessment
    impact_on_probability = Column(Numeric(5, 4), nullable=True, comment="Impact on completion probability")
    impact_on_timeline = Column(Integer, nullable=True, comment="Impact on timeline (days)")
    impact_on_spread = Column(Numeric(10, 2), nullable=True, comment="Impact on arbitrage spread")
    sentiment_score = Column(Numeric(5, 4), nullable=True, comment="Sentiment score (-1 to 1)")

    # Source Information
    source_url = Column(String(500), nullable=True)
    source_type = Column(String(50), nullable=True, comment="News, SEC filing, press release, etc.")
    source_credibility = Column(Numeric(5, 4), nullable=True, comment="Source credibility score")

    # Categorization
    regulatory_related = Column(Boolean, default=False)
    financing_related = Column(Boolean, default=False)
    shareholder_related = Column(Boolean, default=False)
    competitive_related = Column(Boolean, default=False)

    # AI Analysis
    ai_summary = Column(Text, nullable=True, comment="AI-generated summary")
    key_entities = Column(JSON, nullable=True, comment="Extracted entities")
    risk_keywords = Column(JSON, nullable=True, comment="Risk-related keywords found")

    # Relationships
    announced_deal = relationship("AnnouncedDeal", back_populates="deal_updates")

    # Indexes
    __table_args__ = (
        Index("idx_deal_updates_deal_date", "announced_deal_id", "update_date"),
        Index("idx_deal_updates_type", "update_type", "regulatory_related"),
        Index("idx_deal_updates_impact", "impact_on_probability", "sentiment_score"),
    )

    def __repr__(self):
        return f"<DealUpdate {self.update_title[:50]}...>"


class TradeExecution(BaseModel, MetadataMixin):
    """
    Records individual trade executions for arbitrage positions
    Tracks execution quality and transaction costs
    """
    __tablename__ = "trade_executions"

    # Execution Identifiers
    arbitrage_position_id = Column(UUID(as_uuid=False), ForeignKey("arbitrage_positions.id"), nullable=False)
    trade_id = Column(String(100), nullable=False, comment="Broker trade ID")

    # Trade Details
    security_type = Column(String(20), nullable=False, comment="Stock, option, future, etc.")
    symbol = Column(String(20), nullable=False, comment="Trading symbol")
    side = Column(String(10), nullable=False, comment="BUY or SELL")
    quantity = Column(Integer, nullable=False, comment="Number of shares/contracts")
    price = Column(Numeric(10, 4), nullable=False, comment="Execution price")

    # Execution Timing
    order_time = Column(DateTime, nullable=False, comment="Order placement time")
    execution_time = Column(DateTime, nullable=False, comment="Execution time")
    settlement_date = Column(Date, nullable=False, comment="Settlement date")

    # Execution Quality
    execution_venue = Column(String(50), nullable=True, comment="Execution venue")
    market_price = Column(Numeric(10, 4), nullable=True, comment="Market price at execution")
    price_improvement = Column(Numeric(10, 4), nullable=True, comment="Price improvement achieved")
    slippage = Column(Numeric(10, 4), nullable=True, comment="Execution slippage")

    # Costs
    gross_amount = Column(Numeric(15, 2), nullable=False, comment="Gross trade amount")
    commission = Column(Numeric(10, 2), nullable=False, comment="Broker commission")
    sec_fee = Column(Numeric(10, 2), default=0, comment="SEC fee")
    other_fees = Column(Numeric(10, 2), default=0, comment="Other fees")
    net_amount = Column(Numeric(15, 2), nullable=False, comment="Net trade amount")

    # Order Management
    order_type = Column(String(20), nullable=False, comment="Market, limit, stop, etc.")
    time_in_force = Column(String(10), nullable=False, comment="DAY, GTC, etc.")
    original_quantity = Column(Integer, nullable=False, comment="Original order quantity")
    fill_status = Column(String(20), nullable=False, comment="FILLED, PARTIAL, CANCELLED")

    # Relationships
    arbitrage_position = relationship("ArbitragePosition", back_populates="trade_executions")

    # Indexes
    __table_args__ = (
        Index("idx_trade_executions_position", "arbitrage_position_id"),
        Index("idx_trade_executions_symbol_time", "symbol", "execution_time"),
        Index("idx_trade_executions_settlement", "settlement_date"),
    )

    @property
    def execution_speed(self) -> int:
        """Calculate execution speed in milliseconds"""
        if self.order_time and self.execution_time:
            delta = self.execution_time - self.order_time
            return int(delta.total_seconds() * 1000)
        return 0

    def __repr__(self):
        return f"<TradeExecution {self.symbol} {self.side} {self.quantity}@{self.price}>"


class PortfolioSnapshot(BaseModel, MetadataMixin):
    """
    Daily snapshots of portfolio performance and risk metrics
    Enables time-series analysis and performance tracking
    """
    __tablename__ = "portfolio_snapshots"

    # Snapshot Identifiers
    portfolio_id = Column(UUID(as_uuid=False), ForeignKey("investment_portfolios.id"), nullable=False)
    snapshot_date = Column(Date, nullable=False, comment="Date of snapshot")

    # Portfolio Values
    total_value = Column(Numeric(20, 2), nullable=False, comment="Total portfolio value")
    cash_balance = Column(Numeric(20, 2), nullable=False, comment="Cash balance")
    position_value = Column(Numeric(20, 2), nullable=False, comment="Total position value")
    unrealized_pnl = Column(Numeric(20, 2), nullable=False, comment="Unrealized P&L")
    realized_pnl = Column(Numeric(20, 2), nullable=False, comment="Realized P&L")

    # Performance Metrics
    daily_return = Column(Numeric(5, 4), nullable=True, comment="Daily return")
    cumulative_return = Column(Numeric(5, 4), nullable=True, comment="Cumulative return")
    volatility = Column(Numeric(5, 4), nullable=True, comment="Annualized volatility")
    sharpe_ratio = Column(Numeric(5, 4), nullable=True, comment="Sharpe ratio")

    # Risk Metrics
    var_95 = Column(Numeric(15, 2), nullable=True, comment="Value at Risk (95%)")
    expected_shortfall = Column(Numeric(15, 2), nullable=True, comment="Expected shortfall")
    beta = Column(Numeric(5, 4), nullable=True, comment="Portfolio beta")
    correlation_to_market = Column(Numeric(5, 4), nullable=True)

    # Position Metrics
    number_of_positions = Column(Integer, nullable=False, comment="Number of active positions")
    average_position_size = Column(Numeric(15, 2), nullable=True)
    largest_position_size = Column(Numeric(15, 2), nullable=True)
    concentration_ratio = Column(Numeric(5, 4), nullable=True, comment="Top 5 positions concentration")

    # Market Environment
    market_return = Column(Numeric(5, 4), nullable=True, comment="Market return for the day")
    risk_free_rate = Column(Numeric(5, 4), nullable=True, comment="Risk-free rate")
    volatility_index = Column(Numeric(5, 4), nullable=True, comment="Market volatility index")

    # Sector/Strategy Breakdown
    sector_exposures = Column(JSON, nullable=True, comment="Sector exposure breakdown")
    strategy_exposures = Column(JSON, nullable=True, comment="Strategy exposure breakdown")
    geographic_exposures = Column(JSON, nullable=True, comment="Geographic exposure breakdown")

    # Relationships
    portfolio = relationship("InvestmentPortfolio", back_populates="portfolio_snapshots")

    # Indexes
    __table_args__ = (
        Index("idx_portfolio_snapshots_portfolio_date", "portfolio_id", "snapshot_date"),
        Index("idx_portfolio_snapshots_date", "snapshot_date"),
        Index("idx_portfolio_snapshots_performance", "daily_return", "cumulative_return"),
    )

    def __repr__(self):
        return f"<PortfolioSnapshot {self.portfolio_id} {self.snapshot_date}>"


class PortfolioRebalancing(BaseModel, MetadataMixin):
    """
    Records portfolio rebalancing actions and their rationale
    Tracks optimization decisions and their outcomes
    """
    __tablename__ = "portfolio_rebalancing"

    # Rebalancing Identifiers
    portfolio_id = Column(UUID(as_uuid=False), ForeignKey("investment_portfolios.id"), nullable=False)
    rebalancing_date = Column(Date, nullable=False, comment="Date of rebalancing")

    # Rebalancing Trigger
    trigger_type = Column(String(50), nullable=False, comment="What triggered rebalancing")
    trigger_description = Column(Text, nullable=True)

    # Pre-Rebalancing State
    pre_total_value = Column(Numeric(20, 2), nullable=False)
    pre_number_positions = Column(Integer, nullable=False)
    pre_risk_score = Column(Numeric(5, 4), nullable=True)
    pre_allocations = Column(JSON, nullable=True, comment="Pre-rebalancing allocations")

    # Post-Rebalancing State
    post_total_value = Column(Numeric(20, 2), nullable=False)
    post_number_positions = Column(Integer, nullable=False)
    post_risk_score = Column(Numeric(5, 4), nullable=True)
    post_allocations = Column(JSON, nullable=True, comment="Post-rebalancing allocations")

    # Rebalancing Actions
    positions_added = Column(JSON, nullable=True, comment="New positions added")
    positions_removed = Column(JSON, nullable=True, comment="Positions removed")
    positions_modified = Column(JSON, nullable=True, comment="Position size changes")

    # Costs and Impact
    transaction_costs = Column(Numeric(15, 2), nullable=True, comment="Total transaction costs")
    market_impact = Column(Numeric(15, 2), nullable=True, comment="Estimated market impact")
    opportunity_cost = Column(Numeric(15, 2), nullable=True, comment="Opportunity cost of rebalancing")

    # Optimization Metrics
    expected_return_improvement = Column(Numeric(5, 4), nullable=True)
    risk_reduction = Column(Numeric(5, 4), nullable=True)
    sharpe_ratio_improvement = Column(Numeric(5, 4), nullable=True)

    # Performance Post-Rebalancing
    one_week_performance = Column(Numeric(5, 4), nullable=True)
    one_month_performance = Column(Numeric(5, 4), nullable=True)
    three_month_performance = Column(Numeric(5, 4), nullable=True)

    # Relationships
    portfolio = relationship("InvestmentPortfolio", back_populates="rebalancing_actions")

    # Indexes
    __table_args__ = (
        Index("idx_portfolio_rebalancing_portfolio_date", "portfolio_id", "rebalancing_date"),
        Index("idx_portfolio_rebalancing_trigger", "trigger_type"),
        Index("idx_portfolio_rebalancing_performance", "one_month_performance"),
    )

    def __repr__(self):
        return f"<PortfolioRebalancing {self.portfolio_id} {self.rebalancing_date}>"