import { useState } from 'react'
import {
  Button,
  Form,
  FormField,
  Modal,
  SpaceBetween,
  Textarea,
  Input,
} from '@cloudscape-design/components'

export default function NewChatModal({ isOpen, onClose, onCreateChat }) {
  const [title, setTitle] = useState('')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [loading, setLoading] = useState(false)

  const resetAndClose = () => {
    setTitle('')
    setSystemPrompt('')
    onClose()
  }

  const handleSubmit = async () => {
    if (!title.trim()) return

    setLoading(true)
    try {
      await onCreateChat({
        title: title.trim(),
        system_prompt: systemPrompt.trim() || null,
      })
      resetAndClose()
    } catch (error) {
      console.error('Failed to create chat:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      visible={isOpen}
      onDismiss={resetAndClose}
      header="Create new chat"
      closeAriaLabel="Close modal"
      footer={
        <SpaceBetween direction="horizontal" size="xs">
          <Button variant="link" onClick={resetAndClose} disabled={loading}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit} loading={loading} disabled={!title.trim()}>
            Create chat
          </Button>
        </SpaceBetween>
      }
    >
      <Form>
        <SpaceBetween size="l">
          <FormField label="Chat title" description="Use a clear title so chat history is easy to navigate.">
            <Input value={title} onChange={({ detail }) => setTitle(detail.value)} />
          </FormField>

          <FormField label="System prompt" description="Optional instructions that shape assistant behavior.">
            <Textarea value={systemPrompt} onChange={({ detail }) => setSystemPrompt(detail.value)} rows={6} />
          </FormField>
        </SpaceBetween>
      </Form>
    </Modal>
  )
}
