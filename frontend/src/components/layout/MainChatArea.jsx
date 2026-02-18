import { useEffect, useRef } from 'react';
import MessageList from '../chat/MessageList';
import ChatInput from '../chat/ChatInput';
import AttachmentPreview from '../chat/AttachmentPreview';

export default function MainChatArea({
  currentChat,
  messages,
  onSendMessage,
  attachedKBs,
  attachments,
  onAttachFile,
  onRemoveAttachment,
  isUploading
}) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!currentChat) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-white via-slate-50 to-indigo-50/50">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 via-blue-600 to-sky-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-md">
            <span className="text-white font-bold text-2xl">N</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            Welcome to neural<span className="text-indigo-600">::</span>foundry
          </h2>
          <p className="text-slate-600">Create a new chat to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white/80 backdrop-blur">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {/* Attachments Preview */}
      {attachments && attachments.length > 0 && (
        <AttachmentPreview
          attachments={attachments}
          onRemove={onRemoveAttachment}
          isUploading={isUploading}
        />
      )}

      {/* Chat Input */}
      <div className="border-t border-slate-200 p-4 bg-white/80 backdrop-blur">
        <ChatInput
          onSendMessage={onSendMessage}
          attachedKBs={attachedKBs}
          onAttachFile={onAttachFile}
          isUploading={isUploading}
        />
      </div>
    </div>
  );
}
