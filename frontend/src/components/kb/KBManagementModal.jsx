import { useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Container,
  FormField,
  Input,
  Modal,
  SpaceBetween,
  Table,
  Textarea,
} from '@cloudscape-design/components'

export default function KBManagementModal({
  knowledgeBases,
  onClose,
  onKBCreated,
  onKBDeleted,
  userId,
  onShowToast,
  kbAPI,
}) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)
  const [selectedKB, setSelectedKB] = useState(null)
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)

  const handleCreateKB = async () => {
    if (!title.trim()) return

    setCreating(true)
    try {
      const newKB = await kbAPI.createKB(userId, title.trim(), description.trim())
      onKBCreated(newKB)
      onShowToast(`Knowledge base "${title.trim()}" created successfully`, 'success')
      setTitle('')
      setDescription('')
    } catch (error) {
      console.error('Failed to create KB:', error)
      onShowToast('Failed to create knowledge base', 'error')
    } finally {
      setCreating(false)
    }
  }

  const handleUploadDocument = async () => {
    if (!file || !selectedKB) return

    setUploading(true)
    try {
      await kbAPI.uploadDocument(selectedKB.kb_id, file)
      onShowToast(`${file.name} uploaded successfully`, 'success')
      setFile(null)
    } catch (error) {
      console.error('Failed to upload document:', error)
      onShowToast('Failed to upload document', 'error')
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteKB = async (kbId) => {
    try {
      await kbAPI.deleteKB(kbId)
      onKBDeleted(kbId)
      onShowToast('Knowledge base deleted successfully', 'success')
      if (selectedKB?.kb_id === kbId) setSelectedKB(null)
    } catch (error) {
      console.error('Failed to delete KB:', error)
      onShowToast('Failed to delete knowledge base', 'error')
    }
  }

  return (
    <Modal visible onDismiss={onClose} size="max" header="Knowledge base management" closeAriaLabel="Close modal">
      <SpaceBetween size="l">
        <Container header={<Box variant="h3">Create knowledge base</Box>}>
          <SpaceBetween size="m">
            <FormField label="Title">
              <Input value={title} onChange={({ detail }) => setTitle(detail.value)} />
            </FormField>
            <FormField label="Description">
              <Textarea value={description} onChange={({ detail }) => setDescription(detail.value)} rows={3} />
            </FormField>
            <Button variant="primary" onClick={handleCreateKB} loading={creating} disabled={!title.trim()}>
              Create KB
            </Button>
          </SpaceBetween>
        </Container>

        <Container header={<Box variant="h3">Existing knowledge bases</Box>}>
          <Table
            items={knowledgeBases}
            selectionType="single"
            selectedItems={selectedKB ? [selectedKB] : []}
            onSelectionChange={({ detail }) => setSelectedKB(detail.selectedItems[0] || null)}
            columnDefinitions={[
              { id: 'title', header: 'Title', cell: (item) => item.title },
              { id: 'description', header: 'Description', cell: (item) => item.description || '-' },
              {
                id: 'documents',
                header: 'Documents',
                cell: (item) => item.document_count || 0,
              },
              {
                id: 'actions',
                header: 'Actions',
                cell: (item) => (
                  <Button iconName="remove" variant="icon" onClick={() => handleDeleteKB(item.kb_id)} />
                ),
              },
            ]}
            empty={<Box color="text-body-secondary">No knowledge bases available.</Box>}
          />
        </Container>

        <Container header={<Box variant="h3">Upload document</Box>}>
          {!selectedKB ? (
            <Alert type="info">Select a knowledge base from the table to upload a document.</Alert>
          ) : (
            <SpaceBetween size="m">
              <Box>
                Target KB: <strong>{selectedKB.title}</strong>
              </Box>
              <input type="file" accept=".txt,.md,.pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              <Button variant="primary" onClick={handleUploadDocument} loading={uploading} disabled={!file}>
                Upload document
              </Button>
            </SpaceBetween>
          )}
        </Container>
      </SpaceBetween>
    </Modal>
  )
}
