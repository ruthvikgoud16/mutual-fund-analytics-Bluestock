# Data Dictionary - Mutual Fund Analytics

This document contains the detailed data dictionary for the 10 raw CSV files in `data/raw/` for the Mutual Fund Analytics Platform.

---

## 1. 01_fund_master.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Unique code assigned by AMFI | Identifies the mutual fund scheme | `119551` | No | `> 100000` | Yes | None | Non-standard values | Must be positive integer |
| `fund_house` | TEXT | Asset Management Company name | The company managing the fund | `SBI Mutual Fund` | No | Non-empty | No | None | Naming variations / typos | List of top AMCs in India |
| `scheme_name` | TEXT | Full official name of the scheme | User-facing fund identifier | `SBI Bluechip Fund - Regular - Growth` | No | Non-empty | No | None | Naming inconsistencies | Contains "Regular" or "Direct" |
| `category` | TEXT | Broad classification category | Broad asset class (Equity, Debt) | `Equity` | No | `Equity, Debt, Hybrid, Other` | No | None | Typographical errors | Must belong to asset categories |
| `sub_category` | TEXT | Detailed category classification | Asset sub-type | `Large Cap` | No | Large Cap, Mid Cap, ELSS, etc. | No | None | Sub-category name variance | Must belong to SEBI classes |
| `plan` | TEXT | Plan type offered | regular vs direct distribution | `Regular` | No | `Regular, Direct` | No | None | Case mismatches | Must be 'Regular' or 'Direct' |
| `launch_date` | DATE | Fund inception date | Launch date of the scheme | `2006-02-14` | No | `1990-01-01` to current | No | None | Incorrect date format | ISO 8601 YYYY-MM-DD format |
| `benchmark` | TEXT | Relative index benchmark | Index compared against | `NIFTY 100 TRI` | No | Nifty, BSE index names | No | None | Text inconsistencies | Matches active indexes |
| `expense_ratio_pct`| REAL | Annual cost charged to investors | Annual management expense | `1.54` | No | `0.10` to `2.50` | No | None | Unusually high ratios | Between 0.05% and 3.00% |
| `exit_load_pct` | REAL | Charge for premature redemption | Redemption penalty fee | `1.0` | No | `0.0` to `3.0` | No | None | Incorrect float parsed | Between 0% and 5.0% |
| `min_sip_amount` | REAL | Minimum recurring investment | Lowest entry for monthly SIP | `500.0` | No | `100.0` to `5000.0` | No | None | Negative values | Greater than or equal to 100 |
| `min_lumpsum_amount`| REAL | Minimum initial investment | Lowest entry for one-time buy | `1000.0` | No | `500.0` to `10000.0` | No | None | Zero values | Greater than or equal to 500 |
| `fund_manager` | TEXT | Head manager of the fund | Individual in charge of returns | `Sohini Andani` | No | Alphabetical text | No | None | Spelling variations | Text only |
| `risk_category` | TEXT | SEBI standard risk rating | Risk grade (Low to Very High) | `Moderate` | No | Low, Moderate, High, etc. | No | None | Mismatch with SEBI grades | Must match SEBI risk levels |
| `sebi_category_code`| TEXT | Internal SEBI category code | SEBI category identifier | `EC01` | No | Alphanumeric (e.g., EC01, DC01)| No | None | Code formatting | Length of 4 characters |

---

## 2. 02_nav_history.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Scheme code identifier | References the scheme | `119551` | No | `> 100000` | Yes (part) | `dim_fund.amfi_code` | Missing codes | Must exist in `dim_fund` |
| `date` | DATE | NAV business date | Valuation date | `2022-01-03` | No | Jan 2022 to May 2026 | Yes (part) | None | Non-trading dates | ISO 8601 YYYY-MM-DD |
| `nav` | REAL | Net Asset Value price per unit | Price of 1 unit of the fund | `54.3856` | No | `> 0.0` | No | None | Sudden spikes or zero | Must be positive float |

---

## 3. 03_aum_by_fund_house.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | DATE | Quarter ending date | Reporting quarter date | `2022-03-31` | No | 2022 to 2025 quarters | Yes (part) | None | Non-quarter-end dates | Must be quarter end date |
| `fund_house` | TEXT | AMC name | Fund house name | `SBI Mutual Fund` | No | Top AMCs in India | Yes (part) | `dim_fund.fund_house` | String mismatches | Must exist in master list |
| `aum_lakh_crore` | REAL | AUM value in lakh crores | Asset scale indicator | `6.05` | No | `0.1` to `15.0` | No | None | Scaling confusion | Value must be positive |
| `aum_crore` | REAL | AUM value in crores | Asset scale indicator (crores) | `605000.0` | No | `10000` to `1500000` | No | None | Inconsistent value with lakh crore | `aum_crore = aum_lakh_crore * 100000` |
| `num_schemes` | INTEGER | Active schemes count in AMC | Product range scale | `186` | No | `1` to `500` | No | None | Negative counts | Must be positive integer |

---

## 4. 04_monthly_sip_inflows.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `month` | TEXT | Calendar Month | Reporting period | `2022-01` | No | `2022-01` to current | Yes | None | Format errors | Format must be YYYY-MM |
| `sip_inflow_crore` | REAL | Total SIP inflows (Rs. Crore) | Monthly SIP collection | `11517.0` | No | `5000` to `40000` | No | None | Zero value | Must be positive |
| `active_sip_accounts_crore` | REAL | Count of active SIPs (Crores) | Customer retention scale | `4.91` | No | `1.0` to `15.0` | No | None | Decimal parsing | Must be positive |
| `new_sip_accounts_lakh` | REAL | New accounts added (Lakhs) | Growth rate indicator | `9.1` | No | `1.0` to `50.0` | No | None | Missing values | Must be positive |
| `sip_aum_lakh_crore` | REAL | Total SIP AUM (Rs. Lakh Crore) | Accumulated SIP wealth | `4.8` | No | `1.0` to `25.0` | No | None | Out of range | Must be positive |
| `yoy_growth_pct` | REAL | Year-on-year growth percentage | Growth speed index | `22.5` | Yes | `-50.0` to `100.0` | No | None | Nulls in first year | Float or Null |

---

## 5. 05_category_inflows.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `month` | TEXT | Calendar Month | Reporting period | `2024-04` | No | YYYY-MM format | Yes (part) | None | Format error | Format must be YYYY-MM |
| `category` | TEXT | Mutual fund asset category | Industry category classification| `Large Cap` | No | Category names | Yes (part) | `dim_fund.category` | String mismatch | Must match master categories |
| `net_inflow_crore` | REAL | Net monthly inflows (Rs. Crore) | Net sector capital flows | `2413.0` | No | `-10000.0` to `50000.0` | No | None | Negative value handling | Positive/Negative float |

---

## 6. 06_industry_folio_count.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `month` | TEXT | Calendar Month | Reporting period | `2022-01` | No | YYYY-MM format | Yes | None | Format error | Format must be YYYY-MM |
| `total_folios_crore` | REAL | Total folio accounts (Crore) | Total accounts | `13.26` | No | `5.0` to `50.0` | No | None | Incorrect sum | `total = equity + debt + hybrid + others` |
| `equity_folios_crore` | REAL | Equity folios count (Crore) | Stock fund folios | `9.28` | No | `5.0` to `40.0` | No | None | Inconsistent value | Must be positive |
| `debt_folios_crore` | REAL | Debt folios count (Crore) | Fixed income folios | `1.86` | No | `0.5` to `10.0` | No | None | Inconsistent value | Must be positive |
| `hybrid_folios_crore` | REAL | Hybrid folios count (Crore) | Balanced fund folios | `0.8` | No | `0.1` to `5.0` | No | None | Inconsistent value | Must be positive |
| `others_folios_crore` | REAL | Other types of folios (Crore) | Index/Gold/FOF folios | `1.33` | No | `0.1` to `10.0` | No | None | Inconsistent value | Must be positive |

---

## 7. 07_scheme_performance.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | AMFI scheme identifier | References the scheme | `119551` | No | `> 100000` | Yes | `dim_fund.amfi_code` | Code missing | Must exist in `dim_fund` |
| `scheme_name` | TEXT | Scheme name | Fund identifier | `SBI Bluechip Fund` | No | Non-empty | No | None | String mismatch | Matches master scheme name |
| `fund_house` | TEXT | AMC name | Fund house | `SBI Mutual Fund` | No | Top AMCs in India | No | None | String mismatch | Matches master fund house |
| `category` | TEXT | Category name | Asset category | `Large Cap` | No | Category names | No | None | Category mismatch | Matches master category |
| `plan` | TEXT | Plan type | Regular vs Direct plan | `Regular` | No | `Regular, Direct` | No | None | Case mismatches | Must be 'Regular' or 'Direct' |
| `return_1yr_pct` | REAL | 1 Year absolute return | short-term returns | `12.42` | No | `-50` to `150` | No | None | Text formatting | Numeric float |
| `return_3yr_pct` | REAL | 3 Year annualized return (CAGR) | Medium-term returns | `12.36` | No | `-30` to `100` | No | None | Text formatting | Numeric float |
| `return_5yr_pct` | REAL | 5 Year annualized return (CAGR) | Long-term returns | `14.45` | No | `-20` to `80` | No | None | Text formatting | Numeric float |
| `benchmark_3yr_pct`| REAL | Benchmark index 3 Year CAGR | Comparison reference | `11.49` | No | `-30` to `100` | No | None | Index name mismatch | Numeric float |
| `alpha` | REAL | Excess returns vs benchmark | Fund manager skill | `0.87` | No | `-20.0` to `30.0` | No | None | Math mismatch | Return - Benchmark returns |
| `beta` | REAL | Sensitivity to market movements | Risk level indicator | `0.89` | No | `0.1` to `2.5` | No | None | Leverage anomalies | Numeric float |
| `sharpe_ratio` | REAL | Risk-adjusted return metric | Return per unit of risk | `0.88` | No | `-5.0` to `5.0` | No | None | Risk-free rate proxy diff | Numeric float |
| `sortino_ratio` | REAL | Downside risk-adjusted return | Downside risk ratio | `1.29` | No | `-5.0` to `5.0` | No | None | Zero division risk | Numeric float |
| `std_dev_ann_pct` | REAL | Annualized return volatility | Total volatility risk | `14.0` | No | `1.0` to `50.0` | No | None | Calculation mismatch | Numeric float |
| `max_drawdown_pct` | REAL | Worst peak-to-trough drop | Maximum loss capacity | `-21.7` | No | `-100.0` to `0.0` | No | None | Positive values | Must be negative float |
| `aum_crore` | REAL | Total Assets in Crores | Fund scale value | `14288.0` | No | `1.0` to `100000.0` | No | None | Mismatch with AUM file | Must be positive float |
| `expense_ratio_pct`| REAL | Expense ratio percent | Annual charge rate | `1.54` | No | `0.1` to `3.0` | No | None | Inconsistent value | Matches fund master ratio |
| `morningstar_rating`| INTEGER | Morningstar quality rating | Star index (1-5) | `4` | No | `1` to `5` | No | None | Out of range | Must be integer between 1-5 |
| `risk_grade` | TEXT | Performance risk grade | Qualitative score | `Moderate` | No | SEBI standard risk levels | No | None | Mismatch | Matches SEBI standard |

---

## 8. 08_investor_transactions.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `investor_id` | TEXT | Unique investor code | Client ID | `INV003054` | No | Alphanumeric | No | None | Formatting variation | Begins with 'INV' + digits |
| `transaction_date` | DATE | Transaction settlement date | Order execution date | `2024-01-01` | No | 2022 to 2026 | No | `dim_date.date_id` | Future date errors | ISO 8601 YYYY-MM-DD |
| `amfi_code` | INTEGER | Scheme code identifier | References the scheme traded | `119092` | No | `> 100000` | No | `dim_fund.amfi_code` | Invalid codes | Must exist in `dim_fund` |
| `transaction_type` | TEXT | Transaction category | Buy/Sell flag | `SIP` | No | `SIP, Lumpsum, Redemption`| No | None | Mispelled types | Must be in active categories |
| `amount_inr` | INTEGER | Transaction value in Rupees | Trade transaction size | `1834` | No | `> 0` | No | None | Negative amount | Must be positive integer |
| `state` | TEXT | Investor state of residence | Geographic category | `Telangana` | No | Indian States | No | None | Mispellings / Case | Must be valid Indian state |
| `city` | TEXT | Investor city of residence | Geographic location | `Hyderabad` | No | Indian Cities | No | None | Mispellings / Case | Must be valid city |
| `city_tier` | TEXT | Category of city | Geographic tier classification | `T30` | No | `T30, B30` | No | None | Tier classification | Must be 'T30' or 'B30' |
| `age_group` | TEXT | Age range bucket | Age group category | `56+` | No | Age categories | No | None | Category format | Must match age ranges |
| `gender` | TEXT | Investor gender | Gender category | `Female` | No | `Male, Female, Other` | No | None | Code representation | Must match gender |
| `annual_income_lakh`| REAL | Annual income (Lakh Rs) | Financial status | `77.1` | No | `1.0` to `1000.0` | No | None | Negative values | Must be positive |
| `payment_mode` | TEXT | Mode of transaction payment | Channel method | `UPI` | No | UPI, Net Banking, Mandate, Cheque | No | None | Formatting variations | Valid payment channel list |
| `kyc_status` | TEXT | Account KYC status | Verification checkpoint | `Verified` | No | `Verified, Pending` | No | None | Mismatched verification status | Must be 'Verified' or 'Pending' |

---

## 9. 09_portfolio_holdings.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Scheme code identifier | References the holding fund | `119551` | No | `> 100000` | Yes (part) | `dim_fund.amfi_code` | Code missing | Must exist in `dim_fund` |
| `stock_symbol` | TEXT | Asset stock symbol | Underling stock symbol | `POWERGRID` | No | Stock exchange symbols | Yes (part) | None | Typo in ticker | Valid active ticker name |
| `stock_name` | TEXT | Asset stock name | Full company name | `Power Grid Corporation` | No | Company name | No | None | Ticker mismatch | Alphanumeric |
| `sector` | TEXT | Stock sector classification | Economy segment | `Utilities` | No | Standard sectors | No | None | Spelling variance | Standard sector name |
| `weight_pct` | REAL | Weight percent of portfolio | Holding size percentage | `13.85` | No | `0.0` to `100.0` | No | None | Total weight > 100% | Between 0.0 and 100.0 |
| `market_value_cr` | REAL | Holding market value (Crore) | Currency size value | `737.09` | No | `> 0.0` | No | None | Inconsistent value | Must be positive |
| `current_price_inr` | REAL | Underling share price | Share value | `6011.08` | No | `0.1` to `100000` | No | None | Inconsistent share price | Must be positive |
| `portfolio_date` | DATE | Report snapshot date | Holding portfolio date | `2025-12-31` | No | Standard Date | Yes (part) | `dim_date.date_id` | Missing date formats | ISO 8601 YYYY-MM-DD |

---

## 10. 10_benchmark_indices.csv

| Column Name | Data Type | Description | Business Meaning | Example Values | Nullable | Expected Range | Candidate PK | Candidate FK | Data Quality Risks | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | DATE | Trading business date | Index calculation date | `2022-01-03` | No | Jan 2022 to May 2026 | Yes (part) | `dim_date.date_id` | Non-trading dates | ISO 8601 YYYY-MM-DD |
| `index_name` | TEXT | Benchmark name | Index name reference | `NIFTY50` | No | Index codes | Yes (part) | None | Spelling mismatch | Standard index list |
| `close_value` | REAL | Daily close value price | Index closing point | `17492.79` | No | `> 0.0` | No | None | Sudden drop / zero value | Must be positive |
