import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
} from "recharts";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import {
  ChartCard,
  EmptyBlock,
  ErrorBlock,
  FilterBar,
  FilterSelect,
  LoadingBlock,
  TooltipBox,
  formatCompact,
  formatCrore,
  formatInr,
} from "@/components/dashboard/ui";
import {
  AGE_GROUPS,
  getAgeGroupSip,
  getMonthlyVolume,
  getStatesSync,
  getTransactionByState,
  getTxnSplit,
} from "@/lib/dashboard-data";
import { ALL } from "@/lib/dashboard-types";

export const Route = createFileRoute("/investor-analytics")({
  head: () => ({
    meta: [
      { title: "Investor Analytics — Fund Analytics Dashboard" },
      {
        name: "description",
        content:
          "Investor behaviour analytics: transaction value by state, SIP vs lumpsum vs redemption split, average SIP by age group and monthly transaction volume.",
      },
      { property: "og:title", content: "Investor Analytics — Fund Analytics Dashboard" },
      {
        property: "og:description",
        content: "State-wise, age-wise and T30/B30 investor transaction analytics.",
      },
    ],
  }),
  component: InvestorAnalytics,
});

const SPLIT_COLORS = ["var(--color-chart-1)", "var(--color-chart-2)", "var(--color-chart-5)"];

function InvestorAnalytics() {
  const [state, setState] = useState(ALL);
  const [ageGroup, setAgeGroup] = useState(ALL);
  const [cityTier, setCityTier] = useState(ALL);

  const byState = useQuery({
    queryKey: ["txn-state", cityTier, ageGroup],
    queryFn: async () => getTransactionByState(cityTier, ageGroup),
  });
  const split = useQuery({ queryKey: ["txn-split", state], queryFn: async () => getTxnSplit(state) });
  const ageSip = useQuery({ queryKey: ["age-sip", cityTier], queryFn: async () => getAgeGroupSip(cityTier) });
  const volume = useQuery({ queryKey: ["volume", state], queryFn: async () => getMonthlyVolume(state) });

  const stateRows = (byState.data ?? []).filter((s) => state === ALL || s.state === state);

  function reset() {
    setState(ALL);
    setAgeGroup(ALL);
    setCityTier(ALL);
  }

  return (
    <DashboardShell
      title="Investor Analytics"
      subtitle="Page 03 — Geography, demographics and transaction behaviour"
    >
      <FilterBar onReset={reset}>
        <FilterSelect label="State" value={state} options={[ALL, ...getStatesSync()]} onChange={setState} />
        <FilterSelect label="Age group" value={ageGroup} options={[ALL, ...AGE_GROUPS]} onChange={setAgeGroup} />
        <FilterSelect label="City tier" value={cityTier} options={[ALL, "T30", "B30"]} onChange={setCityTier} />
      </FilterBar>

      <div className="grid gap-4 xl:grid-cols-3">
        <ChartCard
          title="Transaction amount by state"
          description="Gross transaction value (₹ crore)"
          className="xl:col-span-2"
        >
          {byState.isPending ? (
            <LoadingBlock height={320} />
          ) : byState.isError ? (
            <ErrorBlock message="Could not load state transactions." />
          ) : !stateRows.length ? (
            <EmptyBlock />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={stateRows} margin={{ left: 4, right: 8, top: 8, bottom: 28 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis
                  dataKey="state"
                  angle={-35}
                  textAnchor="end"
                  height={60}
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v: number) => formatCompact(v)}
                />
                <Tooltip cursor={{ fill: "var(--color-accent)" }} content={<TooltipBox formatter={(v) => formatCrore(v)} />} />
                <Bar dataKey="amountCr" name="Transaction value" radius={[4, 4, 0, 0]}>
                  {stateRows.map((s) => (
                    <Cell
                      key={s.state}
                      fill={s.tier === "T30" ? "var(--color-chart-1)" : "var(--color-chart-2)"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard title="Transaction mix" description="SIP vs lumpsum vs redemption">
          {split.isPending ? (
            <LoadingBlock height={320} />
          ) : !split.data?.length ? (
            <EmptyBlock />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={split.data}
                  dataKey="amountCr"
                  nameKey="type"
                  innerRadius={65}
                  outerRadius={105}
                  paddingAngle={3}
                >
                  {split.data.map((s, i) => (
                    <Cell key={s.type} fill={SPLIT_COLORS[i % SPLIT_COLORS.length]} stroke="var(--color-card)" />
                  ))}
                </Pie>
                <Tooltip content={<TooltipBox formatter={(v) => formatCrore(v)} />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard title="Average SIP by age group" description="Mean monthly SIP ticket (₹)">
          {ageSip.isPending ? (
            <LoadingBlock height={300} />
          ) : !ageSip.data?.length ? (
            <EmptyBlock />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ageSip.data} margin={{ left: 4, right: 8, top: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="ageGroup" tick={{ fontSize: 11 }} stroke="var(--color-muted-foreground)" tickLine={false} />
                <YAxis
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v: number) => formatCompact(v)}
                />
                <Tooltip cursor={{ fill: "var(--color-accent)" }} content={<TooltipBox formatter={(v) => formatInr(v)} />} />
                <Bar dataKey="avgSipAmount" name="Avg SIP" fill="var(--color-chart-3)" radius={[4, 4, 0, 0]} barSize={38} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard title="Monthly transaction volume" description="Transaction count, 2024–2025" className="xl:col-span-2">
          {volume.isPending ? (
            <LoadingBlock height={300} />
          ) : !volume.data?.length ? (
            <EmptyBlock />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={volume.data} margin={{ left: 4, right: 12, top: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="month" interval={2} tick={{ fontSize: 11 }} stroke="var(--color-muted-foreground)" tickLine={false} />
                <YAxis
                  tick={{ fontSize: 11 }}
                  stroke="var(--color-muted-foreground)"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v: number) => formatCompact(v)}
                />
                <Tooltip content={<TooltipBox formatter={(v) => v.toLocaleString("en-IN")} />} />
                <Line
                  type="monotone"
                  dataKey="transactions"
                  name="Transactions"
                  stroke="var(--color-chart-1)"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </div>
    </DashboardShell>
  );
}
