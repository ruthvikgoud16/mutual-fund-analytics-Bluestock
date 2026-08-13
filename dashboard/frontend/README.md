# Bluestock Insights Hub

actual task is this Dashboard Development (Power BI / Tableau)

IN_PROGRESSTASKMEDIUM

Assigned toNKNanda kumarSIsinghnijjar2022VAvarshithavadlamuruRURuthvikgoud16ANankithab67

Due : 09 Aug 2026

Time estimate: 7–8 hours

Tasks:

Connect Power BI to data — import all cleaned CSVs or connect via SQLite ODBC. Verify all 8 tables load. Create relationships on amfi_code and date.

Page 1 — Industry Overview — KPI cards: Total AUM (₹81L Cr), SIP Inflows (₹31K Cr), Folios (26.12 Cr), Schemes (1,908). Line chart: industry AUM trend 2022–2025. Bar chart: AUM by AMC.

Page 2 — Fund Performance — Scatter plot: return (X) vs risk/StdDev (Y), bubble size = AUM. Sortable fund scorecard table. NAV line vs benchmark. Slicers: fund house, category, plan.

Page 3 — Investor Analytics — Bar chart: transaction amount by state. Donut: SIP/Lumpsum/Redemption split. Bar: age group vs avg SIP amount. Monthly transaction volume line. Slicers: state, age group, city tier.

Page 4 — SIP & Market Trends — Dual-axis: SIP inflow (bar) + Nifty 50 (line) 2022–2025. Category inflow heatmap. Top 5 categories by net inflow FY25.

Add interactivity — drill-through from fund table to NAV detail page. Tooltips on all charts. Apply Bluestock colour theme and logo.

Export — save as .pbix. Export to PDF. Export each page as PNG for the final report.

Deliverables: bluestock_mf_dashboard.pbix, Dashboard.pdf, 4 page PNG screenshots.    but the prompt being given to you is this You are now the Principal Engineer responsible for FINALIZING PHASE 5 of the Bluestock Mutual Fund Analytics project.

A separate frontend/UI implementation has been completed in Replit because the previous dashboard implementation did not meet the required visual/UX quality.

IMPORTANT:

DO NOT REBUILD THE DASHBOARD FROM SCRATCH.

The Replit implementation is now the PRIMARY FRONTEND/UI BASELINE.

Your job is to integrate, audit, correct, and finalize it against the actual Bluestock project.

==================================================

SOURCE OF TRUTH — MUST INSPECT ALL OF THESE

==================================================

Before making changes, inspect the repository and determine the actual current state.

You MUST inspect:

1. The Bluestock Phase 5 requirements/specification.

2. The Bluestock project requirements / final requirements file if present.

3. The Phase 5 PDF/handbook if present.

4. The actual datasets under data/.

5. The processed datasets under data/processed/.

6. mutual_fund_analytics.db

7. bluestock_mf.db if present.

8. Phase 1–4 implementation.

9. Phase 3 EDA outputs.

10. Phase 4 Fund Performance outputs.

11. Advanced Analytics outputs.

12. The Replit-generated frontend.

13. Existing dashboard files.

14. Existing README/documentation.

15. Existing tests.

16. Existing Git history and phase tags.

DO NOT assume the previous completion reports are correct.

Verify against the actual repository and actual data.

==================================================

PHASE 5 REQUIREMENTS

==================================================

Required dashboard functionality:

PAGE 1 — INDUSTRY OVERVIEW

- Total AUM — ₹81L Cr

- SIP Inflows — ₹31K Cr

- Folios — 26.12 Cr

- Schemes — 1,908

- Industry AUM trend 2022–2025

- AUM by AMC

PAGE 2 — FUND PERFORMANCE

- Return vs Risk / StdDev scatter

- Bubble size = AUM

- Sortable fund scorecard

- NAV vs benchmark

- Fund House filter

- Category filter

- Plan filter

PAGE 3 — INVESTOR ANALYTICS

- Transaction amount by state

- SIP/Lumpsum/Redemption split

- Age group vs average SIP amount

- Monthly transaction volume

- State filter

- Age Group filter

- City Tier filter

PAGE 4 — SIP & MARKET TRENDS

- SIP inflow + Nifty 50 visualization

- 2022–2025

- Category inflow heatmap

- Top 5 FY25 categories by net inflow

INTERACTIVITY:

- Fund table → fund detail drill-through

- Chart tooltips

- Filters

- Reset controls

- Navigation

- Responsive behavior

- Proper empty/loading/error states

EXPORT TARGETS:

- bluestock_mf_dashboard.pbix

- Dashboard.pdf

- 4 page PNG screenshots

==================================================

CRITICAL FRONTEND REQUIREMENT

==================================================

The Replit frontend is the visual baseline.

DO NOT replace it with the previous generic Streamlit dashboard.

DO NOT downgrade the UI.

DO NOT create a generic AI-generated dashboard.

Preserve the Replit implementation's:

- layout

- typography

- spacing

- visual hierarchy

- chart composition

- navigation

- filters

- tables

- fund detail page

- responsive behavior

- interaction patterns

- Bluestock visual identity

You may refactor implementation where technically necessary, but the final product must retain the professional frontend quality.

==================================================

DATA INTEGRATION

==================================================

The current Replit implementation uses representative/local data.

Replace those data providers with the REAL project data.

Do NOT fabricate metrics.

Connect the UI to the existing project data/database/analytics outputs.

Map the frontend data contracts to:

- industry AUM

- SIP inflows

- folios

- AMC AUM

- fund performance

- risk metrics

- scorecard

- NAV

- benchmarks

- transactions

- demographics

- geographic analytics

- category inflows

Reuse existing Phase 1–4 calculations wherever possible.

Do NOT duplicate analytics logic unnecessarily.

Do NOT recalculate Phase 4 metrics differently in the frontend.

The UI should consume the established analytical outputs.

==================================================

DATA VALIDATION

==================================================

For every major KPI and chart:

trace:

UI value

↓

frontend data provider

↓

database/report

↓

processed dataset

↓

original source

Verify that values are actually supported by the project data.

Pay particular attention to:

- ₹81L Cr AUM

- ₹31K Cr SIP inflow

- 26.12 Cr folios

- 1,908 schemes

- SBI AUM

- Phase 4 fund scores

- CAGR

- Sharpe

- Sortino

- Alpha

- Beta

- Maximum Drawdown

- NAV series

- Nifty benchmark

- transaction totals

- age groups

- state totals

- T30/B30

- category inflows

If a requirement's stated number does not match the actual dataset, DO NOT silently fabricate or overwrite the data.

Document the discrepancy and determine what the Bluestock specification requires.

==================================================

DRILL-THROUGH

==================================================

Verify that:

Fund Performance

→ select fund

→ Fund Detail

works with REAL fund data.

Fund Detail must display the actual:

- fund

- AMC

- category

- plan

- NAV

- benchmark

- CAGR

- Sharpe

- Sortino

- Alpha

- Beta

- Max Drawdown

- Expense Ratio

- Composite Score

No placeholder values.

==================================================

BACKEND / ARCHITECTURE

==================================================

Do not destroy existing:

- SQLite database

- Phase 1 scripts

- Phase 2 schema

- Phase 3 EDA

- Phase 4 analytics

- Advanced analytics

Create a clean integration boundary.

If the frontend needs an API/data service:

implement it cleanly.

If direct SQLite access is appropriate for the current architecture:

use it safely.

Do not move database logic into UI components.

Use:

UI

→ service/data layer

→ database/analytics outputs

not:

UI

→ random SQL queries everywhere.

==================================================

POWER BI / TABLEAU REQUIREMENT

==================================================

The original Bluestock requirement asks for Power BI/Tableau dashboard deliverables.

Do not falsely claim that a web frontend is a .pbix file.

Determine what can actually be generated in this environment.

If a valid .pbix cannot be programmatically created:

- do not create a fake .pbix

- do not rename another file to .pbix

- do not claim it is a Power BI workbook

Instead, preserve the best valid dashboard/export artifacts possible and clearly document the limitation.

If the repository already contains valid Power BI/Tableau assets, inspect them and determine whether they satisfy the requirement.

==================================================

EXPORTS

==================================================

Generate/verify:

Dashboard.pdf

and four page PNG exports:

Page 1 — Industry Overview

Page 2 — Fund Performance

Page 3 — Investor Analytics

Page 4 — SIP & Market Trends

The exports must represent the ACTUAL final dashboard.

Do not generate static images unrelated to the real UI.

==================================================

QUALITY AUDIT

==================================================

Act as a Principal Engineer performing a production release review.

Check:

Architecture

Data correctness

Runtime behavior

UI correctness

UX quality

Performance

Error handling

Type safety

Testing

Security

Maintainability

Requirement traceability

Look specifically for:

- hardcoded metrics

- placeholder data

- fake charts

- dead buttons

- broken navigation

- inconsistent filters

- incorrect calculations

- duplicated analytics logic

- stale Phase 4 outputs

- broken database mappings

- console errors

- runtime exceptions

- missing loading states

- missing empty states

- incorrect number formatting

- misleading axes

- inaccessible controls

- responsive layout problems

==================================================

VERIFICATION GATE

==================================================

Do not declare Phase 5 complete until you actually run the application and verify it.

Run the project's relevant:

- tests

- typecheck

- lint

- formatting

- compilation/build

- database validation

- frontend runtime validation

Verify every Phase 5 page.

Verify every required interaction.

Verify real data appears.

Verify drill-through.

Verify exports.

Verify Git status.

==================================================

GIT DISCIPLINE

==================================================

Do not commit until the implementation is verified.

Before committing:

git status

git diff

git diff --stat

Ensure no unrelated Phase 6/7 work is accidentally included.

Then create the Phase 5 completion commit only after the verification gate passes.

Use:

git commit -m "Complete Phase 5: Dashboard Development"

Then create/update:

phase-5-complete

Verify:

git rev-parse HEAD

git rev-list -n 1 phase-5-complete

git status

==================================================

FINAL REPORT

==================================================

At the end, provide:

1. Phase 5 requirement traceability matrix.

2. Replit frontend integration summary.

3. Actual data sources used.

4. Database mappings.

5. Page-by-page verification.

6. Interaction verification.

7. Export verification.

8. Tests and commands executed.

9. Any discrepancies found.

10. Any limitations.

11. Git commit hash.

12. phase-5-complete tag hash.

13. Final Git status.

14. Honest Phase 5 completion percentage.

IMPORTANT:

Do NOT say "100% complete" merely because files exist.

Phase 5 is complete ONLY when the actual requirements, real data, frontend runtime, interactions, exports, and verification gate all pass.

If anything is missing, identify it explicitly and fix it before completion where possible.

Do not proceed into Phase 6 or Phase 7.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/45b343bf-dafe-4aaa-8a76-50b51e856fc2).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
