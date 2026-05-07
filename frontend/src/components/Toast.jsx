import Flashbar from '@cloudscape-design/components/flashbar'

export default function Toast() {
  return null
}

export function ToastContainer({ toasts, removeToast }) {
  const items = toasts.map((toast) => ({
    id: String(toast.id),
    type: toast.type === 'error' ? 'error' : toast.type === 'success' ? 'success' : 'info',
    content: toast.message,
    dismissible: true,
    onDismiss: () => removeToast(toast.id),
  }))

  if (items.length === 0) return null

  return <Flashbar stackItems items={items} />
}
