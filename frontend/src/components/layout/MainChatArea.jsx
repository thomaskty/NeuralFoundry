import { useEffect, useRef } from 'react'
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
