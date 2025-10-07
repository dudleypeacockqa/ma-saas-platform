"""
Market Data Service
Integrates with real-time market data APIs for valuation inputs
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging
import os

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from ..models.financial_models import MarketDataSnapshot


logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching and storing market data"""

    def __init__(self, db: Session):
        self.db = db

    def fetch_current_market_data(self) -> MarketDataSnapshot:
        """
        Fetch current market data from various sources

        Returns:
            MarketDataSnapshot with current data
        """
        snapshot = MarketDataSnapshot(
            snapshot_date=datetime.utcnow(),
            data_source="Multiple Sources"
        )

        # Get treasury rates (risk-free rates)
        treasury_data = self._fetch_treasury_rates()
        if treasury_data:
            snapshot.risk_free_rate_10yr = treasury_data.get("10yr")
            snapshot.risk_free_rate_5yr = treasury_data.get("5yr")

        # Get market indices
        market_data = self._fetch_market_indices()
        if market_data:
            snapshot.sp500_level = market_data.get("sp500_level")
            snapshot.sp500_pe_ratio = market_data.get("sp500_pe")
            snapshot.market_risk_premium = market_data.get("risk_premium", 6.0)  # Historical average

        # Get credit spreads
        credit_data = self._fetch_credit_spreads()
        if credit_data:
            snapshot.investment_grade_spread = credit_data.get("investment_grade")
            snapshot.high_yield_spread = credit_data.get("high_yield")

        # Get industry multiples
        industry_multiples = self._fetch_industry_multiples()
        if industry_multiples:
            snapshot.industry_multiples = industry_multiples

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot

    def _fetch_treasury_rates(self) -> Optional[Dict[str, float]]:
        """
        Fetch current US Treasury rates

        Returns:
            Dict with treasury rates or None
        """
        if not YFINANCE_AVAILABLE:
            logger.warning("yfinance not available, using default rates")
            return {
                "10yr": 4.5,  # Default values
                "5yr": 4.2
            }

        try:
            # Fetch 10-year treasury
            ticker_10yr = yf.Ticker("^TNX")  # 10-year treasury yield
            data_10yr = ticker_10yr.history(period="1d")

            if not data_10yr.empty:
                rate_10yr = float(data_10yr['Close'].iloc[-1])

                return {
                    "10yr": round(rate_10yr, 2),
                    "5yr": round(rate_10yr - 0.3, 2)  # Approximation
                }
        except Exception as e:
            logger.error(f"Error fetching treasury rates: {str(e)}")

        # Default fallback
        return {
            "10yr": 4.5,
            "5yr": 4.2
        }

    def _fetch_market_indices(self) -> Optional[Dict[str, Any]]:
        """
        Fetch market index data

        Returns:
            Dict with market data or None
        """
        if not YFINANCE_AVAILABLE:
            logger.warning("yfinance not available, using default values")
            return {
                "sp500_level": 4500.0,
                "sp500_pe": 20.0,
                "risk_premium": 6.0
            }

        try:
            # Fetch S&P 500
            sp500 = yf.Ticker("^GSPC")
            sp500_data = sp500.history(period="1d")

            if not sp500_data.empty:
                sp500_level = float(sp500_data['Close'].iloc[-1])

                # Try to get P/E ratio from info
                sp500_info = sp500.info
                sp500_pe = sp500_info.get('trailingPE', 20.0)

                return {
                    "sp500_level": round(sp500_level, 2),
                    "sp500_pe": round(sp500_pe, 1),
                    "risk_premium": 6.0  # Historical average
                }
        except Exception as e:
            logger.error(f"Error fetching market indices: {str(e)}")

        # Default fallback
        return {
            "sp500_level": 4500.0,
            "sp500_pe": 20.0,
            "risk_premium": 6.0
        }

    def _fetch_credit_spreads(self) -> Optional[Dict[str, float]]:
        """
        Fetch credit spreads

        Returns:
            Dict with credit spread data or None
        """
        # In production, would integrate with Bloomberg or FRED API
        # For now, using historical averages
        return {
            "investment_grade": 1.5,  # % spread over treasuries
            "high_yield": 4.5
        }

    def _fetch_industry_multiples(self) -> Dict[str, Dict[str, float]]:
        """
        Fetch industry-specific valuation multiples

        Returns:
            Dict of industry multiples
        """
        # In production, would fetch from financial data provider
        # Using industry benchmarks
        return {
            "technology": {
                "ev_revenue": 5.0,
                "ev_ebitda": 15.0,
                "pe": 25.0
            },
            "healthcare": {
                "ev_revenue": 3.0,
                "ev_ebitda": 12.0,
                "pe": 20.0
            },
            "manufacturing": {
                "ev_revenue": 1.5,
                "ev_ebitda": 10.0,
                "pe": 15.0
            },
            "retail": {
                "ev_revenue": 1.0,
                "ev_ebitda": 8.0,
                "pe": 14.0
            },
            "professional_services": {
                "ev_revenue": 2.5,
                "ev_ebitda": 11.0,
                "pe": 18.0
            },
            "financial_services": {
                "ev_revenue": 3.5,
                "ev_ebitda": 10.0,
                "pe": 12.0
            }
        }

    def get_latest_snapshot(self) -> Optional[MarketDataSnapshot]:
        """
        Get the most recent market data snapshot

        Returns:
            Latest MarketDataSnapshot or None
        """
        snapshot = self.db.query(MarketDataSnapshot).order_by(
            MarketDataSnapshot.snapshot_date.desc()
        ).first()

        # If snapshot is older than 24 hours, fetch new data
        if not snapshot or (datetime.utcnow() - snapshot.snapshot_date) > timedelta(hours=24):
            snapshot = self.fetch_current_market_data()

        return snapshot

    def get_risk_free_rate(self, term_years: int = 10) -> float:
        """
        Get current risk-free rate

        Args:
            term_years: Term in years (5 or 10)

        Returns:
            Risk-free rate as percentage
        """
        snapshot = self.get_latest_snapshot()

        if not snapshot:
            return 4.5  # Default

        if term_years == 5:
            return float(snapshot.risk_free_rate_5yr) if snapshot.risk_free_rate_5yr else 4.2
        else:
            return float(snapshot.risk_free_rate_10yr) if snapshot.risk_free_rate_10yr else 4.5

    def get_market_risk_premium(self) -> float:
        """
        Get current market risk premium

        Returns:
            Market risk premium as percentage
        """
        snapshot = self.get_latest_snapshot()

        if not snapshot or not snapshot.market_risk_premium:
            return 6.0  # Historical average

        return float(snapshot.market_risk_premium)

    def get_industry_multiples(self, industry: str) -> Dict[str, float]:
        """
        Get industry-specific valuation multiples

        Args:
            industry: Industry name

        Returns:
            Dict with multiples
        """
        snapshot = self.get_latest_snapshot()

        if not snapshot or not snapshot.industry_multiples:
            return self._fetch_industry_multiples().get(industry.lower(), {
                "ev_revenue": 2.0,
                "ev_ebitda": 10.0,
                "pe": 15.0
            })

        return snapshot.industry_multiples.get(industry.lower(), {
            "ev_revenue": 2.0,
            "ev_ebitda": 10.0,
            "pe": 15.0
        })

    def get_cost_of_debt_benchmark(self, credit_rating: str = "BBB") -> float:
        """
        Get benchmark cost of debt based on credit rating

        Args:
            credit_rating: Credit rating (AAA, AA, A, BBB, BB, B, CCC)

        Returns:
            Cost of debt as percentage
        """
        snapshot = self.get_latest_snapshot()

        risk_free = self.get_risk_free_rate()

        # Credit spread by rating
        spreads = {
            "AAA": 0.5,
            "AA": 0.7,
            "A": 1.0,
            "BBB": 1.5,
            "BB": 3.0,
            "B": 4.5,
            "CCC": 7.0
        }

        spread = spreads.get(credit_rating.upper(), 1.5)

        return round(risk_free + spread, 2)

    def calculate_beta(
        self,
        ticker: str,
        market_ticker: str = "^GSPC",
        period: str = "2y"
    ) -> Optional[float]:
        """
        Calculate stock beta vs market

        Args:
            ticker: Company ticker symbol
            market_ticker: Market index ticker (default S&P 500)
            period: Historical period for calculation

        Returns:
            Beta value or None
        """
        if not YFINANCE_AVAILABLE:
            logger.warning("yfinance not available for beta calculation")
            return 1.0  # Market beta

        try:
            import numpy as np

            # Fetch historical data
            stock = yf.Ticker(ticker)
            market = yf.Ticker(market_ticker)

            stock_data = stock.history(period=period)
            market_data = market.history(period=period)

            # Calculate returns
            stock_returns = stock_data['Close'].pct_change().dropna()
            market_returns = market_data['Close'].pct_change().dropna()

            # Align dates
            aligned_data = stock_returns.align(market_returns, join='inner')
            stock_returns_aligned = aligned_data[0]
            market_returns_aligned = aligned_data[1]

            # Calculate beta
            covariance = np.cov(stock_returns_aligned, market_returns_aligned)[0][1]
            market_variance = np.var(market_returns_aligned)

            beta = covariance / market_variance

            return round(beta, 2)

        except Exception as e:
            logger.error(f"Error calculating beta for {ticker}: {str(e)}")
            return 1.0  # Default to market beta
