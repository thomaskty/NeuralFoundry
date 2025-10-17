#!/usr/bin/env python3
"""
Layout & Chat Components Generator
Creates Header, Sidebar, MainChatArea, RightPanel and all chat components
Run from project root: python create_layout_components.py
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


def create_layout_components():
    """Generate layout components"""

    print("🚀 Creating layout and chat components...\n")

    original_dir = os.getcwd()

    os.chdir("frontend/src")

    # ============================================================================
    # components/layout/Header.jsx
    # ============================================================================
    header = """import { LogOut, Settings } from 'lucide-react'

export default function Header({ user, onLogout }) {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-lg">N</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-800">
          neural<span className="text-blue-600">::</span>foundry
        </h1>
      </div>

      {/* User Menu */}
      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-sm font-medium text-gray-700">{user.username}</p>
          <p className="text-xs text-gray-500">User ID: {user.id.slice(0, 8)}...</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            className="p-2 hover:bg-gray-100 rounded-lg transition"
            title="Settings"
          >
            <Settings size={20} className="text-gray-600" />
          </button>

          <button
            onClick={onLogout}
            className="p-2 hover:bg-red-50 rounded-lg transition"
            title="Logout"
          >
            <LogOut size={20} className="text-red-600" />
          </button>
        </div>
      </div>
    </header>
  )
}
"""
    create_file("components/layout/Header.jsx", header)

    # ============================================================================
    # components/layout/Sidebar.jsx
    # ============================================================================
    sidebar = """import { Plus, MessageSquare, Trash2, Database } from 'lucide-react'
import { useState } from 'react'
import KBManagementModal from '../kb/KBManagementModal'

export default function Sidebar({ 
  chats, 
  currentChat, 
  onNewChat, 
  onSelectChat, 
  onDeleteChat,
  knowledgeBases,
  onKBCreated,
  onKBDeleted,
  userId
}) {
  const [showKBModal, setShowKBModal] = useState(false)

  return (
    <>
      <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col">
        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={onNewChat}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition"
          >
            <Plus size={20} />
            New Chat
          </button>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto px-4 space-y-2">
          <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Your Chats</p>

          {chats.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No chats yet</p>
          ) : (
            chats.map((chat) => (
              <div
                key={chat.chat_id}
                className={`group relative p-3 rounded-lg cursor-pointer transition ${
                  currentChat?.chat_id === chat.chat_id
                    ? 'bg-blue-100 border border-blue-300'
                    : 'hover:bg-gray-100 border border-transparent'
                }`}
                onClick={() => onSelectChat(chat)}
              >
                <div className="flex items-start gap-2">
                  <MessageSquare size={16} className="text-gray-600 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {chat.title || 'New Chat'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(chat.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteChat(chat.chat_id)
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition"
                  >
                    <Trash2 size={14} className="text-red-600" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* KB Management Button */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={() => setShowKBModal(true)}
            className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition text-sm"
          >
            <Database size={18} />
            Manage Knowledge Bases
          </button>
        </div>
      </div>

      {showKBModal && (
        <KBManagementModal
          knowledgeBases={knowledgeBases}
          onClose={() => setShowKBModal(false)}
          onKBCreated={onKBCreated}
          onKBDeleted={onKBDeleted}
          userId={userId}
        />
      )}
    </>
  )
}
"""
    create_file("components/layout/Sidebar.jsx", sidebar)

    # ============================================================================
    # components/layout/MainChatArea.jsx
    # ============================================================================
    main_chat = """import { useEffect, useRef } from 'react'
import MessageList from '../chat/MessageList'
import ChatInput from '../chat/ChatInput'

export default function MainChatArea({ currentChat, messages, onSendMessage, attachedKBs }) {
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (!currentChat) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">N</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Welcome to neural<span className="text-blue-600">::</span>foundry
          </h2>
          <p className="text-gray-600">Create a new chat to get started</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="border-t border-gray-200 p-4">
        <ChatInput onSendMessage={onSendMessage} attachedKBs={attachedKBs} />
      </div>
    </div>
  )
}
"""
    create_file("components/layout/MainChatArea.jsx", main_chat)

    # ============================================================================
    # components/layout/RightPanel.jsx
    # ============================================================================
    right_panel = """import { ChevronDown } from 'lucide-react'

export default function RightPanel({ 
  knowledgeBases, 
  attachedKBs, 
  onToggleKB,
  selectedModel,
  onModelChange
}) {
  const models = [
    { id: 'mistral-small-latest', name: 'Mistral Small' },
    { id: 'mistral-medium-latest', name: 'Mistral Medium' },
    { id: 'mistral-large-latest', name: 'Mistral Large' }
  ]

  const isKBAttached = (kbId) => {
    return attachedKBs.some(kb => kb.kb_id === kbId)
  }

  return (
    <div className="w-80 bg-gray-50 border-l border-gray-200 flex flex-col">
      {/* LLM Selector */}
      <div className="p-4 border-b border-gray-200">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          LLM Model
        </label>
        <div className="relative">
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            className="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg appearance-none cursor-pointer focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          >
            {models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={20} />
        </div>
      </div>

      {/* Knowledge Base Selector */}
      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">
          Knowledge Bases
        </h3>

        {knowledgeBases.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            No knowledge bases yet
          </p>
        ) : (
          <div className="space-y-2">
            {knowledgeBases.map(kb => {
              const isAttached = isKBAttached(kb.kb_id)

              return (
                <label
                  key={kb.kb_id}
                  className={`block p-3 rounded-lg border-2 cursor-pointer transition ${
                    isAttached
                      ? 'bg-blue-50 border-blue-300'
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={isAttached}
                      onChange={() => onToggleKB(kb.kb_id, isAttached)}
                      className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">
                        {kb.title}
                      </p>
                      {kb.description && (
                        <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                          {kb.description}
                        </p>
                      )}
                    </div>
                  </div>
                </label>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
"""
    create_file("components/layout/RightPanel.jsx", right_panel)

    print("\n📦 Layout components created! Now creating chat components...")

    os.chdir(original_dir)


if __name__ == "__main__":
    create_layout_components()