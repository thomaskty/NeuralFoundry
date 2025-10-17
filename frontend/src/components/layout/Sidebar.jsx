import { Plus, MessageSquare, Trash2, Database } from 'lucide-react'
import { useState } from 'react'
import KBManagementModal from '../kb/KBManagementModal'
import NewChatModal from '../chat/NewChatModal'

export default function Sidebar({
  chats,
  currentChat,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  knowledgeBases,
  onKBCreated,
  onKBDeleted,
  userId,
  onShowToast,  // ADD THIS
  kbAPI         // ADD THIS
}) {
  const [showKBModal, setShowKBModal] = useState(false)
  const [showNewChatModal, setShowNewChatModal] = useState(false)

  const handleCreateChat = async (chatData) => {
    await onNewChat(chatData.title, chatData.system_prompt)
  }

  return (
    <>
      <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col">
        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={() => setShowNewChatModal(true)}
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
                  <MessageSquare size={16} className="text-gray-600 mt-0.5 flex-shrink-0" />
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
                      if (confirm('Delete this chat?')) {
                        onDeleteChat(chat.chat_id)
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition flex-shrink-0"
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

      {/* Modals */}
      <NewChatModal
        isOpen={showNewChatModal}
        onClose={() => setShowNewChatModal(false)}
        onCreateChat={handleCreateChat}
        userId={userId}
      />

      {showKBModal && (
      <KBManagementModal
        knowledgeBases={knowledgeBases}
        onClose={() => setShowKBModal(false)}
        onKBCreated={onKBCreated}
        onKBDeleted={onKBDeleted}
        userId={userId}
        onShowToast={onShowToast}  // ADD THIS
        kbAPI={kbAPI}              // ADD THIS
      />
    )}
    </>
  )
}