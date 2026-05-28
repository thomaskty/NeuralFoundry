import { useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Container,
  Form,
  FormField,
  Header,
  Input,
  SpaceBetween,
} from '@cloudscape-design/components'
import LogoMark from '../components/branding/LogoMark'
import { userAPI } from '../services/api'

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!username.trim()) {
      setError('Please enter a username')
      return
    }

    setLoading(true)

    try {
      const userData = await userAPI.login(username.trim())
      onLogin(userData)
    } catch (err) {
      if (err.response?.status === 404) {
        setError('User not found. Please check your username or contact administrator.')
      } else {
        setError('Failed to login. Please try again.')
      }
      console.error('Login error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="nf-login-root">
      <Container
        header={
          <div className="nf-login-header">
            <LogoMark size={56} withWordmark subtitle="Workflow design and copilot workspace" />
            <Header variant="h1" description="Create workflows for business processes and use the same workspace for general copilot tasks.">
              Sign in
            </Header>
          </div>
        }
      >
        <form onSubmit={handleSubmit}>
          <Form
            actions={
              <Button variant="primary" formAction="submit" loading={loading}>
                Continue
              </Button>
            }
          >
            <SpaceBetween size="l">
              {error && <Alert type="error">{error}</Alert>}

              <FormField label="Username" description="Use an existing username or self-register on first login.">
                <Input
                  value={username}
                  onChange={({ detail }) => setUsername(detail.value)}
                  placeholder="Enter your username"
                  autoFocus
                  disabled={loading}
                />
              </FormField>

              <Box color="text-body-secondary" fontSize="body-s">
                By continuing, you agree to your organization usage policies.
              </Box>
            </SpaceBetween>
          </Form>
        </form>
      </Container>
    </div>
  )
}
