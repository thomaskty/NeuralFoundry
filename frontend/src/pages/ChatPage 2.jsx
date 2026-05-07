import { useEffect, useMemo, useState } from 'react'
import {
  AppLayout,
  Badge,
  Box,
  Button,
  ButtonDropdown,
  Cards,
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
import { ToastContainer } from '../components/Toast'
import { attachmentAPI, chatAPI, kbAPI } from '../services/api'

export default function ChatPage({ user, onLogout }) {
  const [chats, setChats] = useState([])
  const [currentChat, setCurrentChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [knowledgeBases, setKnowledgeBases] = useState([])
  const [attachedKBs, setAttachedKBs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedModel, setSelectedModel] = useState({ label: 'OpenAI GPT-4o mini', value: 'gpt-4o-mini' })
  const [attachments, setAttachments] = useState([])
  const [isUploading, setIsUploading] = useState(false)

  const [toasts, setToasts] = useState([])
  const [fileExplorerKB, setFileExplorerKB] = useState(null)
  const [showKbModal, setShowKbModal] = useState(false)
  const [showNewChatModal, setShowNewChatModal] = useState(false)

  const [navigationOpen, setNavigationOpen] = useState(true)
  const [toolsOpen, setToolsOpen] = useState(true)

  const showToast = (message, type = 'success', duration = 3500) => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type, duration }])
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, duration)
  }

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  useEffect(() => {
    loadUserData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user.id])

  useEffect(() => {
    if (!currentChat) return
    loadChatMessages(currentChat.chat_id)
    loadAttachedKBs(currentChat.chat_id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentChat?.chat_id])

  const loadUserData = async () => {
    try {
      const [chatsData, kbsData] = await Promise.all([chatAPI.getUserChats(user.id), kbAPI.getUserKBs(user.id)])
      const fetchedChats = chatsData.chats || []

      setChats(fetchedChats)
      setKnowledgeBases(kbsData || [])

      if (fetchedChats.length > 0) {
        setCurrentChat(fetchedChats[0])
      }
    } catch (error) {
      console.error('Failed to load user data:', error)
      showToast('Failed to load data', 'error')
    } finally {
      setLoading(false)
    }
  }

  const loadChatMessages = async (chatId) => {
    try {
      const [chatData, attachmentsData] = await Promise.all([
        chatAPI.getChat(chatId),
        attachmentAPI.listAttachments(chatId),
      ])
      setMessages(chatData.messages || [])
      setAttachments(attachmentsData.attachments || [])
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
      setAttachedKBs([])
      showToast('New chat created', 'success')
    } catch (error) {
      console.error('Failed to create chat:', error)
      showToast('Failed to create chat', 'error')
      throw error
    }
  }

  const handleDeleteChat = async (chatId) => {
    try {
      await chatAPI.deleteChat(chatId)
      const updated = chats.filter((chat) => chat.chat_id !== chatId)
      setChats(updated)
      if (currentChat?.chat_id === chatId) {
        setCurrentChat(updated[0] || null)
      }
      showToast('Chat deleted', 'success')
    } catch (error) {
      console.error('Failed to delete chat:', error)
      showToast('Failed to delete chat', 'error')
    }
  }

  const handleSendMessage = async (content) => {
    if (!currentChat) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await chatAPI.sendMessage(currentChat.chat_id, content)
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.reply,
        metadata: response.metadata || {},
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id))
      showToast('Failed to send message', 'error')
    }
  }

  const handleToggleKB = async (kbId, isAttached) => {
    if (!currentChat) return

    try {
      if (isAttached) {
        await kbAPI.detachKB(currentChat.chat_id, kbId)
        setAttachedKBs((prev) => prev.filter((kb) => kb.kb_id !== kbId))
      } else {
        await kbAPI.attachKB(currentChat.chat_id, kbId)
        const kb = knowledgeBases.find((k) => k.kb_id === kbId)
        if (kb) setAttachedKBs((prev) => [...prev, kb])
      }
    } catch (error) {
      console.error('Failed to toggle KB:', error)
      showToast('Failed to update knowledge base link', 'error')
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
    if (!currentChat) return

    setIsUploading(true)
    try {
      await attachmentAPI.uploadAttachment(currentChat.chat_id, file)
      showToast(`File "${file.name}" uploaded`, 'success')

      const attachmentsData = await attachmentAPI.listAttachments(currentChat.chat_id)
      setAttachments(attachmentsData.attachments || [])

      window.setTimeout(async () => {
        const updated = await attachmentAPI.listAttachments(currentChat.chat_id)
        setAttachments(updated.attachments || [])
      }, 3000)
    } catch (error) {
      console.error('Failed to upload attachment:', error)
      showToast('Failed to upload file', 'error')
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemoveAttachment = async (attachmentId) => {
    if (!currentChat) return

    try {
      await attachmentAPI.deleteAttachment(currentChat.chat_id, attachmentId)
      setAttachments((prev) => prev.filter((a) => a.id !== attachmentId))
      showToast('Attachment removed', 'success')
    } catch (error) {
      console.error('Failed to remove attachment:', error)
      showToast('Failed to remove attachment', 'error')
    }
  }

  const toolsKbItems = useMemo(
    () =>
      knowledgeBases.map((kb) => {
        const isAttached = attachedKBs.some((akb) => akb.kb_id === kb.kb_id)
        return (
          <Container key={kb.kb_id}>
            <SpaceBetween size="xs">
              <Checkbox checked={isAttached} onChange={() => handleToggleKB(kb.kb_id, isAttached)}>
                {kb.title}
              </Checkbox>
              <Box color="text-body-secondary" fontSize="body-s">
                {kb.document_count || 0} documents
              </Box>
              <Button variant="inline-link" onClick={() => setFileExplorerKB(kb)}>
                View files
              </Button>
            </SpaceBetween>
          </Container>
        )
      }),
    [knowledgeBases, attachedKBs],
  )

  const navigation = (
    <SpaceBetween size="m">
      <Button variant="primary" fullWidth onClick={() => setShowNewChatModal(true)}>
        New chat
      </Button>

      <Cards
        cardsPerRow={[{ cards: 1 }]}
        items={chats}
        trackBy="chat_id"
        selectionType="single"
        selectedItems={currentChat ? [currentChat] : []}
        onSelectionChange={({ detail }) => setCurrentChat(detail.selectedItems[0] || null)}
        cardDefinition={{
          header: (item) => item.title || 'Untitled chat',
          sections: [
            {
              id: 'created',
              content: (item) => new Date(item.created_at).toLocaleDateString(),
            },
          ],
        }}
        empty={<Box color="text-body-secondary">No chats yet.</Box>}
      />

      <Button variant="normal" fullWidth onClick={() => setShowKbModal(true)}>
        Manage knowledge bases
      </Button>
    </SpaceBetween>
  )

  const tools = (
    <SpaceBetween size="m">
      <Container header={<Header variant="h3">Model</Header>}>
        <Select
          selectedOption={selectedModel}
          onChange={({ detail }) => setSelectedModel(detail.selectedOption)}
          options={[{ label: 'OpenAI GPT-4o mini', value: 'gpt-4o-mini' }]}
        />
      </Container>

      <Container header={<Header variant="h3">Knowledge bases</Header>}>
        <SpaceBetween size="xs">
          {toolsKbItems.length === 0 ? (
            <Box color="text-body-secondary">No knowledge bases available.</Box>
          ) : (
            toolsKbItems
          )}
        </SpaceBetween>
      </Container>
    </SpaceBetween>
  )

  const content = loading ? (
    <Box textAlign="center" padding="xxl">
      <Spinner size="large" />
    </Box>
  ) : !currentChat ? (
    <Container>
      <Box textAlign="center" padding="xxl">
        <SpaceBetween size="m">
          <Header variant="h2">Welcome to Neural Foundry</Header>
          <Box color="text-body-secondary">Create a new chat from the left panel to get started.</Box>
          <Button variant="primary" onClick={() => setShowNewChatModal(true)}>
            Create chat
          </Button>
        </SpaceBetween>
      </Box>
    </Container>
  ) : (
    <SpaceBetween size="m">
      <Container
        header={
          <Header
            variant="h2"
            description={
              <SpaceBetween direction="horizontal" size="xs">
                <StatusIndicator type="success">Ready</StatusIndicator>
                <Badge>{attachedKBs.length} KB attached</Badge>
              </SpaceBetween>
            }
            actions={
              <Button iconName="remove" variant="icon" onClick={() => handleDeleteChat(currentChat.chat_id)} />
            }
          >
            {currentChat.title || 'Chat'}
          </Header>
        }
      >
        <MessageList messages={messages} />
      </Container>

      <Container>
        <AttachmentPreview attachments={attachments} onRemove={handleRemoveAttachment} isUploading={isUploading} />
        <ChatInput
          onSendMessage={handleSendMessage}
          attachedKBs={attachedKBs}
          onAttachFile={handleAttachFile}
          isUploading={isUploading}
        />
      </Container>
    </SpaceBetween>
  )

  return (
    <>
      <AppLayout
        contentType="default"
        navigation={navigation}
        navigationOpen={navigationOpen}
        onNavigationChange={({ detail }) => setNavigationOpen(detail.open)}
        tools={tools}
        toolsOpen={toolsOpen}
        onToolsChange={({ detail }) => setToolsOpen(detail.open)}
        content={content}
        notifications={<ToastContainer toasts={toasts} removeToast={removeToast} />}
        headerSelector="#h"
        ariaLabels={{
          navigation: 'Chats panel',
          navigationToggle: 'Open chats panel',
          navigationClose: 'Close chats panel',
          tools: 'Knowledge base panel',
          toolsToggle: 'Open tools panel',
          toolsClose: 'Close tools panel',
        }}
      />

      <div id="h" className="nf-topbar">
        <Header
          variant="h1"
          description={`Signed in as ${user.username}`}
          actions={
            <ButtonDropdown
              items={[{ id: 'logout', text: 'Logout' }]}
              onItemClick={({ detail }) => {
                if (detail.id === 'logout') onLogout()
              }}
            >
              {user.username}
            </ButtonDropdown>
          }
        >
          Neural Foundry
        </Header>
      </div>

      <NewChatModal isOpen={showNewChatModal} onClose={() => setShowNewChatModal(false)} onCreateChat={handleNewChat} />

      {showKbModal && (
        <KBManagementModal
          knowledgeBases={knowledgeBases}
          onClose={() => setShowKbModal(false)}
          onKBCreated={handleKBCreated}
          onKBDeleted={handleKBDeleted}
          userId={user.id}
          onShowToast={showToast}
          kbAPI={kbAPI}
        />
      )}

      {fileExplorerKB && (
        <FileExplorerModal kb={fileExplorerKB} onClose={() => setFileExplorerKB(null)} onShowToast={showToast} />
      )}
    </>
  )
}
