import { useRef, useState } from 'react'
import {
  Box,
  Button,
  Textarea,
} from '@cloudscape-design/components'

export default function ChatInput({ onSendMessage, attachedKBs, onAttachFile, isUploading }) {
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const fileInputRef = useRef(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!message.trim() || sending) return

    const current = message.trim()
    setSending(true)
    setMessage('')

    try {
      await onSendMessage(current)
    } finally {
      setSending(false)
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file && onAttachFile) {
      onAttachFile(file)
      e.target.value = ''
    }
  }

  return (
    <form onSubmit={handleSubmit} className="nf-chat-input-form">
      <div className="nf-chat-input-top">
        {attachedKBs.length > 0 && (
          <Box color="text-body-secondary" fontSize="body-s" className="nf-chat-context">
            Using {attachedKBs.length} knowledge base{attachedKBs.length === 1 ? '' : 's'}
          </Box>
        )}
        <Box color="text-body-secondary" fontSize="body-s">
          Shift+Enter for a new line
        </Box>
      </div>

      <div className="nf-chat-textarea-wrap">
        <Textarea
          value={message}
          onChange={({ detail }) => setMessage(detail.value)}
          placeholder="Type your message"
          rows={4}
          disabled={sending}
        />
      </div>

      <div className="nf-chat-input-actions">
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.txt,.docx,.doc,.png,.jpg,.jpeg,.html,.md"
          style={{ display: 'none' }}
        />
        <div className="nf-chat-input-left">
          <Button
            type="button"
            iconName="upload"
            onClick={() => fileInputRef.current?.click()}
            disabled={sending || isUploading}
            loading={isUploading}
          >
            Attach file
          </Button>
        </div>
        <div className="nf-chat-input-right">
          <Button variant="primary" formAction="submit" loading={sending} disabled={!message.trim()}>
            Send
          </Button>
        </div>
      </div>
    </form>
  )
}
