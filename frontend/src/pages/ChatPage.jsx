import { useState, useEffect } from 'react'
import Header from '../components/layout/Header'
import Sidebar from '../components/layout/Sidebar'
import MainChatArea from '../components/layout/MainChatArea'
import RightPanel from '../components/layout/RightPanel'
import { ToastContainer } from '../components/Toast'
import FileExplorerModal from '../components/kb/FileExplorerModal'
import { chatAPI, kbAPI, attachmentAPI } from '../services/api'

export default function ChatPage({ user, onLogout }) {
  const [chats, setChats] = useState([])
  const [currentChat, setCurrentChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [knowledgeBases, setKnowledgeBases] = useState([])
  const [attachedKBs, setAttachedKBs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedModel, setSelectedModel] = useState('gpt-4o-mini')
  const [attachments, setAttachments] = useState([])
  const [isUploading, setIsUploading] = useState(false)

  // Toast states
  const [toasts, setToasts] = useState([])
  const [fileExplorerKB, setFileExplorerKB] = useState(null)

  // Toast functions
  const showToast = (message, type = 'success', duration = 3000) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type, duration }])
  }

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  // Handler for opening file explorer
  const handleOpenKBFiles = (kb) => {
    setFileExplorerKB(kb)
  }

  // Load user's chats and KBs
  useEffect(() => {
    loadUserData()
  }, [user])

  // Load messages when chat changes
  useEffect(() => {
    if (currentChat) {
      loadChatMessages(currentChat.chat_id)
      loadAttachedKBs(currentChat.chat_id)
    }
  }, [currentChat])

  const loadUserData = async () => {
    try {
      const [chatsData, kbsData] = await Promise.all([
        chatAPI.getUserChats(user.id),
        kbAPI.getUserKBs(user.id)
      ])

      setChats(chatsData.chats || [])
      setKnowledgeBases(kbsData || [])

      // Select first chat if available
      if (chatsData.chats && chatsData.chats.length > 0) {
        setCurrentChat(chatsData.chats[0])
      }
    } catch (error) {
      console.error('Failed to load user data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadChatMessages = async (chatId) => {
    try {
      const [chatData, attachmentsData] = await Promise.all([
        chatAPI.getChat(chatId),
        attachmentAPI.listAttachments(chatId)
      ])
      setMessages(chatData.messages || [])
      setAttachments(attachmentsData.attachments || [])
    } catch (error) {
      console.error('Failed to load messages:', error)
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

  const handleNewChat = async (title, systemPrompt) => {
    try {
      const newChat = await chatAPI.createChat(user.id, title, systemPrompt)
      setChats([newChat, ...chats])
      setCurrentChat(newChat)
      setMessages([])
      setAttachedKBs([])
    } catch (error) {
      console.error('Failed to create chat:', error)
      throw error
    }
  }

  const handleSelectChat = (chat) => {
    setCurrentChat(chat)
    setAttachments([]) // ADD THIS LINE
  }

  const handleDeleteChat = async (chatId) => {
    try {
      await chatAPI.deleteChat(chatId)
      setChats(chats.filter(c => c.chat_id !== chatId))
      if (currentChat?.chat_id === chatId) {
        setCurrentChat(chats[0] || null)
      }
    } catch (error) {
      console.error('Failed to delete chat:', error)
    }
  }

  const handleSendMessage = async (content) => {
    if (!currentChat) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString()
    }
    setMessages([...messages, userMessage])

    try {
      const response = await chatAPI.sendMessage(currentChat.chat_id, content)

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.reply,
        metadata: response.metadata || {},
        created_at: new Date().toISOString()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages(prev => prev.filter(m => m.id !== userMessage.id))
    }
  }

  const handleToggleKB = async (kbId, isAttached) => {
    if (!currentChat) return

    try {
      if (isAttached) {
        await kbAPI.detachKB(currentChat.chat_id, kbId)
        setAttachedKBs(attachedKBs.filter(kb => kb.kb_id !== kbId))
      } else {
        await kbAPI.attachKB(currentChat.chat_id, kbId)
        const kb = knowledgeBases.find(k => k.kb_id === kbId)
        if (kb) {
          setAttachedKBs([...attachedKBs, kb])
        }
      }
    } catch (error) {
      console.error('Failed to toggle KB:', error)
    }
  }

  const handleKBCreated = (newKB) => {
    setKnowledgeBases([...knowledgeBases, newKB])
  }

  const handleKBDeleted = (kbId) => {
    setKnowledgeBases(knowledgeBases.filter(kb => kb.kb_id !== kbId))
    setAttachedKBs(attachedKBs.filter(kb => kb.kb_id !== kbId))
  }

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  const handleAttachFile = async (file) => {
    if (!currentChat) return

    setIsUploading(true)
    try {
      await attachmentAPI.uploadAttachment(currentChat.chat_id, file)
      showToast(`File "${file.name}" uploaded successfully`, 'success')

      // Reload attachments
      const attachmentsData = await attachmentAPI.listAttachments(currentChat.chat_id)
      setAttachments(attachmentsData.attachments || [])

      // Poll for processing completion
      setTimeout(async () => {
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

    if (!confirm('Remove this attachment?')) return

    try {
      await attachmentAPI.deleteAttachment(currentChat.chat_id, attachmentId)
      setAttachments(attachments.filter(a => a.id !== attachmentId))
      showToast('Attachment removed', 'success')
    } catch (error) {
      console.error('Failed to remove attachment:', error)
      showToast('Failed to remove attachment', 'error')
    }
  }

  return (
    <div className="h-screen flex flex-col bg-slate-50/60">
      <Header user={user} onLogout={onLogout} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          chats={chats}
          currentChat={currentChat}
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
          knowledgeBases={knowledgeBases}
          onKBCreated={handleKBCreated}
          onKBDeleted={handleKBDeleted}
          userId={user.id}
          onShowToast={showToast}
          kbAPI={kbAPI}
        />

        <MainChatArea
          currentChat={currentChat}
          messages={messages}
          onSendMessage={handleSendMessage}
          attachedKBs={attachedKBs}
          attachments={attachments}
          onAttachFile={handleAttachFile}
          onRemoveAttachment={handleRemoveAttachment}
          isUploading={isUploading}
        />

        <RightPanel
          knowledgeBases={knowledgeBases}
          attachedKBs={attachedKBs}
          onToggleKB={handleToggleKB}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
          onOpenKBFiles={handleOpenKBFiles}
        />
      </div>

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} removeToast={removeToast} />

      {/* File Explorer Modal */}
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
