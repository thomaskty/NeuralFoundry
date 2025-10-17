#!/usr/bin/env python3
"""
Chat & KB Components Generator
Creates MessageList, MessageBubble, ChatInput, and KB Management components
Run from project root: python create_chat_kb_components.py
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


def create_chat_kb_components():
    """Generate chat and KB components"""

    print("🚀 Creating chat and KB components...\n")

    original_dir = os.getcwd()

    os.chdir("frontend/src")

    # ============================================================================
    # components/chat/MessageList.jsx
    # ============================================================================
    message_list = """import MessageBubble from './MessageBubble'

export default function MessageList({ messages }) {
  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">Start a conversation...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </div>
  )
}
"""
    create_file("components/chat/MessageList.jsx", message_list)

    # ============================================================================
    # components/chat/MessageBubble.jsx
    # ============================================================================
    message_bubble = r"""import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { User, Bot, Copy, Check } from 'lucide-react'
import { useState } from 'react'

export default function MessageBubble({ message }) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-blue-600' : 'bg-gradient-to-br from-purple-500 to-pink-500'
      }`}>
        {isUser ? (
          <User size={18} className="text-white" />
        ) : (
          <Bot size={18} className="text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div className={`group relative rounded-2xl px-4 py-3 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-gray-100 text-gray-800 border border-gray-200'
        }`}>
          {/* Copy Button */}
          {!isUser && (
            <button
              onClick={handleCopy}
              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1.5 bg-white rounded-lg shadow-sm hover:bg-gray-50 transition"
              title="Copy message"
            >
              {copied ? (
                <Check size={14} className="text-green-600" />
              ) : (
                <Copy size={14} className="text-gray-600" />
              )}
            </button>
          )}

          {/* Message Text */}
          <div className={`prose prose-sm max-w-none ${isUser ? 'prose-invert' : ''}`}>
            <ReactMarkdown
              components={{
                code({node, inline, className, children, ...props}) {
                  const match = /language-(\w+)/.exec(className || '')
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  )
                }
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </div>

        {/* Timestamp */}
        <span className="text-xs text-gray-500 mt-1 px-2">
          {new Date(message.created_at).toLocaleTimeString()}
        </span>
      </div>
    </div>
  )
}
"""
    create_file("components/chat/MessageBubble.jsx", message_bubble)

    # ============================================================================
    # components/chat/ChatInput.jsx
    # ============================================================================
    chat_input = """import { useState } from 'react'
import { Send, Paperclip, Loader2 } from 'lucide-react'

export default function ChatInput({ onSendMessage, attachedKBs }) {
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!message.trim() || sending) return

    setSending(true)
    setMessage('')

    try {
      await onSendMessage(message.trim())
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      {/* Attached KBs Info */}
      {attachedKBs.length > 0 && (
        <div className="flex items-center gap-2 text-xs text-gray-600 px-2">
          <Paperclip size={14} />
          <span>Using {attachedKBs.length} knowledge base{attachedKBs.length > 1 ? 's' : ''}</span>
        </div>
      )}

      {/* Input Area */}
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Shift+Enter for new line)"
            rows={1}
            disabled={sending}
            className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
            style={{ minHeight: '48px', maxHeight: '200px' }}
          />
        </div>

        <button
          type="submit"
          disabled={!message.trim() || sending}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl transition flex items-center gap-2 font-medium"
        >
          {sending ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              Sending...
            </>
          ) : (
            <>
              <Send size={20} />
              Send
            </>
          )}
        </button>
      </div>
    </form>
  )
}
"""
    create_file("components/chat/ChatInput.jsx", chat_input)

    # ============================================================================
    # components/kb/KBManagementModal.jsx
    # ============================================================================
    kb_modal = """import { useState } from 'react'
import { X, Plus, Upload, Trash2, Loader2, Database } from 'lucide-react'
import { kbAPI } from '../../services/api'

export default function KBManagementModal({ 
  knowledgeBases, 
  onClose, 
  onKBCreated, 
  onKBDeleted,
  userId 
}) {
  const [view, setView] = useState('list') // 'list' | 'create' | 'upload'
  const [selectedKB, setSelectedKB] = useState(null)

  // Create KB state
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)

  // Upload state
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)

  const handleCreateKB = async (e) => {
    e.preventDefault()

    if (!title.trim()) return

    setCreating(true)
    try {
      const newKB = await kbAPI.createKB(userId, title.trim(), description.trim())
      onKBCreated(newKB)
      setTitle('')
      setDescription('')
      setView('list')
    } catch (error) {
      console.error('Failed to create KB:', error)
      alert('Failed to create knowledge base')
    } finally {
      setCreating(false)
    }
  }

  const handleUploadDocument = async (e) => {
    e.preventDefault()

    if (!file || !selectedKB) return

    setUploading(true)
    try {
      await kbAPI.uploadDocument(selectedKB.kb_id, file)
      setFile(null)
      setView('list')
      alert('Document uploaded successfully! Processing in background...')
    } catch (error) {
      console.error('Failed to upload document:', error)
      if (error.response?.status === 409) {
        alert('A file with this name already exists in this knowledge base')
      } else {
        alert('Failed to upload document')
      }
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteKB = async (kbId) => {
    if (!confirm('Are you sure you want to delete this knowledge base?')) return

    try {
      await kbAPI.deleteKB(kbId)
      onKBDeleted(kbId)
    } catch (error) {
      console.error('Failed to delete KB:', error)
      alert('Failed to delete knowledge base')
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Database className="text-blue-600" size={24} />
            <h2 className="text-2xl font-bold text-gray-800">
              Knowledge Base Management
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {view === 'list' && (
            <div className="space-y-4">
              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => setView('create')}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition"
                >
                  <Plus size={20} />
                  Create New KB
                </button>
              </div>

              {/* KB List */}
              <div className="space-y-3">
                <h3 className="font-semibold text-gray-700">Your Knowledge Bases</h3>

                {knowledgeBases.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">
                    No knowledge bases yet. Create one to get started!
                  </p>
                ) : (
                  knowledgeBases.map(kb => (
                    <div
                      key={kb.kb_id}
                      className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-800">{kb.title}</h4>
                          {kb.description && (
                            <p className="text-sm text-gray-600 mt-1">{kb.description}</p>
                          )}
                          <p className="text-xs text-gray-500 mt-2">
                            Created {new Date(kb.created_at).toLocaleDateString()}
                          </p>
                        </div>

                        <div className="flex gap-2">
                          <button
                            onClick={() => {
                              setSelectedKB(kb)
                              setView('upload')
                            }}
                            className="p-2 hover:bg-blue-50 rounded-lg transition"
                            title="Upload document"
                          >
                            <Upload size={18} className="text-blue-600" />
                          </button>

                          <button
                            onClick={() => handleDeleteKB(kb.kb_id)}
                            className="p-2 hover:bg-red-50 rounded-lg transition"
                            title="Delete KB"
                          >
                            <Trash2 size={18} className="text-red-600" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {view === 'create' && (
            <form onSubmit={handleCreateKB} className="space-y-4">
              <button
                type="button"
                onClick={() => setView('list')}
                className="text-sm text-gray-600 hover:text-gray-800 flex items-center gap-1"
              >
                ← Back to list
              </button>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Knowledge Base Title *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Technical Documentation"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief description of what this KB contains..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={creating || !title.trim()}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition"
              >
                {creating ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus size={20} />
                    Create Knowledge Base
                  </>
                )}
              </button>
            </form>
          )}

          {view === 'upload' && selectedKB && (
            <form onSubmit={handleUploadDocument} className="space-y-4">
              <button
                type="button"
                onClick={() => {
                  setView('list')
                  setFile(null)
                }}
                className="text-sm text-gray-600 hover:text-gray-800 flex items-center gap-1"
              >
                ← Back to list
              </button>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="font-medium text-gray-800">Uploading to:</p>
                <p className="text-sm text-gray-600">{selectedKB.title}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Document *
                </label>
                <input
                  type="file"
                  accept=".txt,.md,.pdf"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  required
                />
                <p className="text-xs text-gray-500 mt-2">
                  Supported formats: .txt, .md, .pdf
                </p>
              </div>

              {file && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Selected:</span> {file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    Size: {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={uploading || !file}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition"
              >
                {uploading ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload size={20} />
                    Upload Document
                  </>
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
"""
    create_file("components/kb/KBManagementModal.jsx", kb_modal)

    print("\n" + "=" * 70)
    print("✅ ALL COMPONENTS CREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📦 Frontend structure is complete!")
    print("\n📋 Final steps:")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm run dev")
    print("\n🎉 Your app will be ready at: http://localhost:3000")

    os.chdir(original_dir)


if __name__ == "__main__":
    create_chat_kb_components()