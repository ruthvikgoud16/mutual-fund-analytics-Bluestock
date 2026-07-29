# Phase 3: Exploratory Data Analysis (EDA) Report

## 1. Executive Summary
This report summarizes the findings of the Exploratory Data Analysis (EDA) stage for the **Bluestock Mutual Fund Analytics Platform**. The platform integrates multidimensional datasets comprising scheme metadata, daily Net Asset Value (NAV) valuations, quarterly assets under management (AUM), investor transactions, portfolio holdings, monthly SIP inflows, and benchmarks. Using 18 custom-crafted charts, we present comprehensive insights into mutual fund characteristics, category structures, risk-return statistics, portfolio sector allocations, investor behavior, and outliers.

## 2. Dataset Overview
The relational database `mutual_fund_analytics.db` hosts normalized tables matching our validated schema:
- **dim_fund**: 40 distinct schemes tracking characteristics such as expense ratios, launch dates, exit loads, and fund managers.
- **dim_date**: Calendar dimensions covering weekdays and quarters.
- **fact_nav**: 64,320 rows of daily NAV entries representing time-series prices.
- **fact_aum**: 90 quarterly AUM snapshots.
- **fact_sip_industry**: 48 months of SIP inflows.
- **fact_performance**: Returns (1y, 3y, 5y) and risk ratios (Sharpe, Sortino, Alpha, Beta) for 40 schemes.
- **fact_transactions**: 32,778 transaction records.
- **fact_portfolio**: 322 stock allocations across schemes.

## 3. Individual Analysis Sections

### A. Fund & Category Analysis
We evaluated the structure of the 40 mutual fund schemes. Equity remains the dominant asset class with a large count of schemes, followed by Debt. Expense ratios average around 1.5%, with Direct plans offering a cheaper option than Regular plans. 
- *AUM Concentration*: AUM is dominated by a few large Asset Management Companies (e.g., SBI Mutual Fund, ICICI Prudential, and HDFC Mutual Fund).

### B. NAV Volatility & Time Series
Net Asset Values across all schemes follow a log-normal distribution. The historical daily average NAV displays steady upward growth despite occasional short-term market consolidation periods. Schemes such as SBI Bluechip and Mirae Asset Large Cap demonstrate the highest peak NAVs due to early launch dates (accumulation effect).

### C. SIP Industry Trends
Monthly SIP inflows show strong positive growth over the 48-month reporting window, rising from ~11,000 crores to over 20,000 crores. Year-over-Year (YoY) growth rates are positive, indicating robust compounding of retail capital in mutual funds.

### D. Investor Transactions & Regional Analysis
The investor transaction dataset represents a highly active demographic:
- **Purchases vs Redemptions**: Inflows (SIP & Lumpsum) outnumber outflows (Redemptions) in total volume, creating net positive cash inflows.
- **Regional Volume**: Major states like Maharashtra, Gujarat, Karnataka, and Telangana drive the highest transaction value in rupees.

### E. Risk-Return Performance Analysis
- **Outperformance vs Benchmark**: Over 80% of schemes outperformed their respective index benchmarks over a 3-year period, generating positive Alpha.
- **Risk Metrics**: High Sharpe and Sortino ratios are concentrated in hybrid and large-cap equity categories.

### F. Portfolio Sector Allocations & Concentration
- **Sector Focus**: Banks/Financial Services, Technology, and Energy represent the heaviest sector weights.
- **Concentration**: The top 4 sectors account for more than 60% of the entire portfolio holdings.

## 4. Visualizations & Business Interpretations
All figures have been rendered and saved under `figures/`:
1. **01_category_distribution.png**: Depicts scheme representation.
2. **02_expense_ratio_distribution.png**: Identifies charging patterns.
3. **03_aum_by_fund_house.png**: Highlights AUM concentration.
4. **04_nav_distribution.png**: Log distribution of NAVs.
5. **05_nav_growth_trends.png**: Steady compounding over time.
6. **06_top_bottom_nav.png**: Outlines the highest NAV schemes.
7. **07_sip_inflows_trend.png**: Consistent retail compounding.
8. **08_sip_growth_yoy.png**: Compilation of YoY growth rate.
9. **09_sip_active_accounts.png**: Active accounts expansion.
10. **10_purchases_vs_redemptions.png**: Breakdown of transaction types.
11. **11_net_inflows_trend.png**: Net daily investor capital inflows.
12. **12_state_transactions.png**: Regional transaction concentration.
13. **13_best_schemes_cagr.png**: Performance profile of top funds.
14. **14_benchmark_vs_scheme.png**: Outperformance scatter plot.
15. **15_sector_allocations.png**: Sector preference list.
16. **16_portfolio_concentration.png**: Concentration donut chart.
17. **17_performance_correlation.png**: Statistical correlation matrix.
18. **18_outlier_detection.png**: Transaction boxplot outliers.

## 5. Key Findings
1. Retail SIP inflows represent a sticky capital base, growing steadily year-over-year.
2. There is a strong correlation between Alpha and Sharpe ratio, confirming that active managers add risk-adjusted value.
3. Financial services sector holdings create a slight concentration risk for index-hugging equity funds.

## 6. Business Recommendations
- **Cost Optimization**: Launch and market Direct plans with lower expense ratios to cater to digital investors.
- **Regional Expansion**: Expand offline presence in tier-2 states since transaction volumes are highly skewed toward tier-1 states.
- **Diversification**: Rebalance portfolio holdings to reduce exposure to the financial services sector and capture growth in defensive sectors like Pharmaceuticals and consumption.

## 7. Conclusion
The EDA phase is complete. The datasets are highly coherent, the SQLite database is populated correctly, and we have obtained deep insights that will feed the analytical dashboard and forecasting engine in the subsequent phases.
