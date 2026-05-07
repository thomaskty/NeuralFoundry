import { useEffect, useState } from 'react'
import { Box, Spinner } from '@cloudscape-design/components'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'
import { userAPI } from './services/api'

function App() {
  const [user, setUser] = useState(null)
  const [restoring, setRestoring] = useState(true)

  useEffect(() => {
    const restoreUser = async () => {
      const savedUser = localStorage.getItem('neural_user')

      if (!savedUser) {
        setRestoring(false)
        return
      }

      try {
        const parsed = JSON.parse(savedUser)
        if (!parsed?.username) {
          localStorage.removeItem('neural_user')
          return
        }

        // Re-login by username so the stored identifier stays valid after DB resets.
        const freshUser = await userAPI.login(parsed.username)
        setUser(freshUser)
        localStorage.setItem('neural_user', JSON.stringify(freshUser))
      } catch (error) {
        console.error('Failed to restore user session:', error)
        localStorage.removeItem('neural_user')
      } finally {
        setRestoring(false)
      }
    }

    restoreUser()
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('neural_user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('neural_user')
  }

  if (restoring) {
    return (
      <div className="nf-app-loading">
        <Spinner size="large" />
        <Box color="text-body-secondary">Restoring session...</Box>
      </div>
    )
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />
  }

  return <ChatPage user={user} onLogout={handleLogout} />
}

export default App
