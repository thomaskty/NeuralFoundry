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
    { id: 'mistral-small-latest', name: 'Mistral Small' },
    { id: 'mistral-medium-latest', name: 'Mistral Medium' },
    { id: 'mistral-large-latest', name: 'Mistral Large' }
  ]

  const isKBAttached = (kbId) => {
    return attachedKBs.some(kb => kb.kb_id === kbId)
  }

  return (
    <div className="w-80 bg-gray-50 border-l border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          LLM Model
        </label>
        <div className="relative">
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            className="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg appearance-none cursor-pointer focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          >
            {models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={20} />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">
          Knowledge Bases
        </h3>

        {knowledgeBases.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            No knowledge bases yet
          </p>
        ) : (
          <div className="space-y-2">
            {knowledgeBases.map(kb => {
              const isAttached = isKBAttached(kb.kb_id)

              return (
                <div
                  key={kb.kb_id}
                  className={`block p-3 rounded-lg border-2 transition ${
                    isAttached
                      ? 'bg-blue-50 border-blue-300'
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={isAttached}
                      onChange={() => onToggleKB(kb.kb_id, isAttached)}
                      className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">
                        {kb.title}
                      </p>
                      {kb.description && (
                        <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                          {kb.description}
                        </p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        {kb.document_count || 0} {kb.document_count === 1 ? 'document' : 'documents'}
                      </p>
                    </div>
                    <button
                      onClick={() => onOpenKBFiles(kb)}
                      className="flex-shrink-0 p-1.5 hover:bg-blue-100 rounded-lg transition"
                      title="View files"
                    >
                      <FolderOpen size={16} className="text-blue-600" />
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