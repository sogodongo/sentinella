import { fetchEvents, fetchBOMs } from "@/lib/api"
import { StatusBadge } from "@/components/status-badge"

export default async function DashboardPage() {
  const [eventsData, bomsData] = await Promise.allSettled([
    fetchEvents(5),
    fetchBOMs(),
  ])

  const events = eventsData.status === "fulfilled" ? eventsData.value : null
  const boms = bomsData.status === "fulfilled" ? bomsData.value : null

  const allowed = events?.events.filter(e => e.policy_decision === "allowed").length ?? 0
  const denied = events?.events.filter(e => e.policy_decision === "denied").length ?? 0

  return (
    <div className="max-w-4xl">
      <h1 className="text-xl font-semibold text-slate-900 mb-1">Dashboard</h1>
      <p className="text-slate-500 text-sm mb-8">AI governance overview</p>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard label="Total Events" value={events?.total ?? "—"} />
        <StatCard label="Allowed" value={allowed} color="text-emerald-600" />
        <StatCard label="Denied" value={denied} color="text-red-600" />
      </div>

      <section className="mb-8">
        <h2 className="text-sm font-medium text-slate-700 mb-3">Recent Decisions</h2>
        {events ? (
          <div className="bg-white rounded-lg border border-slate-200 divide-y divide-slate-100">
            {events.events.map(event => (
              <div key={event.event_id} className="flex items-center justify-between px-4 py-3">
                <div>
                  <span className="font-mono text-xs text-slate-700">{event.model}</span>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {new Date(event.timestamp).toLocaleString()}
                  </p>
                </div>
                <StatusBadge decision={event.policy_decision} />
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-400 text-sm">Ledger service unavailable</p>
        )}
      </section>

      <section>
        <h2 className="text-sm font-medium text-slate-700 mb-3">Model Registry</h2>
        <p className="text-slate-500 text-sm">
          {boms
            ? `${boms.total} model${boms.total !== 1 ? "s" : ""} registered`
            : "AI-BOM service unavailable"}
        </p>
      </section>
    </div>
  )
}

function StatCard({
  label,
  value,
  color = "text-slate-900",
}: {
  label: string
  value: number | string
  color?: string
}) {
  return (
    <div className="bg-white rounded-lg border border-slate-200 px-4 py-4">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className={`text-2xl font-semibold ${color}`}>{value}</p>
    </div>
  )
}
