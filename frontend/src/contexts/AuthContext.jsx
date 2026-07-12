import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // Verify token is still valid by checking user info
      // For now, just set user from token
      setUser({ token })
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    try {
      // Try JSON endpoint first
      try {
        const response = await api.post('/auth/login-json', { email, password })
        const { access_token } = response.data
        localStorage.setItem('token', access_token)
        setUser({ email, token: access_token })
        return { success: true }
      } catch (jsonError) {
        // Fallback to form data endpoint
        const formData = new URLSearchParams()
        formData.append('username', email)
        formData.append('password', password)
        
        const response = await api.post('/auth/login', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        })
        
        const { access_token } = response.data
        localStorage.setItem('token', access_token)
        setUser({ email, token: access_token })
        return { success: true }
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  const signup = async (email, password) => {
    try {
      const response = await api.post('/auth/signup', { email, password })
      // After signup, return success (don't auto-login)
      return {
        success: true,
        message: 'Account created successfully! Please login to continue.'
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Signup failed'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

