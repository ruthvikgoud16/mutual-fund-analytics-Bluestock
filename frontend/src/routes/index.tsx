import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import {
  ChartCard,
  EmptyBlock,
  ErrorBlock,
  KpiCard,
  LoadingBlock,
  TooltipBox,
  formatCrore,
} from "@/components/dashboard/ui";
import { getAumByAmc, getIndustryAumTrend, getIndustryKpis } from "@/lib/dashboard-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Industry Overview — Fund Analytics Dashboard" },
      {
        name: "description",
        content:
          "Indian mutual fund industry overview: total AUM, monthly SIP inflows, folios, active schemes, AUM trend 2022-2025 and AUM by AMC.",
      },
      { property: "og:title", content: "Industry Overview — Fund Analytics Dashboard" },
      {
        property: "og:description",
        content: "Total AUM, SIP inflows, folios, schemes and AMC-wise AUM for the Indian mutual fund industry.",
      },
    ],
  }),
  component: IndustryOverview,
});

function IndustryOverview() {
  const kpis = useQuery({ queryKey: ["kpis"], queryFn: async () => getIndustryKpis() });
  const trend = useQuery({ queryKey: ["aum-trend"], queryFn: async () => getIndustryAumTrend() });
  const amc = useQuery({ queryKey: ["aum-amc"], queryFn: async () => getAumByAmc() });

  return (
    <DashboardShell
      title="Industry Overview"
      subtitle="Page 01 — Indian mutual fund industry at a glance, FY22 to FY25"
    >
      <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.isPending ? (
          Array.from({ length: 4 }).map((_, i) => <LoadingBlock key={i} height={124} />)
        ) : kpis.isError || !kpis.data ? (
          <div className="sm:col-span-2 xl:col-span-4">
            <ErrorBlock message="Could not load industry KPIs." />
          </div>
        ) : (
          <>
            <KpiCard
              accent
              label="Total AUM"
              value={formatCrore(kpis.data.totalAumCr)}
              caption="Industry assets under management"
            />
            <KpiCard
              label="SIP Inflows"
              value={formatCrore(kpis.data.sipInflowCr)}
              caption="Latest monthly SIP contribution"
            />
            <KpiCard
              label="Folios"
              value={`${kpis.data.foliosCr.toFixed(2)} Cr`}
              caption="Total investor folios"
            />
            <KpiCard
              label="Schemes"
              value={kpis.data.schemes.toLocaleString("en-IN")}
              caption="Active schemes across AMCs"
            />
          </>
        )}
      </div>

      <div className="grid gap-4 xl:grid-cols-5">
        <ChartCard
          title="Industry AUM trend"
          description="Monthly closing AUM, 2022–2025 (₹ crore)"
          className="xl:col-span-3"
        >
          {trend.isPending ? (
            <LoadingBlock height={320} />
          ) : trend.isError ? (
            <ErrorBlock message="Could not load the AUM trend." />
          ) : !trend.data?.length ? (
            <EmptyBlock />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={trend.data} margin={{ left: 4, right: 8, top: 8 }}>
                <defs>
                  <linearGradient id="aumFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-chart-1)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="var(--color-chart-1)" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis
                  dataKey="period"
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  interval={5}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v: number) => `${(v / 100_000).toFixed(1)}L`}
                />
                <Tooltip content={<TooltipBox formatter={(v) => formatCrore(v)} />} />
                <Area
                  type="monotone"
                  dataKey="value"
                  name="AUM"
                  stroke="var(--color-chart-1)"
                  strokeWidth={2}
                  fill="url(#aumFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard title="AUM by AMC" description="Top fund houses by AUM (₹ crore)" className="xl:col-span-2">
          {amc.isPending ? (
            <LoadingBlock height={320} />
          ) : amc.isError ? (
            <ErrorBlock message="Could not load AMC AUM." />
          ) : !amc.data?.length ? (
            <EmptyBlock />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={amc.data} layout="vertical" margin={{ left: 24, right: 12 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickFormatter={(v: number) => `${(v / 100_000).toFixed(1)}L`}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="amc"
                  width={110}
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip cursor={{ fill: "var(--color-accent)" }} content={<TooltipBox formatter={(v) => formatCrore(v)} />} />
                <Bar dataKey="aumCr" name="AUM" fill="var(--color-chart-2)" radius={[0, 4, 4, 0]} barSize={14} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </div>
    </DashboardShell>
  );
}
