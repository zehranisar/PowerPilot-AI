import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import api from '../services/api'
import { Zap, Mail, AlertCircle, CheckCircle, X, Loader2, ArrowLeft } from 'lucide-react'

export default function VerifyOTP() {
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const [resending, setResending] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const navigate = useNavigate()
  const location = useLocation()
  
  const email = location.state?.email
  const password = location.state?.password

  useEffect(() => {
    if (!email || !password) {
      navigate('/signup')
    }
  }, [email, password, navigate])

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [countdown])

  const handleOtpChange = (index, value) => {
    if (value.length > 1) return // Only allow single digit
    
    const newOtp = [...otp]
    newOtp[index] = value.replace(/[^0-9]/g, '') // Only numbers
    
    setOtp(newOtp)
    setError('')
    
    // Auto-focus next input
    if (value && index < 5) {
      const nextInput = document.getElementById(`otp-${index + 1}`)
      if (nextInput) nextInput.focus()
    }
  }

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      const prevInput = document.getElementById(`otp-${index - 1}`)
      if (prevInput) prevInput.focus()
    }
  }

  const handlePaste = (e) => {
    e.preventDefault()
    const pastedData = e.clipboardData.getData('text').replace(/[^0-9]/g, '').slice(0, 6)
    if (pastedData.length === 6) {
      const newOtp = pastedData.split('')
      setOtp(newOtp)
      // Focus last input
      const lastInput = document.getElementById(`otp-5`)
      if (lastInput) lastInput.focus()
    }
  }

  const handleVerify = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    
    const otpCode = otp.join('').trim()
    
    if (otpCode.length !== 6) {
      setError('Please enter the complete 6-digit code')
      return
    }
    
    // Validate it's all digits
    if (!/^\d{6}$/.test(otpCode)) {
      setError('Please enter a valid 6-digit code')
      return
    }
    
    setLoading(true)
    try {
      // Ensure OTP is sent as a clean string with no whitespace
      const cleanOtp = otpCode.replace(/\s/g, '')
      console.log('[Frontend] Sending OTP verification:', { email: email.trim().toLowerCase(), otp_code: cleanOtp, length: cleanOtp.length })
      
      const response = await api.post('/auth/signup/verify-otp', {
        email: email.trim().toLowerCase(),
        otp_code: cleanOtp
      })
      
      // Save token
      localStorage.setItem('token', response.data.access_token)
      
      setSuccess('Email verified successfully! Creating your account...')
      
      // Redirect to dashboard after short delay
      setTimeout(() => {
        window.location.href = '/dashboard'
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid verification code. Please try again.')
      // Clear OTP on error
      setOtp(['', '', '', '', '', ''])
      document.getElementById('otp-0')?.focus()
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (countdown > 0) return
    
    setResending(true)
    setError('')
    try {
      await api.post('/auth/signup/request-otp', {
        email: email,
        password: password
      })
      setSuccess('New verification code sent to your email!')
      setCountdown(60) // 60 second cooldown
      setOtp(['', '', '', '', '', ''])
      document.getElementById('otp-0')?.focus()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to resend code. Please try again.')
    } finally {
      setResending(false)
    }
  }

  if (!email || !password) {
    return null
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Logo */}
          <div className="flex items-center justify-center gap-2 mb-8">
            <Zap className="w-10 h-10 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Energy Forecast</h1>
          </div>

          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Verify Your Email</h2>
          <p className="text-gray-600 mb-2">
            We've sent a 6-digit verification code to
          </p>
          <p className="text-gray-900 font-medium mb-8">{email}</p>

          {success && (
            <div className="mb-6 p-4 bg-green-50 border-2 border-green-200 rounded-lg shadow-sm">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-green-800 mb-1">Success!</h3>
                  <p className="text-sm text-green-700">{success}</p>
                </div>
                <button
                  onClick={() => setSuccess('')}
                  className="flex-shrink-0 text-green-600 hover:text-green-800"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-2 border-red-200 rounded-lg shadow-sm">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <AlertCircle className="w-5 h-5 text-red-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-red-800 mb-1">Error</h3>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
                <button
                  onClick={() => setError('')}
                  className="flex-shrink-0 text-red-600 hover:text-red-800"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          <form onSubmit={handleVerify} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3 text-center">
                Enter Verification Code
              </label>
              <div className="flex justify-center gap-2">
                {otp.map((digit, index) => (
                  <input
                    key={index}
                    id={`otp-${index}`}
                    type="text"
                    inputMode="numeric"
                    maxLength="1"
                    value={digit}
                    onChange={(e) => handleOtpChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(index, e)}
                    onPaste={index === 0 ? handlePaste : undefined}
                    className="w-12 h-14 text-center text-2xl font-bold border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors"
                    disabled={loading}
                    autoFocus={index === 0}
                  />
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || otp.join('').length !== 6}
              className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Verifying...
                </>
              ) : (
                'Verify Email'
              )}
            </button>
          </form>

          <div className="mt-6 text-center space-y-3">
            <p className="text-sm text-gray-600">
              Didn't receive the code?
            </p>
            <button
              onClick={handleResend}
              disabled={resending || countdown > 0}
              className="text-primary-600 hover:text-primary-700 font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {resending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin inline mr-1" />
                  Sending...
                </>
              ) : countdown > 0 ? (
                `Resend code in ${countdown}s`
              ) : (
                'Resend Verification Code'
              )}
            </button>
          </div>

          <button
            onClick={() => navigate('/signup')}
            className="mt-6 w-full flex items-center justify-center gap-2 text-gray-600 hover:text-gray-800 font-medium text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Signup
          </button>
        </div>
      </div>
    </div>
  )
}

