const LEDGER_URL = process.env.LEDGER_SERVICE_URL ?? "http://localhost:8082"
const AIBOM_URL = process.env.AIBOM_SERVICE_URL ?? "http://localhost:8084"

export type PolicyDecision = "allowed" | "denied" | "bypassed"

export interface InferenceEvent {
  event_id: string
  timestamp: string
  model: string
  policy_decision: PolicyDecision
  policy_reason: string
  caller_ip: string | null
  request_message_count: number
  metadata: Record<string, unknown>
}

export interface EventListResponse {
  events: InferenceEvent[]
  total: number
  page_size: number
}

export interface BOMSummary {
  models: string[]
  total: number
}

export async function fetchEvents(limit = 50, offset = 0): Promise<EventListResponse> {
  const res = await fetch(`${LEDGER_URL}/v1/events?limit=${limit}&offset=${offset}`, {
    next: { revalidate: 10 },
  })
  if (!res.ok) throw new Error(`ledger responded ${res.status}`)
  return res.json()
}

export async function fetchBOMs(): Promise<BOMSummary> {
  const res = await fetch(`${AIBOM_URL}/v1/bom`, {
    next: { revalidate: 30 },
  })
  if (!res.ok) throw new Error(`aibom responded ${res.status}`)
  return res.json()
}
