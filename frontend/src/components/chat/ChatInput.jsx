import { useState } from 'react'
import { Send, Paperclip, Loader2 } from 'lucide-react'

export default function ChatInput({ onSendMessage, attachedKBs }) {
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!message.trim() || sending) return

    setSending(true)
    setMessage('')

    try {
      await onSendMessage(message.trim())
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      {/* Attached KBs Info */}
      {attachedKBs.length > 0 && (
        <div className="flex items-center gap-2 text-xs text-gray-600 px-2">
          <Paperclip size={14} />
          <span>Using {attachedKBs.length} knowledge base{attachedKBs.length > 1 ? 's' : ''}</span>
        </div>
      )}

      {/* Input Area */}
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Shift+Enter for new line)"
            rows={1}
            disabled={sending}
            className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
            style={{ minHeight: '48px', maxHeight: '200px' }}
          />
        </div>

        <button
          type="submit"
          disabled={!message.trim() || sending}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl transition flex items-center gap-2 font-medium"
        >
          {sending ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              Sending...
            </>
          ) : (
            <>
              <Send size={20} />
              Send
            </>
          )}
        </button>
      </div>
    </form>
  )
}
