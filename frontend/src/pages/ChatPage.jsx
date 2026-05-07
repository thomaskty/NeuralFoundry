import { useEffect, useState } from 'react'
import {
  Badge,
  Box,
  Button,
  ButtonDropdown,
  Checkbox,
  Container,
  Header,
  Select,
  SpaceBetween,
  Spinner,
  StatusIndicator,
} from '@cloudscape-design/components'
import ChatInput from '../components/chat/ChatInput'
import MessageList from '../components/chat/MessageList'
import AttachmentPreview from '../components/chat/AttachmentPreview'
import NewChatModal from '../components/chat/NewChatModal'
import KBManagementModal from '../components/kb/KBManagementModal'
import FileExplorerModal from '../components/kb/FileExplorerModal'
import LogoMark from '../components/branding/LogoMark'
import { ToastContainer } from '../components/Toast'
import { attachmentAPI, chatAPI, kbAPI } from '../services/api'

const MODEL_OPTIONS = [{ label: 'OpenAI GPT-4o mini', value: 'gpt-4o-mini' }]

export default function ChatPage({ user, onLogout }) {
  const [chats, setChats] = useState([])
  const [currentChat, setCurrentChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [knowledgeBases, setKnowledgeBases] = useState([])
  const [attachedKBs, setAttachedKBs] = useState([])
  const [attachments, setAttachments] = useState([])
  const [selectedModel, setSelectedModel] = useState(MODEL_OPTIONS[0])
  const [loading, setLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)

  const [toasts, setToasts] = useState([])
  const [fileExplorerKB, setFileExplorerKB] = useState(null)
  const [showKBModal, setShowKBModal] = useState(false)
  const [showNewChatModal, setShowNewChatModal] = useState(false)

  useEffect(() => {
    loadUserData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user.id])

  useEffect(() => {
    if (!currentChat?.chat_id) return
    loadChatMessages(currentChat.chat_id)
    loadAttachedKBs(currentChat.chat_id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentChat?.chat_id])

  const showToast = (message, type = 'success', duration = 3500) => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type }])

    window.setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id))
    }, duration)
  }

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }

  const loadUserData = async () => {
    try {
      const [chatsData, kbData] = await Promise.all([
        chatAPI.getUserChats(user.id),
        kbAPI.getUserKBs(user.id),
      ])

      const fetchedChats = chatsData.chats || []
      setChats(fetchedChats)
      setKnowledgeBases(kbData || [])

      if (fetchedChats.length > 0) {
        setCurrentChat(fetchedChats[0])
      }
    } catch (error) {
      console.error('Failed to load user data:', error)
      showToast('Failed to load user data', 'error')
    } finally {
      setLoading(false)
    }
  }

  const loadChatMessages = async (chatId) => {
    try {
      const [chatData, attachmentData] = await Promise.all([
        chatAPI.getChat(chatId),
        attachmentAPI.listAttachments(chatId),
      ])

      setMessages(chatData.messages || [])
      setAttachments(attachmentData.attachments || [])
    } catch (error) {
      console.error('Failed to load messages:', error)
      showToast('Failed to load chat messages', 'error')
    }
  }

  const loadAttachedKBs = async (chatId) => {
    try {
      const data = await kbAPI.getAttachedKBs(chatId)
      setAttachedKBs(data.knowledge_bases || [])
    } catch (error) {
      console.error('Failed to load attached KBs:', error)
    }
  }

  const handleNewChat = async (chatData) => {
    try {
      const newChat = await chatAPI.createChat(user.id, chatData.title, chatData.system_prompt)
      setChats((prev) => [newChat, ...prev])
      setCurrentChat(newChat)
      setMessages([])
      setAttachments([])
      setAttachedKBs([])
      showToast('Chat created', 'success')
    } catch (error) {
      console.error('Failed to create chat:', error)
      showToast('Failed to create chat', 'error')
      throw error
    }
  }

  const handleDeleteChat = async (chatId) => {
    try {
      await chatAPI.deleteChat(chatId)
      const remainingChats = chats.filter((chat) => chat.chat_id !== chatId)
      setChats(remainingChats)

      if (currentChat?.chat_id === chatId) {
        setCurrentChat(remainingChats[0] || null)
        setMessages([])
        setAttachments([])
        setAttachedKBs([])
      }

      showToast('Chat deleted', 'success')
    } catch (error) {
      console.error('Failed to delete chat:', error)
      showToast('Failed to delete chat', 'error')
    }
  }

  const handleSendMessage = async (content) => {
    if (!currentChat?.chat_id) return

    const optimisticMessage = {
      id: Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, optimisticMessage])

    try {
      const response = await chatAPI.sendMessage(currentChat.chat_id, content)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: response.reply,
          metadata: response.metadata || {},
          created_at: new Date().toISOString(),
        },
      ])
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages((prev) => prev.filter((message) => message.id !== optimisticMessage.id))
      showToast('Failed to send message', 'error')
    }
  }

  const handleToggleKB = async (kbId, isAttached) => {
    if (!currentChat?.chat_id) return

    try {
      if (isAttached) {
        await kbAPI.detachKB(currentChat.chat_id, kbId)
        setAttachedKBs((prev) => prev.filter((kb) => kb.kb_id !== kbId))
      } else {
        await kbAPI.attachKB(currentChat.chat_id, kbId)
        const kb = knowledgeBases.find((item) => item.kb_id === kbId)
        if (kb) {
          setAttachedKBs((prev) => [...prev, kb])
        }
      }
    } catch (error) {
      console.error('Failed to toggle KB:', error)
      showToast('Failed to update knowledge base connection', 'error')
    }
  }

  const handleKBCreated = (newKB) => {
    setKnowledgeBases((prev) => [...prev, newKB])
  }

  const handleKBDeleted = (kbId) => {
    setKnowledgeBases((prev) => prev.filter((kb) => kb.kb_id !== kbId))
    setAttachedKBs((prev) => prev.filter((kb) => kb.kb_id !== kbId))
  }

  const handleAttachFile = async (file) => {
    if (!currentChat?.chat_id) return

    setIsUploading(true)
    try {
      await attachmentAPI.uploadAttachment(currentChat.chat_id, file)
      showToast(`Uploaded ${file.name}`, 'success')

      const updatedAttachments = await attachmentAPI.listAttachments(currentChat.chat_id)
      setAttachments(updatedAttachments.attachments || [])

      window.setTimeout(async () => {
        const refreshed = await attachmentAPI.listAttachments(currentChat.chat_id)
        setAttachments(refreshed.attachments || [])
      }, 3000)
    } catch (error) {
      console.error('Failed to upload attachment:', error)
      showToast('Failed to upload attachment', 'error')
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemoveAttachment = async (attachmentId) => {
    if (!currentChat?.chat_id) return

    try {
      await attachmentAPI.deleteAttachment(currentChat.chat_id, attachmentId)
      setAttachments((prev) => prev.filter((attachment) => attachment.id !== attachmentId))
      showToast('Attachment removed', 'success')
    } catch (error) {
      console.error('Failed to remove attachment:', error)
      showToast('Failed to remove attachment', 'error')
    }
  }

  const handlePlaceholderAction = (label) => {
    showToast(`${label} is a planned workspace feature`, 'info')
  }

  const renderSidebar = () => (
    <aside className="nf-sidebar">
      <div className="nf-sidebar-header">
        <Button variant="primary" fullWidth onClick={() => setShowNewChatModal(true)}>
          New chat
        </Button>
      </div>

      <div className="nf-chat-list">
        {chats.length === 0 ? (
          <div className="nf-empty-panel">No chats yet</div>
        ) : (
          chats.map((chat) => {
            const selected = currentChat?.chat_id === chat.chat_id
            return (
              <button
                key={chat.chat_id}
                type="button"
                className={`nf-chat-list-item ${selected ? 'is-active' : ''}`}
                onClick={() => setCurrentChat(chat)}
              >
                <div className="nf-chat-list-row">
                  <div className="nf-chat-list-title">{chat.title || 'Untitled chat'}</div>
                  <Button
                    iconName="remove"
                    variant="icon"
                    onClick={(event) => {
                      event.stopPropagation()
                      handleDeleteChat(chat.chat_id)
                    }}
                  />
                </div>
                <div className="nf-chat-list-meta">
                  <span>{new Date(chat.created_at).toLocaleDateString()}</span>
                  <span>{selected ? 'Open' : 'Recent'}</span>
                </div>
              </button>
            )
          })
        )}
      </div>
    </aside>
  )

  const renderTools = () => (
    <aside className="nf-tools">
      <Container header={<Header variant="h3">Model</Header>}>
        <Select
          selectedOption={selectedModel}
          options={MODEL_OPTIONS}
          onChange={({ detail }) => setSelectedModel(detail.selectedOption)}
        />
      </Container>

      <Container header={<Header variant="h3">Knowledge bases</Header>}>
        <SpaceBetween size="s">
          {knowledgeBases.length === 0 ? (
            <Box color="text-body-secondary">No knowledge bases available.</Box>
          ) : (
            knowledgeBases.map((kb) => {
              const isAttached = attachedKBs.some((attached) => attached.kb_id === kb.kb_id)
              return (
                <div key={kb.kb_id} className="nf-kb-card">
                  <div className="nf-kb-card-top">
                    <Checkbox checked={isAttached} onChange={() => handleToggleKB(kb.kb_id, isAttached)}>
                      {kb.title}
                    </Checkbox>
                    <Button variant="inline-link" onClick={() => setFileExplorerKB(kb)}>
                      Files
                    </Button>
                  </div>
                  {kb.description && (
                    <Box color="text-body-secondary" fontSize="body-s">
                      {kb.description}
                    </Box>
                  )}
                  <Box color="text-body-secondary" fontSize="body-s">
                    {kb.document_count || 0} documents
                  </Box>
                </div>
              )
            })
          )}
        </SpaceBetween>
      </Container>

      <Container header={<Header variant="h3">Workspace actions</Header>}>
        <div className="nf-action-grid">
          <button type="button" className="nf-action-card" onClick={() => handlePlaceholderAction('Saved prompts')}>
            <span className="nf-action-title">Saved prompts</span>
            <span className="nf-action-copy">Reuse approved prompt patterns across chats.</span>
          </button>
          <button type="button" className="nf-action-card" onClick={() => handlePlaceholderAction('Team sharing')}>
            <span className="nf-action-title">Team sharing</span>
            <span className="nf-action-copy">Share sessions, notes, and KB selections with collaborators.</span>
          </button>
          <button type="button" className="nf-action-card" onClick={() => handlePlaceholderAction('Evaluations')}>
            <span className="nf-action-title">Evaluations</span>
            <span className="nf-action-copy">Track answer quality and retrieval performance over time.</span>
          </button>
          <button type="button" className="nf-action-card" onClick={() => handlePlaceholderAction('Exports')}>
            <span className="nf-action-title">Exports</span>
            <span className="nf-action-copy">Export chats, citations, and decisions into handoff docs.</span>
          </button>
        </div>
      </Container>
    </aside>
  )

  const renderMain = () => {
    if (loading) {
      return (
        <div className="nf-main-loading">
          <Spinner size="large" />
        </div>
      )
    }

    if (!currentChat) {
      return (
        <div className="nf-main-empty">
          <div className="nf-hero-card">
            <div className="nf-hero-eyebrow">Neural Foundry</div>
            <h2>Professional workspace for RAG conversations</h2>
            <p>Create a new chat, attach knowledge bases, and test retrieval end-to-end.</p>
            <Button variant="primary" onClick={() => setShowNewChatModal(true)}>
              Create chat
            </Button>
          </div>
        </div>
      )
    }

    return (
      <div className="nf-main-chat">
        <div className="nf-chat-stage">
          <div className="nf-chat-stage-header">
            <div>
              <h2>{currentChat.title || 'Untitled chat'}</h2>
              <div className="nf-chat-stage-status">
                <StatusIndicator type="success">Connected</StatusIndicator>
                <Badge>{attachedKBs.length} KB attached</Badge>
              </div>
            </div>
            <div className="nf-chat-stage-actions">
              <Button onClick={() => handlePlaceholderAction('Branch chat')}>Branch</Button>
              <Button onClick={() => handlePlaceholderAction('Summary view')}>Summarize</Button>
              <Button onClick={() => handlePlaceholderAction('Source map')}>Sources</Button>
              <Button iconName="remove" variant="icon" onClick={() => handleDeleteChat(currentChat.chat_id)} />
            </div>
          </div>

          <div className="nf-chat-scroll">
            <MessageList messages={messages} />
          </div>
        </div>

        <div className="nf-composer-shell">
          <AttachmentPreview
            attachments={attachments}
            onRemove={handleRemoveAttachment}
            isUploading={isUploading}
          />
          <ChatInput
            onSendMessage={handleSendMessage}
            attachedKBs={attachedKBs}
            onAttachFile={handleAttachFile}
            isUploading={isUploading}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="nf-shell">
      <header className="nf-topbar">
        <div className="nf-brand">
          <LogoMark size={44} withWordmark subtitle="RAG Studio" />
        </div>
        <div className="nf-topbar-actions">
          <Button onClick={() => setShowKBModal(true)}>Knowledge bases</Button>
          <Button onClick={() => handlePlaceholderAction('Workspace search')}>Search</Button>
          <Button onClick={() => handlePlaceholderAction('Agent workflows')}>Agents</Button>
          <Button onClick={() => handlePlaceholderAction('Insights dashboard')}>Insights</Button>
          <Button onClick={() => handlePlaceholderAction('Workflow templates')}>Templates</Button>
          <ButtonDropdown
            items={[{ id: 'logout', text: 'Logout' }]}
            onItemClick={({ detail }) => {
              if (detail.id === 'logout') onLogout()
            }}
          >
            {user.username}
          </ButtonDropdown>
        </div>
      </header>

      <div className="nf-shell-body">
        {renderSidebar()}
        <main className="nf-main">{renderMain()}</main>
        {renderTools()}
      </div>

      <div className="nf-notifications">
        <ToastContainer toasts={toasts} removeToast={removeToast} />
      </div>

      <NewChatModal
        isOpen={showNewChatModal}
        onClose={() => setShowNewChatModal(false)}
        onCreateChat={handleNewChat}
      />

      {showKBModal && (
        <KBManagementModal
          knowledgeBases={knowledgeBases}
          onClose={() => setShowKBModal(false)}
          onKBCreated={handleKBCreated}
          onKBDeleted={handleKBDeleted}
          userId={user.id}
          onShowToast={showToast}
          kbAPI={kbAPI}
        />
      )}

      {fileExplorerKB && (
        <FileExplorerModal
          kb={fileExplorerKB}
          onClose={() => setFileExplorerKB(null)}
          onShowToast={showToast}
        />
      )}
    </div>
  )
}
