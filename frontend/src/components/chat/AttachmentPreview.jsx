import { Box, Button, SpaceBetween } from '@cloudscape-design/components'

function formatFileSize(bytes) {
  if (!bytes) return 'Unknown'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function AttachmentPreview({ attachments, onRemove, isUploading }) {
  if (!attachments || attachments.length === 0) return null

  return (
    <Box padding="m" borderTop="divider">
      <SpaceBetween size="xs">
        <Box variant="h3">Attachments ({attachments.length})</Box>
        {attachments.map((att) => (
          <div key={att.id} className="nf-attachment-row">
            <div>
              <Box fontWeight="bold">{att.filename}</Box>
              <Box color="text-body-secondary" fontSize="body-s">
                {formatFileSize(att.file_size)}
              </Box>
            </div>
            <div className="nf-attachment-actions">
              <Button iconName="remove" variant="icon" onClick={() => onRemove(att.id)} disabled={isUploading} />
            </div>
          </div>
        ))}
      </SpaceBetween>
    </Box>
  )
}
