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
      <div className="w-72 bg-white/70 backdrop-blur border-r border-slate-200 flex flex-col shadow-sm">
        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={() => setShowNewChatModal(true)}
            className="w-full bg-slate-900 hover:bg-slate-800 text-white font-semibold py-3 rounded-xl flex items-center justify-center gap-2 transition shadow-sm"
          >
            <Plus size={20} />
            New Chat
          </button>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto px-4 space-y-2">
          <p className="text-xs font-semibold text-slate-500 uppercase mb-2 tracking-wider">Your Chats</p>

          {chats.length === 0 ? (
            <p className="text-sm text-slate-500 text-center py-4">No chats yet</p>
          ) : (
            chats.map((chat) => (
              <div
                key={chat.chat_id}
                className={`group relative p-3 rounded-xl cursor-pointer transition border ${
                  currentChat?.chat_id === chat.chat_id
                    ? 'bg-indigo-50 border-indigo-200 shadow-sm'
                    : 'hover:bg-slate-50 border-transparent'
                }`}
                onClick={() => onSelectChat(chat)}
              >
                <div className="flex items-start gap-2">
                  <MessageSquare size={16} className="text-slate-500 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-800 truncate">
                      {chat.title || 'New Chat'}
                    </p>
                    <p className="text-xs text-slate-500">
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
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-rose-100 rounded transition flex-shrink-0"
                  >
                    <Trash2 size={14} className="text-rose-600" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* KB Management Button */}
        <div className="p-4 border-t border-slate-200">
          <button
            onClick={() => setShowKBModal(true)}
            className="w-full bg-white border border-slate-200 hover:border-slate-300 text-slate-700 font-semibold py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 transition text-sm shadow-sm"
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
