import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
  BarChart,
} from "recharts";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import {
  ChartCard,
  EmptyBlock,
  ErrorBlock,
  LoadingBlock,
  TooltipBox,
  formatCompact,
  formatCrore,
} from "@/components/dashboard/ui";
import { getCategoryInflowHeatmap, getSipVsMarket, getTopCategoriesFy25 } from "@/lib/dashboard-data";

export const Route = createFileRoute("/sip-market-trends")({
  head: () => ({
    meta: [
      { title: "SIP & Market Trends — Fund Analytics Dashboard" },
      {
        name: "description",
        content:
          "Monthly SIP inflows against Nifty 50 from 2022 to 2025, quarterly category inflow heatmap and the top five FY25 categories by net inflow.",
      },
      { property: "og:title", content: "SIP & Market Trends — Fund Analytics Dashboard" },
      {
        property: "og:description",
        content: "SIP inflow versus Nifty 50 and category-level net inflow trends.",
      },
    ],
  }),
  component: SipMarketTrends,
});

function heatColor(value: number, min: number, max: number) {
  if (value < 0) return "var(--color-destructive)";
  const t = max === min ? 0.5 : (value - min) / (max - min);
  return `color-mix(in oklab, var(--color-chart-1) ${Math.round(12 + t * 78)}%, var(--color-card))`;
}

function SipMarketTrends() {
  const sip = useQuery({ queryKey: ["sip-market"], queryFn: async () => getSipVsMarket() });
  const heat = useQuery({ queryKey: ["cat-heatmap"], queryFn: async () => getCategoryInflowHeatmap() });
  const top = useQuery({ queryKey: ["top-cat"], queryFn: async () => getTopCategoriesFy25() });

  const periods = [...new Set((heat.data ?? []).map((c) => c.period))];
  const categories = [...new Set((heat.data ?? []).map((c) => c.category))];
  const values = (heat.data ?? []).map((c) => c.netInflowCr);
  const min = values.length ? Math.min(...values) : 0;
  const max = values.length ? Math.max(...values) : 0;

  return (
    <DashboardShell
      title="SIP & Market Trends"
      subtitle="Page 04 — SIP flows against market performance and category rotation"
    >
      <ChartCard
        title="SIP inflow vs Nifty 50"
        description="Monthly SIP contribution (bars, ₹ crore) against Nifty 50 close (line), 2022–2025"
      >
        {sip.isPending ? (
          <LoadingBlock height={340} />
        ) : sip.isError ? (
          <ErrorBlock message="Could not load SIP and market data." />
        ) : !sip.data?.length ? (
          <EmptyBlock />
        ) : (
          <ResponsiveContainer width="100%" height={340}>
            <ComposedChart data={sip.data} margin={{ left: 4, right: 12, top: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="month" interval={5} tick={{ fontSize: 11 }} stroke="var(--color-muted-foreground)" tickLine={false} />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 11 }}
                stroke="var(--color-muted-foreground)"
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => formatCompact(v)}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                domain={["dataMin - 1500", "dataMax + 1500"]}
                tick={{ fontSize: 11 }}
                stroke="var(--color-muted-foreground)"
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => formatCompact(v)}
              />
              <Tooltip
                cursor={{ fill: "var(--color-accent)" }}
                content={
                  <TooltipBox
                    formatter={(v, key) => (key === "sipInflowCr" ? formatCrore(v) : v.toLocaleString("en-IN"))}
                  />
                }
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar yAxisId="left" dataKey="sipInflowCr" name="SIP inflow" fill="var(--color-chart-2)" radius={[3, 3, 0, 0]} />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="nifty50"
                name="Nifty 50"
                stroke="var(--color-chart-5)"
                strokeWidth={2.5}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </ChartCard>

      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <ChartCard title="Category inflow heatmap" description="Net inflow by category and FY25 quarter (₹ crore)">
          {heat.isPending ? (
            <LoadingBlock height={320} />
          ) : !heat.data?.length ? (
            <EmptyBlock />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[420px] border-separate border-spacing-1 text-xs">
                <thead>
                  <tr>
                    <th className="text-left font-medium text-muted-foreground">Category</th>
                    {periods.map((p) => (
                      <th key={p} className="px-2 font-medium text-muted-foreground">
                        {p}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {categories.map((cat) => (
                    <tr key={cat}>
                      <td className="whitespace-nowrap pr-2 font-medium text-foreground">{cat}</td>
                      {periods.map((p) => {
                        const cell = heat.data.find((c) => c.category === cat && c.period === p);
                        const v = cell?.netInflowCr ?? 0;
                        return (
                          <td key={p} className="p-0">
                            <div
                              title={`${cat} · ${p}: ${formatCrore(v)}`}
                              className="grid h-10 place-items-center rounded-md text-[11px] font-medium tabular-nums text-foreground"
                              style={{ background: heatColor(v, min, max) }}
                            >
                              {formatCompact(v)}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </ChartCard>

        <ChartCard title="Top 5 categories — FY25 net inflow" description="Highest net inflow categories (₹ crore)">
          {top.isPending ? (
            <LoadingBlock height={320} />
          ) : !top.data?.length ? (
            <EmptyBlock />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={top.data} layout="vertical" margin={{ left: 20, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v: number) => formatCompact(v)}
                />
                <YAxis
                  type="category"
                  dataKey="category"
                  width={90}
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip cursor={{ fill: "var(--color-accent)" }} content={<TooltipBox formatter={(v) => formatCrore(v)} />} />
                <Bar dataKey="netInflowCr" name="Net inflow" fill="var(--color-chart-1)" radius={[0, 4, 4, 0]} barSize={22} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </div>
    </DashboardShell>
  );
}
