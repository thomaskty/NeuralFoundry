import { ChevronDown, FolderOpen } from 'lucide-react'

export default function RightPanel({
  knowledgeBases,
  attachedKBs,
  onToggleKB,
  selectedModel,
  onModelChange,
  onOpenKBFiles
}) {
  const models = [
    { id: 'gpt-4o-mini', name: 'OpenAI GPT-4o mini' }
  ]

  const isKBAttached = (kbId) => {
    return attachedKBs.some(kb => kb.kb_id === kbId)
  }

  return (
    <div className="w-80 bg-white/70 backdrop-blur border-l border-slate-200 flex flex-col shadow-sm">
      <div className="p-4 border-b border-slate-200">
        <label className="block text-sm font-semibold text-slate-700 mb-2">
          LLM Model
        </label>
        <div className="relative">
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl appearance-none cursor-pointer focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none shadow-sm"
          >
            {models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={20} />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="text-sm font-semibold text-slate-700 mb-3">
          Knowledge Bases
        </h3>

        {knowledgeBases.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-4">
            No knowledge bases yet
          </p>
        ) : (
          <div className="space-y-2">
            {knowledgeBases.map(kb => {
              const isAttached = isKBAttached(kb.kb_id)

              return (
                <div
                  key={kb.kb_id}
                  className={`block p-3 rounded-xl border transition shadow-sm ${
                    isAttached
                      ? 'bg-indigo-50 border-indigo-200'
                      : 'bg-white border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={isAttached}
                      onChange={() => onToggleKB(kb.kb_id, isAttached)}
                      className="mt-1 w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500 cursor-pointer"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-slate-800 truncate">
                        {kb.title}
                      </p>
                      {kb.description && (
                        <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                          {kb.description}
                        </p>
                      )}
                      <p className="text-xs text-slate-400 mt-1">
                        {kb.document_count || 0} {kb.document_count === 1 ? 'document' : 'documents'}
                      </p>
                    </div>
                    <button
                      onClick={() => onOpenKBFiles(kb)}
                      className="flex-shrink-0 p-1.5 hover:bg-indigo-100 rounded-lg transition"
                      title="View files"
                    >
                      <FolderOpen size={16} className="text-indigo-600" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
