import { cn } from "@/lib/utils";
import { AlertCircle, Inbox } from "lucide-react";
import type { ReactNode } from "react";

/* --------------------------------- format --------------------------------- */

export function formatCrore(value: number) {
  if (Math.abs(value) >= 100_000) return `₹${(value / 100_000).toFixed(2)}L Cr`;
  if (Math.abs(value) >= 1_000) return `₹${(value / 1_000).toFixed(1)}K Cr`;
  return `₹${value.toFixed(0)} Cr`;
}

export function formatInr(value: number) {
  return `₹${value.toLocaleString("en-IN")}`;
}

export function formatCompact(value: number) {
  return value.toLocaleString("en-IN", { notation: "compact", maximumFractionDigits: 1 });
}

export function formatPct(value: number) {
  return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}

/* ---------------------------------- cards --------------------------------- */

export function KpiCard({
  label,
  value,
  caption,
  accent,
}: {
  label: string;
  value: string;
  caption: string;
  accent?: boolean;
}) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border border-border bg-card p-5 shadow-sm transition-shadow hover:shadow-md",
        accent && "bg-primary text-primary-foreground",
      )}
    >
      <p className={cn("text-xs font-medium uppercase tracking-wider", accent ? "opacity-80" : "text-muted-foreground")}>
        {label}
      </p>
      <p className="mt-2 text-3xl font-semibold tabular-nums tracking-tight">{value}</p>
      <p className={cn("mt-1 text-xs", accent ? "opacity-75" : "text-muted-foreground")}>{caption}</p>
      <div
        aria-hidden
        className={cn(
          "absolute -right-6 -top-6 size-20 rounded-full",
          accent ? "bg-primary-foreground/10" : "bg-accent",
        )}
      />
    </div>
  );
}

export function ChartCard({
  title,
  description,
  actions,
  className,
  children,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
  className?: string;
  children: ReactNode;
}) {
  return (
    <section className={cn("rounded-xl border border-border bg-card p-5 shadow-sm", className)}>
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold tracking-tight text-card-foreground">{title}</h2>
          {description && <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>}
        </div>
        {actions}
      </div>
      {children}
    </section>
  );
}

/* --------------------------------- states --------------------------------- */

export function LoadingBlock({ height = 280 }: { height?: number }) {
  return (
    <div
      role="status"
      aria-label="Loading chart"
      className="animate-pulse rounded-lg bg-muted"
      style={{ height }}
    />
  );
}

export function EmptyBlock({ message = "No data matches the current filters." }: { message?: string }) {
  return (
    <div className="grid h-[280px] place-items-center rounded-lg border border-dashed border-border text-center">
      <div className="px-6">
        <Inbox className="mx-auto size-6 text-muted-foreground" aria-hidden />
        <p className="mt-2 text-sm text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}

export function ErrorBlock({ message }: { message: string }) {
  return (
    <div className="grid h-[280px] place-items-center rounded-lg border border-destructive/40 bg-destructive/5 text-center">
      <div className="px-6">
        <AlertCircle className="mx-auto size-6 text-destructive" aria-hidden />
        <p className="mt-2 text-sm text-destructive">{message}</p>
      </div>
    </div>
  );
}

/* --------------------------------- filters -------------------------------- */

export function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  const id = `filter-${label.replace(/\s+/g, "-").toLowerCase()}`;
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-9 min-w-[9rem] rounded-lg border border-input bg-card px-2.5 text-sm text-foreground shadow-sm outline-none transition-colors focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/40"
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </div>
  );
}

export function FilterBar({ children, onReset }: { children: ReactNode; onReset: () => void }) {
  return (
    <div className="mb-6 flex flex-wrap items-end gap-3 rounded-xl border border-border bg-card p-4 shadow-sm">
      {children}
      <button
        type="button"
        onClick={onReset}
        className="h-9 rounded-lg border border-input bg-background px-3 text-sm font-medium text-foreground transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40"
      >
        Reset filters
      </button>
    </div>
  );
}

/* --------------------------------- tooltip -------------------------------- */

export function TooltipBox({
  active,
  payload,
  label,
  formatter,
}: {
  active?: boolean;
  payload?: { name?: string; value?: number | string; color?: string; dataKey?: string | number }[];
  label?: string | number;
  formatter?: (value: number, key: string) => string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-popover px-3 py-2 text-xs shadow-lg">
      {label !== undefined && <p className="mb-1 font-medium text-popover-foreground">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} className="flex items-center gap-2 text-muted-foreground">
          <span className="size-2 rounded-full" style={{ background: p.color }} aria-hidden />
          <span>{p.name ?? p.dataKey}</span>
          <span className="ml-auto font-medium tabular-nums text-popover-foreground">
            {formatter && typeof p.value === "number"
              ? formatter(p.value, String(p.dataKey ?? ""))
              : typeof p.value === "number"
                ? p.value.toLocaleString("en-IN")
                : p.value}
          </span>
        </p>
      ))}
    </div>
  );
}
