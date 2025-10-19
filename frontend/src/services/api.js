import axios from 'axios'

const API_BASE = '/api/v1'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ============================================================================
// User APIs
// ============================================================================
export const userAPI = {
  login: async (username) => {
    const response = await api.post('/users/login', null, {
      params: { username }
    })
    return response.data
  },

  create: async (username) => {
    const response = await api.post('/users', { username })
    return response.data
  }
}

// ============================================================================
// Chat APIs
// ============================================================================
export const chatAPI = {
  getUserChats: async (userId) => {
    const response = await api.get(`/users/${userId}/chats`)
    return response.data
  },

  createChat: async (userId, title, systemPrompt = null) => {
    const response = await api.post(`/users/${userId}/chats`, {
      title: title || 'New Chat',
      system_prompt: systemPrompt
    })
    return response.data
  },

  getChat: async (chatId) => {
    const response = await api.get(`/chats/${chatId}`)
    return response.data
  },

  deleteChat: async (chatId) => {
    const response = await api.delete(`/chats/${chatId}`)
    return response.data
  },

  sendMessage: async (chatId, content) => {
    const response = await api.post(`/chats/${chatId}/messages`, {
      role: 'user',
      content
    })
    return response.data
  }
}

// ============================================================================
// Knowledge Base APIs
// ============================================================================
export const kbAPI = {
  getUserKBs: async (userId) => {
    const response = await api.get(`/users/${userId}/knowledge-bases`)
    return response.data
  },

  createKB: async (userId, title, description) => {
    const response = await api.post(`/users/${userId}/knowledge-bases`, {
      title,
      description
    })
    return response.data
  },

  uploadDocument: async (kbId, file) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(
      `/knowledge-bases/${kbId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data
  },

  listDocuments: async (kbId) => {
    const response = await api.get(`/knowledge-bases/${kbId}/documents`)
    return response.data
  },

  deleteDocument: async (kbId, documentId) => {
    const response = await api.delete(`/knowledge-bases/${kbId}/documents/${documentId}`)
    return response.data
  },

  deleteKB: async (kbId) => {
    const response = await api.delete(`/knowledge-bases/${kbId}`)
    return response.data
  },

  // Chat-KB Integration
  getAttachedKBs: async (chatId) => {
    const response = await api.get(`/chats/${chatId}/knowledge-bases`)
    return response.data
  },

  attachKB: async (chatId, kbId) => {
    const response = await api.post(`/chats/${chatId}/knowledge-bases/${kbId}`)
    return response.data
  },

  detachKB: async (chatId, kbId) => {
    const response = await api.delete(`/chats/${chatId}/knowledge-bases/${kbId}`)
    return response.data
  }
}

export default api