import { useState } from 'react'
import { X, Plus, Upload, Trash2, Loader2, Database } from 'lucide-react'

export default function KBManagementModal({
  knowledgeBases,
  onClose,
  onKBCreated,
  onKBDeleted,
  userId,
  onShowToast,
  kbAPI
}) {
  const [view, setView] = useState('list')
  const [selectedKB, setSelectedKB] = useState(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)

  const handleCreateKB = async (e) => {
    e.preventDefault()
    if (!title.trim()) return

    setCreating(true)
    try {
      const newKB = await kbAPI.createKB(userId, title.trim(), description.trim())
      onKBCreated(newKB)
      onShowToast(`Knowledge base "${title.trim()}" created successfully!`, 'success')
      setTitle('')
      setDescription('')
      setView('list')
    } catch (error) {
      console.error('Failed to create KB:', error)
      onShowToast('Failed to create knowledge base', 'error')
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
      onShowToast(`${file.name} uploaded successfully!`, 'success')
      setFile(null)
      setView('list')
    } catch (error) {
      console.error('Failed to upload document:', error)
      if (error.response?.status === 409) {
        onShowToast('A file with this name already exists', 'error')
      } else {
        onShowToast('Failed to upload document', 'error')
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
      onShowToast('Knowledge base deleted successfully', 'success')
    } catch (error) {
      console.error('Failed to delete KB:', error)
      onShowToast('Failed to delete knowledge base', 'error')
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] flex flex-col">
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

        <div className="flex-1 overflow-y-auto p-6">
          {view === 'list' && (
            <div className="space-y-4">
              <div className="flex gap-3">
                <button
                  onClick={() => setView('create')}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition"
                >
                  <Plus size={20} />
                  Create New KB
                </button>
              </div>

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
            <div className="space-y-4">
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
                onClick={handleCreateKB}
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
            </div>
          )}

          {view === 'upload' && selectedKB && (
            <div className="space-y-4">
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
                onClick={handleUploadDocument}
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
            </div>
          )}
        </div>
      </div>
    </div>
  )
}