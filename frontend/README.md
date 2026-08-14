# Mutual Fund Analytics Dashboard

A professional React-based dashboard for analyzing mutual fund performance, investor analytics, and market trends.

## Features

- **Industry Overview** — Key performance indicators (AUM, SIP inflows, active schemes)
- **Fund Performance** — Risk vs return analysis with fund rankings and scorecard
- **Investor Analytics** — Geographic distribution, transaction analysis, demographic insights
- **SIP & Market Trends** — Correlation of SIP inflows with market indices, category trends
- **Fund Drill-Through** — Detailed NAV trends and performance for individual funds

## Technology Stack

- **Frontend Framework**: React 19 with TypeScript
- **Router**: TanStack Router (file-based routing)
- **UI Components**: Radix UI with Tailwind CSS
- **Charts**: Recharts for data visualization
- **Build Tool**: Vite
- **State Management**: React Query for API caching

## Getting Started

### Prerequisites

- Node.js 18+
- npm or bun

### Installation

```bash
cd frontend
npm install
# or
bun install
```

### Development Server

```bash
npm run dev
# or
bun run dev
```

The dashboard will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
# or
bun run build
```

### Linting

```bash
npm run lint
# or
bun run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── routes/           # Page components
│   │   ├── index.tsx     # Home / Industry Overview
│   │   ├── fund-performance.tsx
│   │   ├── investor-analytics.tsx
│   │   ├── sip-market-trends.tsx
│   │   ├── funds.$fundId.tsx  # Fund detail drill-through
│   │   └── __root.tsx    # Root layout
│   ├── components/
│   │   ├── dashboard/    # Shared dashboard components
│   │   └── ui/           # Reusable UI components
│   ├── lib/              # Utilities and helpers
│   └── styles/           # Global styles
├── public/
│   ├── api/              # Static data JSON files
│   └── ...
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Data Integration

Dashboard data is loaded from static JSON files (`public/api/dashboard_data.json`) generated from the mutual fund analytics backend. Data updates are triggered by the backend ETL pipeline.

## API Reference

The dashboard expects the following structure in `public/api/dashboard_data.json`:

- `kpis` — Industry KPIs (total AUM, SIP inflows, etc.)
- `aumTrend` — AUM time series
- `aumByAmc` — AUM distribution by fund house
- `funds` — List of all funds with metrics
- `navSeries` — NAV vs benchmark time series for each fund
- `stateAmounts` — Transaction amounts by geographic region
- `txnSplit` — Transaction type breakdown
- And more (see `export_dashboard_json.py` for full structure)

## Performance Notes

- All data is pre-computed and exported as static JSON
- Charts are client-side only (no server-side rendering)
- Large datasets are cached by React Query
- Monthly aggregation reduces data points for performant rendering

## License

Proprietary — Mutual Fund Analytics Project

---

## Contributing

This frontend is part of a larger mutual fund analytics platform. Ensure all changes:

1. Maintain compatibility with the backend data structure
2. Pass ESLint checks
3. Are tested in development mode before deployment
4. Do not introduce external dependencies without justification
