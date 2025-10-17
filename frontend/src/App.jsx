import { useState, useEffect } from 'react'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'

function App() {
  const [user, setUser] = useState(null)

  // Check if user is logged in
  useEffect(() => {
    const savedUser = localStorage.getItem('neural_user')
    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('neural_user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('neural_user')
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />
  }

  return <ChatPage user={user} onLogout={handleLogout} />
}

export default App