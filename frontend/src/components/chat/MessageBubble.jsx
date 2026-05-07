import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import {
  Badge,
  Box,
  Button,
  Container,
  SpaceBetween,
} from '@cloudscape-design/components'

export default function MessageBubble({ message }) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className={`nf-message-row ${isUser ? 'is-user' : 'is-assistant'}`}>
      <Container>
        <SpaceBetween size="s">
          <div className="nf-message-meta">
            <Badge color={isUser ? 'blue' : 'green'}>{isUser ? 'User' : 'Assistant'}</Badge>
            <Box color="text-body-secondary" fontSize="body-s">
              {new Date(message.created_at).toLocaleTimeString()}
            </Box>
            {!isUser && (
              <Button iconName={copied ? 'status-positive' : 'copy'} variant="icon" onClick={handleCopy} />
            )}
          </div>

          <Box>
            <ReactMarkdown
              components={{
                code({ inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '')
                  return !inline && match ? (
                    <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div" {...props}>
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  )
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          </Box>
        </SpaceBetween>
      </Container>
    </div>
  )
}
