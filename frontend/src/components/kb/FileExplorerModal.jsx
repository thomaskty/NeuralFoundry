import { useState, useEffect } from 'react'
import { X, Upload, Trash2, Loader2, File, FileText, Database, AlertCircle } from 'lucide-react'
import { kbAPI } from '../../services/api'

export default function FileExplorerModal({ kb, onClose, onShowToast }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [deleting, setDeleting] = useState(null)

  useEffect(() => {
    loadDocuments()
  }, [kb.kb_id])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const docs = await kbAPI.listDocuments(kb.kb_id)
      setDocuments(docs)
    } catch (error) {
      console.error('Failed to load documents:', error)
      onShowToast('Failed to load documents', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    try {
      await kbAPI.uploadDocument(kb.kb_id, selectedFile)
      onShowToast(`${selectedFile.name} uploaded successfully!`, 'success')
      setSelectedFile(null)
      setTimeout(loadDocuments, 1000)
    } catch (error) {
      console.error('Failed to upload:', error)
      if (error.response?.status === 409) {
        onShowToast('A file with this name already exists', 'error')
      } else {
        onShowToast('Failed to upload document', 'error')
      }
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (documentId, filename) => {
    if (!confirm(`Delete "${filename}"? This cannot be undone.`)) return

    setDeleting(documentId)
    try {
      await kbAPI.deleteDocument(kb.kb_id, documentId)
      onShowToast(`${filename} deleted successfully`, 'success')
      setDocuments(docs => docs.filter(d => d.id !== documentId))
    } catch (error) {
      console.error('Failed to delete:', error)
      onShowToast('Failed to delete document', 'error')
    } finally {
      setDeleting(null)
    }
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Database className="text-blue-600" size={24} />
            <div>
              <h2 className="text-2xl font-bold text-gray-800">{kb.title}</h2>
              <p className="text-sm text-gray-500">
                {documents.length} {documents.length === 1 ? 'document' : 'documents'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-6 border-b border-gray-200 bg-gray-50">
          <div className="flex gap-3">
            <div className="flex-1">
              <input
                type="file"
                accept=".txt,.md,.pdf"
                onChange={(e) => setSelectedFile(e.target.files[0])}
                disabled={uploading}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100"
              />
            </div>
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium rounded-lg flex items-center gap-2 transition"
            >
              {uploading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload size={18} />
                  Upload
                </>
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Supported formats: .txt, .md, .pdf • Max size: 10MB
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-blue-600" />
            </div>
          ) : documents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500">
              <FileText size={48} className="mb-3 opacity-50" />
              <p className="text-lg font-medium">No documents yet</p>
              <p className="text-sm">Upload a document to get started</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map(doc => (
                <div
                  key={doc.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm transition"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                      <File className="text-blue-600" size={20} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-800 truncate">
                        {doc.filename}
                      </h4>
                      <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                        <span>{formatFileSize(doc.text_size)}</span>
                        <span>•</span>
                        <span>{doc.chunk_count} chunks</span>
                        <span>•</span>
                        <span>{formatDate(doc.created_at)}</span>
                      </div>
                      {doc.mime_type && (
                        <span className="inline-block mt-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                          {doc.mime_type}
                        </span>
                      )}
                    </div>

                    <button
                      onClick={() => handleDelete(doc.id, doc.filename)}
                      disabled={deleting === doc.id}
                      className="flex-shrink-0 p-2 hover:bg-red-50 rounded-lg transition disabled:opacity-50"
                      title="Delete document"
                    >
                      {deleting === doc.id ? (
                        <Loader2 size={18} className="text-red-600 animate-spin" />
                      ) : (
                        <Trash2 size={18} className="text-red-600" />
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {documents.length > 0 && (
          <div className="p-4 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <AlertCircle size={16} />
              <span>
                Total chunks: {documents.reduce((sum, doc) => sum + doc.chunk_count, 0)}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}