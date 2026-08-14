import { Link } from "@tanstack/react-router";
import { BarChart3, Gauge, LineChart, Users, Download } from "lucide-react";
import type { ReactNode } from "react";
import { DATA_SOURCE_LABEL, IS_LIVE_DATA } from "@/lib/dashboard-data";

const NAV = [
  { to: "/", label: "Industry Overview", page: "01", icon: Gauge },
  { to: "/fund-performance", label: "Fund Performance", page: "02", icon: BarChart3 },
  { to: "/investor-analytics", label: "Investor Analytics", page: "03", icon: Users },
  { to: "/sip-market-trends", label: "SIP & Market Trends", page: "04", icon: LineChart },
] as const;

export function DashboardShell({
  title,
  subtitle,
  actions,
  children,
}: {
  title: string;
  subtitle: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto flex max-w-[1600px] flex-col lg:flex-row">
        <aside className="sticky top-0 z-30 shrink-0 border-b border-sidebar-border bg-sidebar lg:h-screen lg:w-64 lg:border-r lg:border-b-0">
          <div className="flex items-center gap-3 px-5 py-5">
            <div className="grid size-9 place-items-center rounded-lg bg-primary font-bold text-primary-foreground">
              B
            </div>
            <div className="leading-tight">
              <p className="text-sm font-semibold tracking-tight text-sidebar-foreground">Fund Analytics</p>
              <p className="text-xs text-muted-foreground">Dashboard</p>
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto px-3 pb-3 lg:flex-col lg:overflow-visible">
            {NAV.map(({ to, label, page, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className="group flex shrink-0 items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                activeOptions={{ exact: to === "/" }}
                activeProps={{
                  className: "bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary",
                }}
              >
                <Icon className="size-4 shrink-0" aria-hidden />
                <span className="whitespace-nowrap font-medium">{label}</span>
                <span className="ml-auto hidden text-[10px] tabular-nums opacity-60 lg:inline">{page}</span>
              </Link>
            ))}
          </nav>
          <div className="hidden px-5 pb-5 lg:mt-auto lg:block">
            <div className="rounded-lg border border-sidebar-border bg-sidebar-accent/50 p-3">
              <p className="flex items-center gap-1.5 text-xs font-medium text-sidebar-foreground">
                <Download className="size-3.5" aria-hidden /> Exports
              </p>
              <p className="mt-1 text-[11px] leading-snug text-muted-foreground">
                Dashboard.pdf and 4 page PNGs are rendered from these pages.
              </p>
            </div>
          </div>
        </aside>

        <main className="min-w-0 flex-1 px-4 py-6 sm:px-8 sm:py-8">
          <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">{title}</h1>
              <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
            </div>
            <div className="flex items-center gap-3">{actions}</div>
          </header>
          {!IS_LIVE_DATA && (
            <p className="mb-6 rounded-lg border border-warning/40 bg-warning/10 px-3 py-2 text-xs font-medium text-warning-foreground">
              {DATA_SOURCE_LABEL}
            </p>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
