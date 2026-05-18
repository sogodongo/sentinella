import type { PolicyDecision } from "@/lib/api"

const styles: Record<PolicyDecision, string> = {
  allowed: "bg-emerald-100 text-emerald-800 border border-emerald-200",
  denied: "bg-red-100 text-red-800 border border-red-200",
  bypassed: "bg-amber-100 text-amber-800 border border-amber-200",
}

export function StatusBadge({ decision }: { decision: PolicyDecision }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${styles[decision]}`}>
      {decision}
    </span>
  )
}
