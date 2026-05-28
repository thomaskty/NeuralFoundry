import { useEffect, useRef, useState } from 'react'
import {
  Box,
  Button,
} from '@cloudscape-design/components'

function formatAttachmentSummary(attachments) {
  return attachments.map((attachment) => attachment.filename).filter(Boolean)
}

export default function ChatInput({
  onSendMessage,
  attachedKBs,
  attachments = [],
  onAttachFile,
  isUploading,
}) {
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [showAllAttachments, setShowAllAttachments] = useState(false)
  const fileInputRef = useRef(null)
  const textareaRef = useRef(null)
  const attachmentNames = formatAttachmentSummary(attachments)
  const hiddenAttachmentCount = Math.max(attachmentNames.length - 4, 0)
  const visibleAttachmentNames = showAllAttachments ? attachmentNames : attachmentNames.slice(0, 4)

  const resizeTextarea = () => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = '0px'
    const nextHeight = Math.min(Math.max(textarea.scrollHeight, 44), 168)
    textarea.style.height = `${nextHeight}px`
    textarea.style.overflowY = textarea.scrollHeight > 168 ? 'auto' : 'hidden'
  }

  useEffect(() => {
    resizeTextarea()
  }, [message])

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

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (message.trim() && !sending) {
        handleSubmit(e)
      }
    }
  }

  return (
    <form onSubmit={handleSubmit} className="nf-chat-input-form">
      <div className="nf-chat-textarea-wrap">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message"
          rows={1}
          disabled={sending}
          className="nf-chat-textarea"
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
          {(attachedKBs.length > 0 || attachments.length > 0) && (
            <div className={`nf-chat-inline-context ${showAllAttachments ? 'is-expanded' : ''}`}>
              {attachedKBs.length > 0 && (
                <Box color="text-body-secondary" fontSize="body-s" className="nf-chat-context">
                  Using {attachedKBs.length} KB{attachedKBs.length === 1 ? '' : 's'}
                </Box>
              )}
              {attachmentNames.length > 0 && (
                <>
                  <Box color="text-body-secondary" fontSize="body-s" className="nf-chat-context nf-chat-context-files">
                    Attached {visibleAttachmentNames.join(', ')}
                  </Box>
                  {hiddenAttachmentCount > 0 && !showAllAttachments && (
                    <Button
                      type="button"
                      variant="inline-link"
                      onClick={() => setShowAllAttachments(true)}
                    >
                      +{hiddenAttachmentCount} files
                    </Button>
                  )}
                  {showAllAttachments && attachmentNames.length > 4 && (
                    <Button
                      type="button"
                      variant="inline-link"
                      onClick={() => setShowAllAttachments(false)}
                    >
                      Less
                    </Button>
                  )}
                </>
              )}
            </div>
          )}
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
