import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
  Legend,
} from "recharts";
import { ArrowUpDown, ChevronRight } from "lucide-react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import {
  ChartCard,
  EmptyBlock,
  ErrorBlock,
  FilterBar,
  FilterSelect,
  LoadingBlock,
  TooltipBox,
  formatCrore,
} from "@/components/dashboard/ui";
import { getCategories, getFundHouses, getFunds, getNavSeries } from "@/lib/dashboard-data";
import type { FundRow } from "@/lib/dashboard-types";
import { ALL } from "@/lib/dashboard-types";

export const Route = createFileRoute("/fund-performance")({
  head: () => ({
    meta: [
      { title: "Fund Performance — Fund Analytics Dashboard" },
      {
        name: "description",
        content:
          "Risk vs return scatter, sortable fund scorecard with Sharpe, Sortino, alpha, beta and drawdown, plus NAV versus benchmark.",
      },
      { property: "og:title", content: "Fund Performance — Fund Analytics Dashboard" },
      {
        property: "og:description",
        content: "Compare mutual funds on return, risk, Sharpe, Sortino and composite score.",
      },
    ],
  }),
  component: FundPerformance,
});

type SortKey = keyof Pick<
  FundRow,
  "fundName" | "aumCr" | "cagr3y" | "stdDev" | "sharpe" | "sortino" | "maxDrawdown" | "expenseRatio" | "compositeScore"
>;

const COLUMNS: { key: SortKey; label: string; numeric?: boolean }[] = [
  { key: "fundName", label: "Fund" },
  { key: "aumCr", label: "AUM", numeric: true },
  { key: "cagr3y", label: "CAGR 3Y", numeric: true },
  { key: "stdDev", label: "Std Dev", numeric: true },
  { key: "sharpe", label: "Sharpe", numeric: true },
  { key: "sortino", label: "Sortino", numeric: true },
  { key: "maxDrawdown", label: "Max DD", numeric: true },
  { key: "expenseRatio", label: "Expense", numeric: true },
  { key: "compositeScore", label: "Score", numeric: true },
];

function FundPerformance() {
  const navigate = useNavigate();
  const [amc, setAmc] = useState(ALL);
  const [category, setCategory] = useState(ALL);
  const [plan, setPlan] = useState(ALL);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("compositeScore");
  const [sortDesc, setSortDesc] = useState(true);

  const funds = useQuery({ queryKey: ["funds"], queryFn: async () => getFunds() });

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const rows = (funds.data ?? []).filter(
      (f) =>
        (amc === ALL || f.amc === amc) &&
        (category === ALL || f.category === category) &&
        (plan === ALL || f.plan === plan) &&
        (!q || f.fundName.toLowerCase().includes(q) || f.amc.toLowerCase().includes(q)),
    );
    return [...rows].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === "string" || typeof bv === "string")
        return sortDesc ? String(bv).localeCompare(String(av)) : String(av).localeCompare(String(bv));
      return sortDesc ? Number(bv) - Number(av) : Number(av) - Number(bv);
    });
  }, [funds.data, amc, category, plan, search, sortKey, sortDesc]);

  const selected = filtered.find((f) => f.fundId === selectedId) ?? filtered[0];
  const nav = useQuery({
    queryKey: ["nav", selected?.fundId],
    queryFn: async () => getNavSeries(selected!.fundId),
    enabled: !!selected,
  });

  function toggleSort(key: SortKey) {
    if (key === sortKey) setSortDesc((d) => !d);
    else {
      setSortKey(key);
      setSortDesc(true);
    }
  }

  function reset() {
    setAmc(ALL);
    setCategory(ALL);
    setPlan(ALL);
    setSearch("");
    setSelectedId(null);
  }


  return (
    <DashboardShell
      title="Fund Performance"
      subtitle="Page 02 — Risk-adjusted performance, scorecard and NAV vs benchmark"
    >
      <FilterBar onReset={reset}>
        <FilterSelect label="Fund house" value={amc} options={[ALL, ...getFundHouses()]} onChange={setAmc} />
        <FilterSelect label="Category" value={category} options={[ALL, ...getCategories()]} onChange={setCategory} />
        <FilterSelect label="Plan" value={plan} options={[ALL, "Direct", "Regular"]} onChange={setPlan} />
        <label className="flex flex-col gap-1">
          <span className="text-[11px] uppercase tracking-wider text-muted-foreground">Search fund</span>
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Fund or AMC name"
            className="h-8 w-52 rounded-md border border-border bg-background px-2 text-sm text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
          />
        </label>

        <p className="ml-auto text-xs text-muted-foreground">
          {filtered.length} of {funds.data?.length ?? 0} funds
        </p>
      </FilterBar>

      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Return vs risk" description="3Y CAGR (X) vs standard deviation (Y); bubble size = AUM">
          {funds.isPending ? (
            <LoadingBlock height={320} />
          ) : funds.isError ? (
            <ErrorBlock message="Could not load fund metrics." />
          ) : !filtered.length ? (
            <EmptyBlock />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <ScatterChart margin={{ left: 4, right: 12, top: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis
                  type="number"
                  dataKey="cagr3y"
                  name="CAGR 3Y"
                  unit="%"
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                />
                <YAxis
                  type="number"
                  dataKey="stdDev"
                  name="Std Dev"
                  unit="%"
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                  axisLine={false}
                />
                <ZAxis type="number" dataKey="aumCr" range={[30, 420]} name="AUM" />
                <Tooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  content={({ active, payload }) => {
                    const f = payload?.[0]?.payload as FundRow | undefined;
                    if (!active || !f) return null;
                    return (
                      <div className="rounded-lg border border-border bg-popover px-3 py-2 text-xs shadow-lg">
                        <p className="font-medium text-popover-foreground">{f.fundName}</p>
                        <p className="text-muted-foreground">
                          {f.category} · {f.plan}
                        </p>
                        <p className="mt-1 text-popover-foreground">
                          CAGR {f.cagr3y}% · Risk {f.stdDev}% · {formatCrore(f.aumCr)}
                        </p>
                      </div>
                    );
                  }}
                />
                <Scatter data={filtered} name="Funds" fill="var(--color-chart-1)" fillOpacity={0.55} />
              </ScatterChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard
          title="NAV vs benchmark"
          description={selected ? `${selected.fundName} · rebased to 100` : "Select a fund"}
        >
          {!selected ? (
            <EmptyBlock message="No fund matches the current filters." />
          ) : nav.isPending ? (
            <LoadingBlock height={320} />
          ) : nav.isError ? (
            <ErrorBlock message="Could not load the NAV series." />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={nav.data} margin={{ left: 4, right: 12, top: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis
                  dataKey="date"
                  interval={5}
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip content={<TooltipBox />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line type="monotone" dataKey="nav" name="Fund NAV" stroke="var(--color-chart-1)" strokeWidth={2} dot={false} />
                <Line
                  type="monotone"
                  dataKey="benchmark"
                  name="Nifty 50 TRI"
                  stroke="var(--color-chart-4)"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </div>

      <ChartCard
        title="Fund scorecard"
        description="Click a row to load its NAV chart; use the chevron (or Enter) to drill through to fund detail"
        className="mt-4"
      >
        {funds.isPending ? (
          <LoadingBlock height={360} />
        ) : !filtered.length ? (
          <EmptyBlock />
        ) : (
          <div className="max-h-[460px] overflow-auto rounded-lg border border-border">
            <table className="w-full min-w-[820px] text-sm">
              <thead className="sticky top-0 z-10 bg-muted">
                <tr>
                  {COLUMNS.map((c) => (
                    <th
                      key={c.key}
                      scope="col"
                      className={`px-3 py-2.5 font-medium ${c.numeric ? "text-right" : "text-left"}`}
                    >
                      <button
                        type="button"
                        onClick={() => toggleSort(c.key)}
                        aria-label={`Sort by ${c.label}`}
                        className={`inline-flex items-center gap-1 text-xs uppercase tracking-wider transition-colors hover:text-foreground ${
                          sortKey === c.key ? "text-foreground" : "text-muted-foreground"
                        }`}
                      >
                        {c.label}
                        <ArrowUpDown className="size-3" aria-hidden />
                      </button>
                    </th>
                  ))}
                  <th className="w-8" />
                </tr>
              </thead>
              <tbody>
                {filtered.slice(0, 60).map((f) => (
                  <tr
                    key={f.fundId}
                    tabIndex={0}
                    onClick={() => setSelectedId(f.fundId)}
                    onDoubleClick={() => navigate({ to: "/funds/$fundId", params: { fundId: f.fundId } })}
                    onKeyDown={(e) => {
                      if (e.key === "Enter")
                        navigate({ to: "/funds/$fundId", params: { fundId: f.fundId } });
                      if (e.key === " ") {
                        e.preventDefault();
                        setSelectedId(f.fundId);
                      }
                    }}
                    aria-selected={selected?.fundId === f.fundId}
                    className={`cursor-pointer border-t border-border transition-colors hover:bg-accent focus:outline-none ${
                      selected?.fundId === f.fundId ? "bg-accent" : ""
                    }`}
                  >
                    <td className="px-3 py-2.5">
                      <p className="font-medium text-foreground">{f.fundName}</p>
                      <p className="text-xs text-muted-foreground">
                        {f.category} · {f.plan}
                      </p>
                    </td>
                    <td className="px-3 py-2.5 text-right tabular-nums">{formatCrore(f.aumCr)}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums">{f.cagr3y}%</td>
                    <td className="px-3 py-2.5 text-right tabular-nums">{f.stdDev}%</td>
                    <td className="px-3 py-2.5 text-right tabular-nums">{f.sharpe}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums">{f.sortino}</td>
                    <td className="px-3 py-2.5 text-right tabular-nums text-destructive">{f.maxDrawdown}%</td>
                    <td className="px-3 py-2.5 text-right tabular-nums">{f.expenseRatio}%</td>
                    <td className="px-3 py-2.5 text-right">
                      <span className="inline-block rounded-md bg-primary/10 px-2 py-0.5 font-semibold tabular-nums text-primary">
                        {f.compositeScore}
                      </span>
                    </td>
                    <td className="pr-2">
                      <button
                        type="button"
                        aria-label={`Open NAV detail for ${f.fundName}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate({ to: "/funds/$fundId", params: { fundId: f.fundId } });
                        }}
                        className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                      >
                        <ChevronRight className="size-4" aria-hidden />
                      </button>
                    </td>
                  </tr>
                ))}

              </tbody>
            </table>
          </div>
        )}
      </ChartCard>
    </DashboardShell>
  );
}
