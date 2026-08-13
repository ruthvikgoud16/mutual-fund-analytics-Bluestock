"""FastAPI server for Bluestock Mutual Fund Analytics.

Serves 100% REAL data from mutual_fund_analytics.db to the Lovable React frontend.
Endpoints:
  GET /api/dashboard-data
  GET /api/kpis
  GET /api/aum-trend
  GET /api/aum-amc
  GET /api/funds
  GET /api/funds/{fund_id}
  GET /api/nav/{fund_id}
  GET /api/state-transactions
  GET /api/transaction-split
  GET /api/age-sip
  GET /api/monthly-volume
  GET /api/sip-market
  GET /api/category-heatmap
  GET /api/top-categories
"""

from export_dashboard_json import export_data
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Bluestock Mutual Fund Analytics API",
    description="Real data backend API serving mutual_fund_analytics.db",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_CACHE = None


def get_cached_data():
    global _CACHE
    if _CACHE is None:
        _CACHE = export_data()
    return _CACHE


@app.get("/api/dashboard-data")
def get_all_dashboard_data():
    """Return all dashboard datasets in a single bundle for instant UI loading."""
    return get_cached_data()


@app.get("/api/kpis")
def get_kpis():
    data = get_cached_data()
    return data["kpis"]


@app.get("/api/aum-trend")
def get_aum_trend():
    data = get_cached_data()
    return data["aumTrend"]


@app.get("/api/aum-amc")
def get_aum_by_amc():
    data = get_cached_data()
    return data["aumByAmc"]


@app.get("/api/funds")
def get_funds():
    data = get_cached_data()
    return data["funds"]


@app.get("/api/funds/{fund_id}")
def get_fund_by_id(fund_id: str):
    data = get_cached_data()
    fund = next((f for f in data["funds"] if f["fundId"] == fund_id), None)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    return fund


@app.get("/api/nav/{fund_id}")
def get_nav_series(fund_id: str):
    data = get_cached_data()
    series = data["navSeries"].get(fund_id)
    if series is None:
        # Fallback to first available series if exact code match is absent
        first_key = next(iter(data["navSeries"].keys()))
        return data["navSeries"][first_key]
    return series


@app.get("/api/state-transactions")
def get_state_transactions(tier: str = "All", ageGroup: str = "All"):
    data = get_cached_data()
    states = data["stateAmounts"]
    if tier != "All":
        states = [s for s in states if s["tier"] == tier]
    return states


@app.get("/api/transaction-split")
def get_transaction_split(state: str = "All"):
    data = get_cached_data()
    if state != "All" and state in data["stateFilteredCache"]:
        return data["stateFilteredCache"][state]["txnSplit"]
    return data["txnSplit"]


@app.get("/api/age-sip")
def get_age_sip(tier: str = "All"):
    data = get_cached_data()
    if tier != "All" and tier in data["tierAgeCache"]:
        return data["tierAgeCache"][tier]
    return data["ageGroupSip"]


@app.get("/api/monthly-volume")
def get_monthly_volume(state: str = "All"):
    data = get_cached_data()
    if state != "All" and state in data["stateFilteredCache"]:
        return data["stateFilteredCache"][state]["monthlyVolume"]
    return data["monthlyVolume"]


@app.get("/api/sip-market")
def get_sip_vs_market():
    data = get_cached_data()
    return data["sipVsMarket"]


@app.get("/api/category-heatmap")
def get_category_heatmap():
    data = get_cached_data()
    return data["categoryHeatmap"]


@app.get("/api/top-categories")
def get_top_categories():
    data = get_cached_data()
    return data["topCategoriesFy25"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
