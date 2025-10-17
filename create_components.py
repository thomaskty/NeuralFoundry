#!/usr/bin/env python3
"""
React Components Generator
Creates all React components for Neural Foundry frontend
Run from project root: python create_components.py
"""
import os


def create_file(path, content):
    """Create file with content"""
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Created: {path}")


def create_components():
    """Generate all React components"""

    print("🚀 Creating React components...\n")

    original_dir = os.getcwd()

    os.chdir("frontend/src")

    # ============================================================================
    # App.jsx - Main Application
    # ============================================================================
    app_jsx = """import { useState, useEffect } from 'react'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'

function App() {
  const [user, setUser] = useState(null)

  // Check if user is logged in
  useEffect(() => {
    const savedUser = localStorage.getItem('neural_user')
    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('neural_user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('neural_user')
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />
  }

  return <ChatPage user={user} onLogout={handleLogout} />
}

export default App
"""
    create_file("App.jsx", app_jsx)

    # ============================================================================
    # services/api.js - API Service Layer
    # ============================================================================
    api_js = """import axios from 'axios'

const API_BASE = '/api/v1'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ============================================================================
// User APIs
// ============================================================================
export const userAPI = {
  getByUsername: async (username) => {
    const response = await api.get(`/users?username=${username}`)
    return response.data
  },

  create: async (username) => {
    const response = await api.post('/users', { username })
    return response.data
  }
}

// ============================================================================
// Chat APIs
// ============================================================================
export const chatAPI = {
  getUserChats: async (userId) => {
    const response = await api.get(`/users/${userId}/chats`)
    return response.data
  },

  createChat: async (userId, title) => {
    const response = await api.post(`/users/${userId}/chats`, {
      title: title || 'New Chat',
      system_prompt: null
    })
    return response.data
  },

  getChat: async (chatId) => {
    const response = await api.get(`/chats/${chatId}`)
    return response.data
  },

  deleteChat: async (chatId) => {
    const response = await api.delete(`/chats/${chatId}`)
    return response.data
  },

  sendMessage: async (chatId, content) => {
    const response = await api.post(`/chats/${chatId}/messages`, {
      role: 'user',
      content
    })
    return response.data
  }
}

// ============================================================================
// Knowledge Base APIs
// ============================================================================
export const kbAPI = {
  getUserKBs: async (userId) => {
    const response = await api.get(`/users/${userId}/knowledge-bases`)
    return response.data
  },

  createKB: async (userId, title, description) => {
    const response = await api.post(`/users/${userId}/knowledge-bases`, {
      title,
      description
    })
    return response.data
  },

  uploadDocument: async (kbId, file) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(
      `/knowledge-bases/${kbId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data
  },

  deleteKB: async (kbId) => {
    const response = await api.delete(`/knowledge-bases/${kbId}`)
    return response.data
  },

  // Chat-KB Integration
  getAttachedKBs: async (chatId) => {
    const response = await api.get(`/chats/${chatId}/knowledge-bases`)
    return response.data
  },

  attachKB: async (chatId, kbId) => {
    const response = await api.post(`/chats/${chatId}/knowledge-bases/${kbId}`)
    return response.data
  },

  detachKB: async (chatId, kbId) => {
    const response = await api.delete(`/chats/${chatId}/knowledge-bases/${kbId}`)
    return response.data
  }
}

export default api
"""
    create_file("services/api.js", api_js)

    # ============================================================================
    # pages/LoginPage.jsx
    # ============================================================================
    login_page = """import { useState } from 'react'
import { userAPI } from '../services/api'
import { Loader2 } from 'lucide-react'

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!username.trim()) {
      setError('Please enter a username')
      return
    }

    setLoading(true)

    try {
      // Try to find existing user or create new one
      const userData = await userAPI.create(username.trim())
      onLogin(userData)
    } catch (err) {
      if (err.response?.status === 400) {
        setError('Username already exists. Please use a different username.')
      } else {
        setError('Failed to login. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800">
            neural<span className="text-blue-600">::</span>foundry
          </h1>
          <p className="text-gray-600 mt-2">AI-Powered Knowledge Assistant</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              disabled={loading}
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Logging in...
              </>
            ) : (
              'Continue'
            )}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          By continuing, you agree to our Terms of Service
        </p>
      </div>
    </div>
  )
}
"""
    create_file("pages/LoginPage.jsx", login_page)

    # ============================================================================
    # pages/ChatPage.jsx
    # ============================================================================
    chat_page = """import { useState, useEffect } from 'react'
import Header from '../components/layout/Header'
import Sidebar from '../components/layout/Sidebar'
import MainChatArea from '../components/layout/MainChatArea'
import RightPanel from '../components/layout/RightPanel'
import { chatAPI, kbAPI } from '../services/api'

export default function ChatPage({ user, onLogout }) {
  const [chats, setChats] = useState([])
  const [currentChat, setCurrentChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [knowledgeBases, setKnowledgeBases] = useState([])
  const [attachedKBs, setAttachedKBs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedModel, setSelectedModel] = useState('mistral-small-latest')

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
      const chatData = await chatAPI.getChat(chatId)
      setMessages(chatData.messages || [])
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

  const handleNewChat = async () => {
    try {
      const newChat = await chatAPI.createChat(user.id, 'New Chat')
      setChats([newChat, ...chats])
      setCurrentChat(newChat)
      setMessages([])
      setAttachedKBs([])
    } catch (error) {
      console.error('Failed to create chat:', error)
    }
  }

  const handleSelectChat = (chat) => {
    setCurrentChat(chat)
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

    // Optimistic update
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString()
    }
    setMessages([...messages, userMessage])

    try {
      const response = await chatAPI.sendMessage(currentChat.chat_id, content)

      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.reply,
        created_at: new Date().toISOString()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      // Remove optimistic message on error
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

  return (
    <div className="h-screen flex flex-col">
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
        />

        <MainChatArea
          currentChat={currentChat}
          messages={messages}
          onSendMessage={handleSendMessage}
          attachedKBs={attachedKBs}
        />

        <RightPanel
          knowledgeBases={knowledgeBases}
          attachedKBs={attachedKBs}
          onToggleKB={handleToggleKB}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />
      </div>
    </div>
  )
}
"""
    create_file("pages/ChatPage.jsx", chat_page)

    print("\n📦 Components created! Now creating layout components...")

    os.chdir(original_dir)


if __name__ == "__main__":
    create_components()