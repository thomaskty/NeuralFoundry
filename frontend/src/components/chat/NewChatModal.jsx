import { useState } from 'react'
import { X, MessageSquare, Sparkles } from 'lucide-react'

export default function NewChatModal({ isOpen, onClose, onCreateChat, userId }) {
  const [title, setTitle] = useState('')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!title.trim()) {
      alert('Please enter a chat title')
      return
    }

    setLoading(true)

    try {
      await onCreateChat({
        title: title.trim(),
        system_prompt: systemPrompt.trim() || null
      })

      // Reset form
      setTitle('')
      setSystemPrompt('')
      onClose()
    } catch (error) {
      console.error('Failed to create chat:', error)
      alert('Failed to create chat. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur flex items-center justify-center z-50 p-4">
      <div className="bg-white/90 backdrop-blur rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col border border-slate-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 via-blue-600 to-sky-500 rounded-xl flex items-center justify-center shadow-sm">
              <MessageSquare className="text-white" size={20} />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Create New Chat</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-lg transition"
            disabled={loading}
          >
            <X size={24} className="text-slate-600" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Title Field */}
          <div>
            <label htmlFor="chat-title" className="block text-sm font-semibold text-slate-700 mb-2">
              Chat Title *
            </label>
            <input
              id="chat-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., FastAPI Development Help"
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition shadow-sm"
              disabled={loading}
              autoFocus
              maxLength={100}
            />
            <p className="text-xs text-slate-500 mt-1">
              Give your chat a descriptive name
            </p>
          </div>

          {/* System Prompt Field */}
          <div>
            <label htmlFor="system-prompt" className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
              <Sparkles size={16} className="text-indigo-500" />
              System Prompt (Optional)
            </label>
            <textarea
              id="system-prompt"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="You are a helpful assistant specialized in..."
              rows={6}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none resize-none transition shadow-sm"
              disabled={loading}
              maxLength={500}
            />
            <p className="text-xs text-slate-500 mt-1">
              Customize the AI's behavior and expertise for this chat
            </p>
          </div>

          {/* Examples */}
          <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4">
            <p className="text-sm font-semibold text-indigo-900 mb-2">
              💡 Example System Prompts:
            </p>
            <ul className="text-xs text-indigo-800 space-y-1">
              <li>• "You are an expert Python developer who provides concise, production-ready code."</li>
              <li>• "You are a technical interviewer asking challenging system design questions."</li>
              <li>• "You are a friendly tutor explaining complex topics in simple terms."</li>
              <li>• "You are a code reviewer focusing on best practices and performance."</li>
            </ul>
          </div>
        </form>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-slate-200 bg-slate-50/70">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 text-slate-700 hover:bg-slate-200 rounded-lg transition font-semibold"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || !title.trim()}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-lg transition font-semibold flex items-center gap-2 shadow-sm"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Creating...
              </>
            ) : (
              <>
                <MessageSquare size={18} />
                Create Chat
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
