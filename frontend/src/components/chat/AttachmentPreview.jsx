import { X, FileText, Loader2 } from 'lucide-react';

export default function AttachmentPreview({ attachments, onRemove, isUploading }) {
  if (!attachments || attachments.length === 0) return null;

  const getFileIcon = (mimeType) => {
    if (mimeType?.includes('pdf')) return '📄';
    if (mimeType?.includes('image')) return '🖼️';
    if (mimeType?.includes('text')) return '📝';
    if (mimeType?.includes('word')) return '📘';
    return '📎';
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="border-t border-slate-200 bg-white/70 backdrop-blur p-3">
      <div className="text-xs text-slate-600 mb-2 font-semibold">
        📎 Attached Files ({attachments.length})
      </div>
      <div className="space-y-2">
        {attachments.map((att) => (
          <div
            key={att.id}
            className="flex items-center justify-between bg-white rounded-xl p-2 border border-slate-200 shadow-sm"
          >
            <div className="flex items-center space-x-2 flex-1 min-w-0">
              <span className="text-xl">{getFileIcon(att.mime_type)}</span>

              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-slate-800 truncate">
                  {att.filename}
                </div>
                <div className="text-xs text-slate-500 flex items-center space-x-2">
                  <span>{formatFileSize(att.file_size)}</span>
                  {att.processing_status === 'processing' && (
                    <>
                      <span>•</span>
                      <span className="text-indigo-600 flex items-center">
                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                        Processing...
                      </span>
                    </>
                  )}
                  {att.processing_status === 'completed' && (
                    <>
                      <span>•</span>
                      <span className="text-emerald-600">✓ Ready</span>
                    </>
                  )}
                  {att.processing_status === 'failed' && (
                    <>
                      <span>•</span>
                      <span className="text-rose-600">✗ Failed</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={() => onRemove(att.id)}
              disabled={isUploading}
              className="ml-2 p-1 hover:bg-rose-50 rounded transition-colors disabled:opacity-50"
              title="Remove"
            >
              <X className="w-4 h-4 text-rose-500" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
