import type { InferenceEvent } from "@/lib/api"
import { StatusBadge } from "@/components/status-badge"

export function EventTable({ events }: { events: InferenceEvent[] }) {
  if (events.length === 0) {
    return (
      <p className="text-slate-500 text-sm py-8 text-center">
        No inference events recorded yet.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-slate-500 uppercase border-b border-slate-200">
          <tr>
            <th className="pb-3 pr-4">Timestamp</th>
            <th className="pb-3 pr-4">Model</th>
            <th className="pb-3 pr-4">Decision</th>
            <th className="pb-3 pr-4">Reason</th>
            <th className="pb-3">Messages</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {events.map((event) => (
            <tr key={event.event_id} className="hover:bg-slate-50">
              <td className="py-3 pr-4 text-slate-500 whitespace-nowrap">
                {new Date(event.timestamp).toLocaleString()}
              </td>
              <td className="py-3 pr-4 font-mono text-xs text-slate-700">
                {event.model}
              </td>
              <td className="py-3 pr-4">
                <StatusBadge decision={event.policy_decision} />
              </td>
              <td className="py-3 pr-4 text-slate-600">
                {event.policy_reason}
              </td>
              <td className="py-3 text-slate-500">
                {event.request_message_count}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
