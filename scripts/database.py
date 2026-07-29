"""SQLAlchemy database models for the Mutual Fund Analytics Star Schema.

This module maps Python classes to normalized relational database tables.
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DimFund(Base):
    """Scheme metadata dimension."""

    __tablename__ = "dim_fund"

    amfi_code = Column(Integer, primary_key=True)
    fund_house = Column(String, nullable=False)
    scheme_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    sub_category = Column(String, nullable=False)
    plan = Column(String, nullable=False)
    launch_date = Column(Date)
    benchmark = Column(String)
    expense_ratio_pct = Column(Float)
    exit_load_pct = Column(Float)
    min_sip_amount = Column(Float)
    min_lumpsum_amount = Column(Float)
    fund_manager = Column(String)
    risk_category = Column(String)
    sebi_category_code = Column(String)

    # Relationships
    nav_history = relationship("FactNav", back_populates="fund")
    transactions = relationship("FactTransactions", back_populates="fund")
    performance = relationship("FactPerformance", back_populates="fund", uselist=False)
    portfolio = relationship("FactPortfolio", back_populates="fund")
    risk_metrics = relationship("FactRiskMetrics", back_populates="fund", uselist=False)


class DimDate(Base):
    """Calendar dimension table."""

    __tablename__ = "dim_date"

    date_id = Column(Date, primary_key=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    is_weekday = Column(Boolean, nullable=False)


class FactNav(Base):
    """Time-series NAV valuation fact."""

    __tablename__ = "fact_nav"

    amfi_code = Column(Integer, ForeignKey("dim_fund.amfi_code"), nullable=False)
    date_id = Column(Date, ForeignKey("dim_date.date_id"), nullable=False)
    nav = Column(Float, nullable=False)
    daily_return_pct = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint("amfi_code", "date_id"),
        Index("idx_fact_nav_composite", "amfi_code", "date_id"),
    )

    fund = relationship("DimFund", back_populates="nav_history")


class FactTransactions(Base):
    """Investor transactions fact table."""

    __tablename__ = "fact_transactions"

    tx_id = Column(String, primary_key=True)
    investor_id = Column(String, nullable=False)
    amfi_code = Column(Integer, ForeignKey("dim_fund.amfi_code"), nullable=False)
    transaction_date = Column(Date, ForeignKey("dim_date.date_id"), nullable=False)
    transaction_type = Column(String, nullable=False)
    amount_inr = Column(Integer, nullable=False)
    state = Column(String)
    city = Column(String)
    city_tier = Column(String)
    age_group = Column(String)
    gender = Column(String)
    annual_income_lakh = Column(Float)
    payment_mode = Column(String)
    kyc_status = Column(String)

    __table_args__ = (
        CheckConstraint("transaction_type IN ('Sip', 'Lumpsum', 'Redemption')"),
        CheckConstraint("kyc_status IN ('Verified', 'Pending')"),
        Index("idx_fact_transactions_amfi", "amfi_code"),
        Index("idx_fact_transactions_date", "transaction_date"),
    )

    fund = relationship("DimFund", back_populates="transactions")


class FactPerformance(Base):
    """Fund performance analytics indicators fact."""

    __tablename__ = "fact_performance"

    amfi_code = Column(Integer, ForeignKey("dim_fund.amfi_code"), primary_key=True)
    return_1yr_pct = Column(Float)
    return_3yr_pct = Column(Float)
    return_5yr_pct = Column(Float)
    benchmark_3yr_pct = Column(Float)
    alpha = Column(Float)
    beta = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    std_dev_ann_pct = Column(Float)
    max_drawdown_pct = Column(Float)
    morningstar_rating = Column(Integer)
    risk_grade = Column(String)

    __table_args__ = (
        CheckConstraint("morningstar_rating >= 1 AND morningstar_rating <= 5"),
    )

    fund = relationship("DimFund", back_populates="performance")


class FactPortfolio(Base):
    """Portfolio equity security holdings fact."""

    __tablename__ = "fact_portfolio"

    amfi_code = Column(Integer, ForeignKey("dim_fund.amfi_code"), nullable=False)
    stock_symbol = Column(String, nullable=False)
    stock_name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    weight_pct = Column(Float, nullable=False)
    market_value_cr = Column(Float)
    current_price_inr = Column(Float)
    portfolio_date = Column(Date, ForeignKey("dim_date.date_id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("amfi_code", "stock_symbol", "portfolio_date"),
        Index("idx_fact_portfolio_composite", "amfi_code", "portfolio_date"),
    )

    fund = relationship("DimFund", back_populates="portfolio")


class FactAum(Base):
    """Fund house quarterly assets under management."""

    __tablename__ = "fact_aum"

    fund_house = Column(String, nullable=False)
    date_id = Column(Date, ForeignKey("dim_date.date_id"), nullable=False)
    aum_lakh_crore = Column(Float)
    aum_crore = Column(Float)
    num_schemes = Column(Integer)

    __table_args__ = (PrimaryKeyConstraint("fund_house", "date_id"),)


class FactSipIndustry(Base):
    """Monthly aggregate industry SIP inflows."""

    __tablename__ = "fact_sip_industry"

    month = Column(String, primary_key=True)  # YYYY-MM
    sip_inflow_crore = Column(Float)
    active_sip_accounts_crore = Column(Float)
    new_sip_accounts_lakh = Column(Float)
    sip_aum_lakh_crore = Column(Float)
    yoy_growth_pct = Column(Float)


class FactRiskMetrics(Base):
    """Calculated financial risk and performance analytics metrics fact table."""

    __tablename__ = "fact_risk_metrics"

    amfi_code = Column(Integer, ForeignKey("dim_fund.amfi_code"), primary_key=True)
    cagr_pct = Column(Float)
    volatility_ann_pct = Column(Float)
    downside_deviation_pct = Column(Float)
    max_drawdown_pct = Column(Float)
    beta = Column(Float)
    alpha = Column(Float)
    tracking_error_pct = Column(Float)
    information_ratio = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    treynor_ratio = Column(Float)
    calmar_ratio = Column(Float)
    hhi = Column(Float)
    diversification_score = Column(Float)
    calculation_date = Column(Date)

    fund = relationship("DimFund", back_populates="risk_metrics")
