import { fetchBOMs } from "@/lib/api"

export default async function ModelsPage() {
  let data = null
  let error = null

  try {
    data = await fetchBOMs()
  } catch {
    error = "AI-BOM service is unavailable."
  }

  return (
    <div className="max-w-3xl">
      <h1 className="text-xl font-semibold text-slate-900 mb-1">Model Registry</h1>
      <p className="text-slate-500 text-sm mb-8">
        CycloneDX ML-BOM inventory of registered AI model components
      </p>
      {error ? (
        <p className="text-red-500 text-sm">{error}</p>
      ) : (
        <div className="bg-white rounded-lg border border-slate-200 divide-y divide-slate-100">
          {data && data.models.length > 0 ? (
            data.models.map((modelId) => (
              <div key={modelId} className="px-4 py-3 flex items-center justify-between">
                <span className="font-mono text-sm text-slate-700">{modelId}</span>
                <span className="text-xs text-slate-400">CycloneDX 1.5</span>
              </div>
            ))
          ) : (
            <p className="px-4 py-6 text-slate-400 text-sm text-center">
              No models registered yet.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
