import { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Modal,
  SpaceBetween,
  Table,
} from '@cloudscape-design/components'
import { kbAPI } from '../../services/api'

export default function FileExplorerModal({ kb, onClose, onShowToast }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)

  useEffect(() => {
    loadDocuments()
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      onShowToast(`${selectedFile.name} uploaded successfully`, 'success')
      setSelectedFile(null)
      await loadDocuments()
    } catch (error) {
      console.error('Failed to upload:', error)
      onShowToast('Failed to upload document', 'error')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (documentId, filename) => {
    try {
      await kbAPI.deleteDocument(kb.kb_id, documentId)
      onShowToast(`${filename} deleted successfully`, 'success')
      setDocuments((prev) => prev.filter((d) => d.id !== documentId))
    } catch (error) {
      console.error('Failed to delete:', error)
      onShowToast('Failed to delete document', 'error')
    }
  }

  return (
    <Modal visible onDismiss={onClose} size="max" closeAriaLabel="Close modal" header={`Files in ${kb.title}`}>
      <SpaceBetween size="l">
        <SpaceBetween direction="horizontal" size="s">
          <input type="file" accept=".txt,.md,.pdf" onChange={(e) => setSelectedFile(e.target.files?.[0] || null)} />
          <Button variant="primary" onClick={handleUpload} loading={uploading} disabled={!selectedFile}>
            Upload
          </Button>
        </SpaceBetween>

        {documents.length === 0 && !loading && <Alert type="info">No files uploaded yet.</Alert>}

        <Table
          loading={loading}
          items={documents}
          columnDefinitions={[
            { id: 'filename', header: 'Filename', cell: (item) => item.filename },
            { id: 'chunks', header: 'Chunks', cell: (item) => item.chunk_count || 0 },
            {
              id: 'created',
              header: 'Created',
              cell: (item) => new Date(item.created_at).toLocaleString(),
            },
            {
              id: 'actions',
              header: 'Actions',
              cell: (item) => (
                <Button iconName="remove" variant="icon" onClick={() => handleDelete(item.id, item.filename)} />
              ),
            },
          ]}
          empty={<Box color="text-body-secondary">No documents found.</Box>}
        />
      </SpaceBetween>
    </Modal>
  )
}
