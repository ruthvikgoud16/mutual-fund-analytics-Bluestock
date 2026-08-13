import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowLeft } from "lucide-react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import {
  ChartCard,
  ErrorBlock,
  LoadingBlock,
  TooltipBox,
  formatCrore,
  formatPct,
} from "@/components/dashboard/ui";
import { fetchFundById, getNavSeries } from "@/lib/dashboard-data";

export const Route = createFileRoute("/funds/$fundId")({
  loader: async ({ params }) => {
    const fund = await fetchFundById(params.fundId);
    if (!fund) throw notFound();
    return { fund };
  },
  head: ({ loaderData }) => {
    if (!loaderData)
      return {
        meta: [{ title: "Fund not found — Bluestock" }, { name: "robots", content: "noindex" }],
      };
    const t = `${loaderData.fund.fundName} — Fund Detail`;
    return {
      meta: [
        { title: t },
        {
          name: "description",
          content: `${loaderData.fund.fundName}: NAV vs benchmark, CAGR, Sharpe, Sortino, alpha, beta, max drawdown, expense ratio and composite score.`,
        },
        { property: "og:title", content: t },
        {
          property: "og:description",
          content: `Risk and return detail for ${loaderData.fund.fundName} (${loaderData.fund.category}, ${loaderData.fund.plan}).`,
        },
      ],
    };
  },
  notFoundComponent: FundNotFound,
  component: FundDetail,
});

function FundNotFound() {
  return (
    <DashboardShell title="Fund not found" subtitle="This fund is not present in the current dataset">
      <ErrorBlock message="No fund matches that identifier." />
    </DashboardShell>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: "pos" | "neg" }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">{label}</p>
      <p
        className={`mt-1 text-xl font-semibold tabular-nums ${
          tone === "neg" ? "text-destructive" : tone === "pos" ? "text-success" : "text-foreground"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function FundDetail() {
  const { fund } = Route.useLoaderData();
  const nav = useQuery({ queryKey: ["nav", fund.fundId], queryFn: async () => getNavSeries(fund.fundId) });

  return (
    <DashboardShell
      title={fund.fundName}
      subtitle={`${fund.amc} · ${fund.category} · ${fund.plan} plan`}
      actions={
        <Link
          to="/fund-performance"
          className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-input bg-card px-3 text-sm font-medium text-foreground transition-colors hover:bg-accent"
        >
          <ArrowLeft className="size-4" aria-hidden /> Back to scorecard
        </Link>
      }
    >
      <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="AUM" value={formatCrore(fund.aumCr)} />
        <Metric label="CAGR 3Y" value={formatPct(fund.cagr3y)} tone="pos" />
        <Metric label="Std deviation" value={`${fund.stdDev}%`} />
        <Metric label="Composite score" value={String(fund.compositeScore)} />
        <Metric label="Sharpe" value={String(fund.sharpe)} />
        <Metric label="Sortino" value={String(fund.sortino)} />
        <Metric label="Alpha" value={formatPct(fund.alpha)} tone={fund.alpha < 0 ? "neg" : "pos"} />
        <Metric label="Beta" value={String(fund.beta)} />
        <Metric label="Max drawdown" value={`${fund.maxDrawdown}%`} tone="neg" />
        <Metric label="Expense ratio" value={`${fund.expenseRatio}%`} />
        <Metric label="Plan" value={fund.plan} />
        <Metric label="Category" value={fund.category} />
      </div>

      <ChartCard title="NAV vs benchmark" description="Fund NAV against Nifty 50 TRI, rebased to 100 (2022–2025)">
        {nav.isPending ? (
          <LoadingBlock height={360} />
        ) : nav.isError ? (
          <ErrorBlock message="Could not load the NAV series." />
        ) : (
          <ResponsiveContainer width="100%" height={360}>
            <LineChart data={nav.data} margin={{ left: 4, right: 12, top: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="date" interval={4} tick={{ fontSize: 11 }} stroke="var(--color-muted-foreground)" tickLine={false} />
              <YAxis tick={{ fontSize: 11 }} stroke="var(--color-muted-foreground)" tickLine={false} axisLine={false} />
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
    </DashboardShell>
  );
}
