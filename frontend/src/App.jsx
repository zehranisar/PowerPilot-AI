import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Signup from './pages/Signup'
import VerifyOTP from './pages/VerifyOTP'
import ForgotPassword from './pages/ForgotPassword'
import Dashboard from './pages/Dashboard'
import Predictions from './pages/Predictions'
import Chat from './pages/Chat'
import Layout from './components/Layout'

function PrivateRoute({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" />
}

function PublicRoute({ children }) {
  const { user } = useAuth()
  return !user ? children : <Navigate to="/dashboard" />
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/signup" element={<PublicRoute><Signup /></PublicRoute>} />
          <Route path="/verify-otp" element={<PublicRoute><VerifyOTP /></PublicRoute>} />
          <Route path="/forgot-password" element={<PublicRoute><ForgotPassword /></PublicRoute>} />
          <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="predictions" element={<Predictions />} />
            <Route path="chat" element={<Chat />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

