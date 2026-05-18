import { fetchEvents } from "@/lib/api"
import { EventTable } from "@/components/event-table"

export default async function EventsPage() {
  let data = null
  let error = null

  try {
    data = await fetchEvents(100)
  } catch {
    error = "Ledger service is unavailable."
  }

  return (
    <div className="max-w-5xl">
      <h1 className="text-xl font-semibold text-slate-900 mb-1">Audit Log</h1>
      <p className="text-slate-500 text-sm mb-8">
        Immutable record of all AI inference decisions
      </p>
      {error ? (
        <p className="text-red-500 text-sm">{error}</p>
      ) : (
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <EventTable events={data?.events ?? []} />
        </div>
      )}
    </div>
  )
}
