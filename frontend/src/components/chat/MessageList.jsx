import { Box, SpaceBetween } from '@cloudscape-design/components'
import MessageBubble from './MessageBubble'

export default function MessageList({ messages }) {
  if (messages.length === 0) {
    return (
      <Box color="text-body-secondary" textAlign="center" padding={{ vertical: 'xxl' }}>
        Start a conversation to test your workflow.
      </Box>
    )
  }

  return (
    <SpaceBetween size="l">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </SpaceBetween>
  )
}
